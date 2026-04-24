# AI Recipe Generator (RAG-Based Chatbot)

An intelligent recipe recommendation chatbot built using Retrieval-Augmented Generation (RAG).  
The system suggests recipes based on available ingredients and generates step-by-step cooking instructions using large language models.

---

## Features

- Ingredient-based recipe search  
- Retrieval-Augmented Generation (RAG) pipeline using FAISS  
- LLM-powered response generation using Groq (LLaMA 3.1)  
- Interactive user interface using Streamlit  
- Chat history tracking  
- Fast semantic search using embeddings  

---

## Tech Stack

- Frontend: Streamlit  
- Backend: Python  
- LLM: Groq (LLaMA 3.1)  
- Vector Database: FAISS  
- Embeddings: Sentence Transformers (MiniLM)  
- Framework: LangChain  

---

## Architecture

User Input (Ingredients)  
→ FAISS Vector Search (Top-K Recipes)  
→ Context Retrieval  
→ LLM (Groq - LLaMA 3.1)  
→ Generated Recipe and Instructions  

---

## Setup Instructions

### 1. Clone the Repository

git clone https://github.com/your-username/ai_mini_RAG.git  
cd ai_mini_RAG  

---

### 2. Create Virtual Environment

python -m venv venv  
venv\Scripts\activate  

---

### 3. Install Dependencies

pip install streamlit langchain langchain-community langchain-huggingface langchain-groq faiss-cpu sentence-transformers python-dotenv  

---

### 4. Add API Key

Create a `.env` file in the root directory:

GROQ_API_KEY=your_api_key_here  

---

### 5. Run the Application

python -m streamlit run app.py  

---

## Example Usage

Input:  
tomato, onion, garlic  

Output:  
- Suggested recipe  
- Step-by-step instructions  
- Missing ingredients  

---

## Dataset

Source: Kaggle (3A2M Recipe Dataset)  

Features:
- Title  
- Directions  
- Ingredients (NER)  
- Genre  

The dataset was cleaned, balanced across categories, and converted into structured documents for efficient retrieval.

---

## Key Highlights

- Efficient handling of large-scale dataset through sampling  
- Semantic retrieval using FAISS vector database  
- Modular pipeline: Data Processing → Embedding → Retrieval → Generation  
- Integration of LLM with retrieval for context-aware responses  

---

## Future Improvements

- Ingredient matching optimization  
- Nutritional filtering (calories, diet type)  
- Image-based ingredient detection  
- Cloud deployment  

---
