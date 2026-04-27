# AI Recipe Assistant (RAG-Based)

## Overview

The AI Recipe Assistant is an intelligent application that helps users discover recipes using either available ingredients or dish-based queries. The system uses Retrieval-Augmented Generation (RAG) to combine semantic search with a Large Language Model (LLM) to provide accurate and structured cooking instructions.

---

## Features

* Ingredient-based recipe recommendation
* Dish-based query handling (e.g., "how to make pasta")
* Missing ingredient detection
* Step-by-step cooking instructions
* Out-of-domain query detection
* Chat-based user interface
* Semantic search using FAISS
* Hybrid RAG architecture (logic + LLM)

---

## Tech Stack

* Frontend: HTML, CSS, JavaScript
* Backend: FastAPI (Python)
* Vector Database: FAISS
* Embeddings: Sentence Transformers (all-MiniLM-L6-v2)
* LLM: Groq (LLaMA 3.1)
* Environment: Python Virtual Environment, VS Code

---

## Project Structure

```
ai_mini_RAG/
│
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── style.css
│
├── main.py
├── app.py
├── clean.py
├── remove_columns.py
├── RAG.ipynb
├── README.md
├── .gitignore
└── .env
```

---

## How It Works

1. User enters a query (ingredients or dish name)
2. Query is converted into embeddings
3. FAISS retrieves the most relevant recipes
4. Backend selects the best match
5. Missing ingredients are computed (if applicable)
6. LLM generates structured response
7. Output is displayed in the frontend

---

## Setup Instructions

### 1. Clone the Repository

```
git clone https://github.com/Naren04karthik/ai_mini_RAG.git
cd ai_mini_RAG
```

---

### 2. Create Virtual Environment

```
python -m venv .venv
```

Activate:

**Windows:**

```
.venv\Scripts\activate
```

---

### 3. Install Dependencies

```
pip install fastapi uvicorn langchain langchain-community langchain-huggingface langchain-groq sentence-transformers faiss-cpu python-dotenv
```

---

### 4. Setup Environment Variables

Create a `.env` file in root:

```
GROQ_API_KEY=your_groq_api_key_here
```

---

### 5. Run Backend (FastAPI)

```
uvicorn main:app --reload
```

Server will run at:

```
http://127.0.0.1:8000
```

---

### 6. Run Frontend

* Open `frontend/index.html` in browser
  OR
* Use Live Server in VS Code

---

## Conclusion

This project demonstrates the effective use of Retrieval-Augmented Generation (RAG) by combining FAISS-based semantic retrieval with LLM-based response generation. It provides a practical and user-friendly solution for recipe discovery and cooking assistance.

---
