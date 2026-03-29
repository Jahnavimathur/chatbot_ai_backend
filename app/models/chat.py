from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Text, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base
import enum

class RoleEnum(enum.Enum):
    user = "user"
    assistant = "assistant"

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    title = Column(String(255))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("Message", back_populates="session", cascade="all, delete")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id", ondelete="CASCADE"))
    role = Column(Enum(RoleEnum))
    content = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    # Relationships
    session = relationship("ChatSession", back_populates="messages")

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    file_name = Column(String(255))
    file_path = Column(Text)
    uploaded_at = Column(TIMESTAMP, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="documents")
    embeddings = relationship("Embedding", back_populates="document", cascade="all, delete")

class Embedding(Base):
    __tablename__ = "embeddings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"))
    content = Column(Text)
    embedding = Column(JSON)

    # Relationships
    document = relationship("Document", back_populates="embeddings")
