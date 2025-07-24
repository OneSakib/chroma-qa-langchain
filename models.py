from pydantic import BaseModel


class UploadFileResponse(BaseModel):
    session_id: str


class ChatRequest(BaseModel):
    session_id: str
    question: str


class ChatResponse(BaseModel):
    session_id: str
    answer: str
