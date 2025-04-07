# 🧠 Promtior RAG Chatbot

A Retrieval-Augmented Generation (RAG) chatbot that allows users to ask questions about content extracted from a specific URL. This project is designed to provide intelligent responses about Promtior's website by combining scraping, embeddings, and LLM-powered generation.

---

## 🚀 Features

- 🔍 Scrapes web content dynamically
- 🧠 Uses a RAG architecture for contextualized answers
- 💬 Chat interface ready to be consumed by a frontend
- 🌐 API exposed via FastAPI
- ⚡ Integration with GeminiAI for language generation
- 📚 Pinecone vector database for semantic search

---

## 🛠️ Tech Stack

- **Python 3.10+**
- **FastAPI** – API backend framework
- **LangChain** – RAG orchestration
- **Pinecone** – Vector database
- **Gemini AI** – Language model API
- **Playwright** - For advanced scraping tasks

---

## 📡 Live Demo

> 🧪 You can test the deployed API here:  
> [https://askbot.up.railway.app](https://askbot.up.railway.app)

---

## 📦 API Endpoints

| Method | Endpoint       | Description                             |
|--------|----------------|-----------------------------------------|
| GET    | `/health`      | Health check with service status        |
| POST   | `/ask`         | Ask a question about the scraped site   |
| GET    | `/`            | (Optional) Serves `index.html` frontend |

---


#  📧 Support
For any issues or questions, feel free to reach out to Luis Gonzalo Cao.        
email: luisgonzalocao@gmail.com           
linkedin: https://linkedin.com/in/luis-gonzalo-cao
