from fastapi import FastAPI
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
import os
import re
from dotenv import load_dotenv

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq

# Load ENV
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    print("Warning: GROQ_API_KEY is not set. LLM calls will fail until it is configured.")

# FastAPI setup
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Load embeddings + FAISS

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

try:
    vector_db = FAISS.load_local(
        "recipe_faiss_index",
        embeddings,
        allow_dangerous_deserialization=True
    )
except Exception as exc:
    vector_db = None
    print(f"Error loading FAISS index: {exc}")

# Load LLM
try:
    llm = ChatGroq(
        model_name="llama-3.1-8b-instant",
        temperature=0,
        groq_api_key=groq_api_key
    )
except Exception as exc:
    llm = None
    print(f"Error initializing Groq client: {exc}")

# Request model
class RecipeContext(BaseModel):
    recipe_name: str | None = None
    ingredients: list[str] = Field(default_factory=list)
    missing_ingredients: list[str] = Field(default_factory=list)
    last_user_query: str | None = None
    last_answer: str | None = None


class QueryRequest(BaseModel):
    query: str
    context: RecipeContext | None = None


# UTIL FUNCTIONS
def extract_ingredients(text):
    match = re.search(r"Ingredients:(.*?)(Instructions:|Directions:|$)", text, re.S)
    if match:
        return [i.strip().lower() for i in re.split(r",|\n", match.group(1)) if i.strip()]
    return []

def clean_input(query):
    return [i.strip().lower() for i in query.split(",")]

def get_missing(user, recipe):
    return [r for r in recipe if not any(u in r or r in u for u in user)]

def is_dish_query(query):
    keywords = ["how to make", "recipe for", "prepare", "procedure"]
    return any(k in query.lower() for k in keywords)

def extract_dish(query):
    q = query.lower()
    for k in ["how to make", "recipe for", "prepare", "procedure"]:
        if k in q:
            return q.replace(k, "").strip()
    return q


def extract_recipe_name(recipe_text):
    for line in recipe_text.splitlines():
        cleaned = line.strip()
        if not cleaned:
            continue
        lowered = cleaned.lower()
        if lowered.startswith("ingredients") or lowered.startswith("steps"):
            continue
        if lowered.startswith("missing ingredients"):
            continue
        return re.sub(r"^(recipe name:|title:)\s*", "", cleaned, flags=re.I).strip()
    return "Suggested Recipe"


def looks_like_follow_up(query, context):
    if not context:
        return False

    normalized = query.strip().lower()
    if not normalized:
        return False

    follow_up_markers = [
        "this",
        "that",
        "it",
        "these",
        "those",
        "same",
        "instead",
        "replace",
        "substitute",
        "add",
        "remove",
        "change",
        "modify",
        "adjust",
        "swap",
        "without",
        "with",
        "more",
        "less",
        "what if",
        "can we",
        "can i",
    ]

    return any(marker in normalized for marker in follow_up_markers)


def build_follow_up_prompt(query, context):
    ingredients = ", ".join(context.ingredients) if context.ingredients else "Not available"
    missing = ", ".join(context.missing_ingredients) if context.missing_ingredients else "None"
    previous_answer = context.last_answer or "Not available"
    recipe_name = context.recipe_name or "the previous recipe"

    return f"""
        You are a professional chef assistant.
        The user is asking a follow-up question about a previously discussed recipe.
        Previous recipe name: {recipe_name}
        Previous ingredients: {ingredients}
        Previous missing ingredients: {missing}
        Previous assistant answer: {previous_answer}
        User follow-up question: {query}
        Rules:
        - Answer using the previous recipe context.
        - If the user wants to add, replace, remove, or adjust ingredients, explain the effect clearly.
        - If the request is ambiguous, ask a short clarifying question.
        - Do not invent a completely new recipe unless the user explicitly asks for one.
        Return a concise helpful answer.
        """

@app.post("/chat")
def chat(req: QueryRequest):
    try:
        if vector_db is None:
            return {"answer": "Recipe search is unavailable because the FAISS index could not be loaded."}

        if llm is None:
            return {"answer": "Recipe generation is unavailable because the LLM client could not be initialized."}

        query_raw = req.query.strip()
        query = query_raw.lower()

        if looks_like_follow_up(query_raw, req.context):
            prompt = build_follow_up_prompt(query_raw, req.context)
            res = llm.invoke(prompt)
            return {
                "answer": res.content,
                "mode": "follow_up",
                "context": req.context.model_dump() if req.context else None,
            }

        
        #   OUT OF DOMAIN CHECK
      
        docs_scores = vector_db.similarity_search_with_score(query, k=1)

        threshold = 1.5  # tune if needed

        if not docs_scores or docs_scores[0][1] > threshold:
            return {
                "answer": "Out of domain. I can only answer recipe-related queries. Please ask about food or cooking."
            }

        #  DISH QUERY
        if is_dish_query(query):
            dish = extract_dish(query)
            docs = vector_db.similarity_search(dish, k=1)

            if not docs:
                return {"answer": "Recipe not found"}

            recipe_text = docs[0].page_content

            prompt = f"""
                You are a professional chef.Use ONLY the recipe below.
                Recipe:
                {recipe_text}
                Give:
                Recipe Name, Ingredients (bullet points), Steps (numbered clearly)
                DO NOT include missing ingredients.
                FORMAT:
                Recipe Name:
                ...
                Ingredients:
                item1, item2
                Steps:(Each step should be explained clearly in detail)
                1. ...
                2. ...
                """
            res = llm.invoke(prompt)
            return {
                "answer": res.content,
                "mode": "recipe",
                "context": {
                    "recipe_name": extract_recipe_name(recipe_text),
                    "ingredients": recipe_text and extract_ingredients(recipe_text) or [],
                    "missing_ingredients": [],
                    "last_user_query": query_raw,
                    "last_answer": res.content,
                },
            }
        
        #  INGREDIENT QUERY
        user = clean_input(query)

        docs_scores = vector_db.similarity_search_with_score(query, k=3)
        docs = [doc for doc, score in docs_scores]

        best_doc = None
        best_score = -1

        for doc in docs:
            recipe_text = doc.page_content
            recipe_ing = extract_ingredients(recipe_text)

            overlap = sum(
                1 for r in recipe_ing
                if any(u in r or r in u for u in user)
            )

            if overlap > best_score:
                best_score = overlap
                best_doc = doc

        if not best_doc:
            return {"answer":"No suitable recipe found."}

        recipe_text = best_doc.page_content
        recipe_ing = extract_ingredients(recipe_text)

        missing = get_missing(user, recipe_ing)
        missing_text = "None" if not missing else ", ".join(missing)

        prompt = f"""
            You are a professional chef assistant. Use ONLY the given recipe.
            Recipe:
            {recipe_text}
            User Ingredients:
            {query}
            Give: Recipe Name, Ingredients, Steps
            Missing Ingredients: {missing_text}
            FORMAT:
            Recipe Name:
            ...
            Ingredients:
            item1
            item2
            Steps:(Each step should be explained clearly in detail)
            1. ...
            2. ...
            Missing Ingredients:
            {missing_text}
            """

        res = llm.invoke(prompt)
        return {
            "answer": res.content,
            "mode": "recipe",
            "context": {
                "recipe_name": extract_recipe_name(recipe_text),
                "ingredients": recipe_ing,
                "missing_ingredients": missing,
                "last_user_query": query_raw,
                "last_answer": res.content,
            },
        }
    except Exception as exc:
        return {"answer": f"Unexpected server error while processing the recipe request: {exc}"}
