from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
import re
from dotenv import load_dotenv

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq

# -----------------------------
# Load ENV
# -----------------------------
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

# -----------------------------
# FastAPI setup
# -----------------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Load embeddings + FAISS
# -----------------------------
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vector_db = FAISS.load_local(
    "recipe_faiss_index",
    embeddings,
    allow_dangerous_deserialization=True
)

# -----------------------------
# Load LLM
# -----------------------------
llm = ChatGroq(
    model_name="llama-3.1-8b-instant",
    temperature=0,
    groq_api_key=groq_api_key
)

# -----------------------------
# Request model
# -----------------------------
class QueryRequest(BaseModel):
    query: str


# -----------------------------
# UTIL FUNCTIONS
# -----------------------------
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

@app.post("/chat")
def chat(req: QueryRequest):

    query = req.query.strip().lower()

    # -----------------------------
<<<<<<< HEAD
    #  OUT OF DOMAIN CHECK
=======
    #   OUT OF DOMAIN CHECK
>>>>>>> 4127deab7e89e74a9fe9e26b36fdec031df309e9
    # -----------------------------
    docs_scores = vector_db.similarity_search_with_score(query, k=1)

    threshold = 1.5  # tune if needed

    if not docs_scores or docs_scores[0][1] > threshold:
        return {
            "answer": "Out of domain. I can only answer recipe-related queries. Please ask about food or cooking."
        }

    # ============================
    #  DISH QUERY
    # ============================
    if is_dish_query(query):

        dish = extract_dish(query)
        docs = vector_db.similarity_search(dish, k=1)

        if not docs:
            return {"answer": "Recipe not found"}

        recipe_text = docs[0].page_content

        prompt = f"""
            You are a professional chef.

            Use ONLY the recipe below.

            Recipe:
            {recipe_text}

            Give:
            - Recipe Name
            - Ingredients (bullet points)
            - Steps (numbered clearly)

            DO NOT include missing ingredients.

            FORMAT:

            Recipe Name:
            ...

            Ingredients:
            - item1
            - item2

            Steps:(Each step should be explained clearly in detail)
            1. ...
            2. ...
            """

        res = llm.invoke(prompt)
        return {"answer": res.content}

    # ============================
    #  INGREDIENT QUERY
    # ============================
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
        return {"answer": "No suitable recipe found."}

    recipe_text = best_doc.page_content
    recipe_ing = extract_ingredients(recipe_text)

    missing = get_missing(user, recipe_ing)
    missing_text = "None" if not missing else ", ".join(missing)

    prompt = f"""
        You are a professional chef assistant.

        Use ONLY the given recipe.

        Recipe:
        {recipe_text}

        User Ingredients:
        {query}

        Give:
        - Recipe Name
        - Ingredients
        - Steps
        - Missing Ingredients: {missing_text}

        FORMAT:

        Recipe Name:
        ...

        Ingredients:
        - item1
        - item2

        Steps:(Each step should be explained clearly in detail)
        1. ...
        2. ...

        Missing Ingredients:
        {missing_text}
        """

    res = llm.invoke(prompt)

    return {"answer": res.content}

    # ============================
    #  INGREDIENT QUERY
    # ============================
    user = clean_input(query)
    docs = vector_db.similarity_search(query, k=3)

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
        return {"answer": "No suitable recipe found."}

    recipe_text = best_doc.page_content
    recipe_ing = extract_ingredients(recipe_text)

    missing = get_missing(user, recipe_ing)
    missing_text = "None" if not missing else ", ".join(missing)

    prompt = f"""
            You are a professional chef assistant.
            If the prompt query is out of domain say out of domain question.Dont do assumption for it by giving the wrong information.

            Recipe:
            {recipe_text}

            User Ingredients:
            {query}

            Give:
            - Recipe Name
            - Ingredients
            - Steps
            - Missing Ingredients: {missing_text}

            FORMAT:

            Recipe Name:
            ...

            Ingredients:
            - item1
            - item2

            Steps:(Each step should be explained clearly in detail)
            1. ...
            2. ...

            Missing Ingredients:
            {missing_text}
            """

    res = llm.invoke(prompt)

<<<<<<< HEAD
    return {"answer": res.content}
=======
    return {"answer": res.content}
>>>>>>> 4127deab7e89e74a9fe9e26b36fdec031df309e9
