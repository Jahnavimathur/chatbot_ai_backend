from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import user, chat, documents
from app.db.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

description = """
Chatbot AI Backend API 🚀

A comprehensive backend for a Chatbot AI application, featuring:
* **User Authentication** (Signup/Login with JWT)
* **Chat Sessions** (Session management and AI interaction)
* **Document Management** (PDF uploading and RAG search)

Used by the Next.js frontend.
"""

tags_metadata = [
    {
        "name": "auth",
        "description": "Operations with users and authentication. Including login and signup.",
    },
    {
        "name": "chat",
        "description": "Core chat functionality. Create sessions and send messages to the AI.",
    },
    {
        "name": "documents",
        "description": "Document management for Knowledge Base / RAG.",
    },
]
app = FastAPI(
    title="Chatbot AI API",
    description=description,
    version="1.0.0",
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(chat.router)
app.include_router(documents.router)

@app.get("/", tags=["health"], summary="Health Check")
def read_root():
    """
    Returns a simple message to check if the API is running correctly.
    """
    return {"message": "Hello from Chatbot AI Backend 🚀"}