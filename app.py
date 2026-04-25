# import streamlit as st
# import os
# from dotenv import load_dotenv

# from langchain_community.vectorstores import FAISS
# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_groq import ChatGroq

# # -----------------------------
# # Load environment variables
# # -----------------------------
# load_dotenv()
# groq_api_key = os.getenv("GROQ_API_KEY")

# # -----------------------------
# # Load embeddings
# # -----------------------------
# embeddings = HuggingFaceEmbeddings(
#     model_name="sentence-transformers/all-MiniLM-L6-v2"
# )

# # -----------------------------
# # Load FAISS index
# # -----------------------------
# vector_db = FAISS.load_local(
#     "recipe_faiss_index",
#     embeddings,
#     allow_dangerous_deserialization=True
# )
# # -----------------------------
# # Load Groq LLM
# # -----------------------------
# llm = ChatGroq(
#     model_name="llama-3.1-8b-instant",
#     temperature=0,
#     groq_api_key=groq_api_key
# )
# # -----------------------------
# # Streamlit UI
# # -----------------------------
# st.set_page_config(page_title="Recipe Generator", page_icon="🍳")

# st.title("AI Recipe Generator (RAG + Groq)")
# st.write("Enter ingredients and get a recipe instantly!")

# query = st.text_input("Enter ingredients (comma separated):")

# if st.button("Get Recipe"):

#     if query:
#         # Retrieve relevant recipes
#         docs = vector_db.similarity_search(query, k=3)

#         context = "\n\n".join([doc.page_content for doc in docs])

#         # Prompt
#         prompt = f"""
# You are a smart cooking assistant.

# User ingredients: {query}

# Based on the recipes below:
# {context}

# Do the following:
# 1. Suggest the best matching recipe
# 2. Provide clear step-by-step instructions
# 3. List missing ingredients (if any)

# Format the answer neatly.
# """

#         # Generate response
#         response = llm.invoke(prompt)

#         st.subheader("Suggested Recipe")
#         st.write(response.content)

#     else:
#         st.warning("Please enter some ingredients!")

import streamlit as st
import os
import re
from dotenv import load_dotenv

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

# -----------------------------
# Load embeddings
# -----------------------------
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# -----------------------------
# Load FAISS index
# -----------------------------
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
# UTIL FUNCTIONS
# -----------------------------

def clean_user_input(query):
    return [i.strip().lower() for i in query.split(",")]

def extract_ingredients(text):
    match = re.search(r"Ingredients:(.*?)(Instructions:|Directions:|$)", text, re.S)
    if match:
        ingredients_text = match.group(1)
        return [i.strip().lower() for i in re.split(r",|\n", ingredients_text) if i.strip()]
    return []

def get_missing(user_ing, recipe_ing):
    missing = []
    for r in recipe_ing:
        if not any(u in r or r in u for u in user_ing):
            missing.append(r)
    return missing

# -----------------------------
# UI
# -----------------------------
st.set_page_config(page_title="Recipe Generator", page_icon="🍳")

st.title("AI Recipe Generator (Correct RAG)")
st.write("Enter ingredients and get accurate recipe!")

query = st.text_input("Enter ingredients (comma separated):")

if st.button("Get Recipe"):

    if query:

        user_ing = clean_user_input(query)

        # -----------------------------
        # RAG retrieval
        # -----------------------------
        docs = vector_db.similarity_search(query, k=3)

        best_doc = None
        best_score = -1

        for doc in docs:
            text = doc.page_content
            recipe_ing = extract_ingredients(text)

            overlap = sum(
                1 for r in recipe_ing
                if any(u in r or r in u for u in user_ing)
            )

            if overlap > best_score:
                best_score = overlap
                best_doc = doc

        if not best_doc:
            st.error("No suitable recipe found")
        else:
            recipe_text = best_doc.page_content
            recipe_ing = extract_ingredients(recipe_text)

            # -----------------------------
            # Missing ingredients (BACKEND)
            # -----------------------------
            missing = get_missing(user_ing, recipe_ing)

            missing_text = "None" if not missing else ", ".join(missing)

            # -----------------------------
            # LLM ONLY for explanation
            # -----------------------------
            prompt = f"""
                You are a cooking expert.

                STRICT RULES:
                - Use ONLY the given recipe
                - DO NOT change ingredients

                Recipe:
                {recipe_text}

                Tasks:
                1. Give recipe name
                2. Explain each step clearly in detail

                FORMAT:

                Recipe Name:
                ...

                Steps:
                1. ...
                2. ...
                """

            response = llm.invoke(prompt)

            # -----------------------------
            # OUTPUT
            # -----------------------------
            st.subheader("Recipe Output")
            st.write(response.content)

            st.subheader("Missing Ingredients")
            st.write(missing_text)

    else:
        st.warning("Please enter ingredients!")