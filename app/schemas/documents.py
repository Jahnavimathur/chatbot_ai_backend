from pydantic import BaseModel
from datetime import datetime

class DocumentBase(BaseModel):
    file_name: str
    
class DocumentCreate(DocumentBase):
    file_path: str
    
class Document(DocumentBase):
    id: int
    user_id: int
    uploaded_at: datetime
    
    class Config:
        from_attributes = True
