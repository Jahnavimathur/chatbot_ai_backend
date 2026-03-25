from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import user
from app.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Chatbot AI API")

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)

@app.get("/")
def read_root():
    return {"message": "Hello from Chatbot AI Backend 🚀"}