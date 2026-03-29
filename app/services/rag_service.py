import io
import PyPDF2
from sqlalchemy.orm import Session
import numpy as np
from app.models.chat import Document, Embedding
from app.services.ollama_service import get_embedding

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extracts text from a raw PDF byte stream."""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception as e:
        print(f"Error extracting PDF: {e}")
        return ""

def split_text_into_chunks(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    """A basic text splitter to chunk document contents."""
    chunks = []
    start = 0
    text_length = len(text)
    while start < text_length:
        end = start + chunk_size
        chunks.append(text[start:end])
        start += (chunk_size - overlap)
    return chunks

def process_document(file_name: str, file_path: str, file_bytes: bytes, user_id: int, db: Session) -> Document:
    """
    Complete flow for uploading a document:
    1. Create Document record in DB.
    2. Extract text.
    3. Split into embeddings.
    4. Save to DB.
    """
    # 1. Create document record
    db_doc = Document(user_id=user_id, file_name=file_name, file_path=file_path)
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    
    # 2. Extract text
    text = extract_text_from_pdf(file_bytes)
    
    # 3. Split into chunks
    chunks = split_text_into_chunks(text)
    
    # 4. Generate embeddings and store
    for chunk in chunks:
        if not chunk.strip():
            continue
        try:
            emb_vector = get_embedding(chunk)
            db_emb = Embedding(
                document_id=db_doc.id,
                content=chunk,
                embedding=emb_vector # Store as list, SQLAlchemy JSON handles conversion
            )
            db.add(db_emb)
        except Exception as e:
            print(f"Error generating embedding for chunk: {e}")
            continue
            
    db.commit()
    return db_doc

def cosine_similarity(v1, v2):
    """Computes cosine similarity between two vectors."""
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0
    return dot_product / (norm_v1 * norm_v2)

def search_similar_chunks(query: str, db: Session, user_id: int = None, top_k: int = 3) -> str:
    """
    Searches for the `top_k` most similar chunks in the MySQL database.
    Does a simple brute-force cosine similarity check in-memory.
    """
    query_emb = get_embedding(query)
    
    # Fetch all embeddings. If user_id is provided, filter by user's documents
    if user_id:
        all_embs = db.query(Embedding).join(Document).filter(Document.user_id == user_id).all()
    else:
        all_embs = db.query(Embedding).all()
    
    scored_chunks = []
    for emb in all_embs:
        db_vec = emb.embedding
        if not db_vec or not isinstance(db_vec, list):
            continue
        score = cosine_similarity(query_emb, db_vec)
        scored_chunks.append((score, emb.content))
        
    # Sort by highest similarity
    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    
    top_chunks = [chunk for score, chunk in scored_chunks[:top_k]]
    return "\n\n".join(top_chunks)
