import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.utils.auth import get_current_user
from app.services.rag_service import process_document
from app.schemas.documents import Document as DocumentSchema
from app.models.chat import Document

router = APIRouter(prefix="/documents", tags=["documents"])

UPLOAD_DIRECTORY = "uploads"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

@router.post("/upload", response_model=DocumentSchema, summary="Upload and process a PDF")
async def upload_document(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    Upload a PDF document. It will be automatically:
    1. Saved to the server storage.
    2. Split into chunks.
    3. Converted into embeddings and stored for Vector Search (RAG).
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    file_path = os.path.join(UPLOAD_DIRECTORY, f"{current_user.id}_{file.filename}")
    
    # Save file to disk
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Read bytes for PyPDF2
    with open(file_path, "rb") as f:
        file_bytes = f.read()
        
    try:
        # DB saving, extraction, and embedding happens in process_document
        document = process_document(
            file_name=file.filename,
            file_path=file_path,
            file_bytes=file_bytes,
            user_id=current_user.id,
            db=db
        )
        return document
    except Exception as e:
        print(f"Error processing document: {e}")
        # In case of partial failure, you might want to rollback or cleanup
        raise HTTPException(status_code=500, detail="Error processing and embedding document.")

@router.get("", response_model=list[DocumentSchema], summary="List all user documents")
def get_documents(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Get a list of all documents uploaded by the current user.
    """
    documents = db.query(Document).filter(Document.user_id == current_user.id).all()
    return documents
