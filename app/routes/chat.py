from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.chat import ChatSession, Message, RoleEnum
from app.schemas.chat import ChatSessionCreate, ChatSession as ChatSessionSchema, ChatRequest, Message as MessageSchema
from app.models.user import User
from app.utils.auth import get_current_user
from app.services.ollama_service import get_chat_response
from app.services.rag_service import search_similar_chunks

router = APIRouter(prefix="", tags=["chat"])

@router.post("/create-session", response_model=ChatSessionSchema)
def create_session(session: ChatSessionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_session = ChatSession(user_id=current_user.id, title=session.title)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

@router.get("/chat/{session_id}", response_model=list[MessageSchema])
def get_session_chat(session_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    messages = db.query(Message).filter(Message.session_id == session_id).order_by(Message.created_at.asc()).all()
    return messages

@router.post("/chat", response_model=MessageSchema)
def send_message(request: ChatRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_session = db.query(ChatSession).filter(ChatSession.id == request.session_id, ChatSession.user_id == current_user.id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    # 1. Save user message to DB
    user_message = Message(session_id=request.session_id, role=RoleEnum.user, content=request.message)
    db.add(user_message)
    db.commit()
    db.refresh(user_message)
    
    # 2. Fetch previous messages context
    # Get last 10 messages for conversation context
    recent_messages = db.query(Message).filter(Message.session_id == request.session_id).order_by(Message.created_at.desc()).limit(10).all()
    recent_messages.reverse() # Reverse so they are in chronological order
    
    # 3. Optional RAG: Search embeddings for knowledge base augmentation
    try:
        context = search_similar_chunks(request.message, db=db, user_id=current_user.id, top_k=3)
    except Exception as e:
        print(f"RAG search error: {e}")
        context = ""
    
    # 4. Send to Ollama
    try:
        ai_response_text = get_chat_response(messages=recent_messages, context=context)
    except Exception as e:
        print(f"Ollama error: {e}")
        raise HTTPException(status_code=500, detail="Error communicating with AI service.")
        
    # 5. Save AI response
    ai_message = Message(session_id=request.session_id, role=RoleEnum.assistant, content=ai_response_text)
    db.add(ai_message)
    db.commit()
    db.refresh(ai_message)
    
    # 6. Return response to frontend
    return ai_message
