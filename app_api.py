from models import *
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from uuid import uuid4
from fastapi.middleware.cors import CORSMiddleware
from qa_search import CreateVectorStore, VectorSearch
import os
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

FILE_ROOT_FILDER = os.path.join(os.curdir, 'upload_files')
os.makedirs(FILE_ROOT_FILDER, exist_ok=True)


@app.post('/upload_pdf')
async def upload_pdf(file: UploadFile = File(...)):
    file_extension = file.filename.split('.')[-1]
    if file_extension not in ('pdf',):
        raise HTTPException(status_code=400, detail="Please Uplaod PDF File")
    session_id = str(uuid4())
    file_path = os.path.join(FILE_ROOT_FILDER, f"user_{session_id}")
    try:
        with open(file_path, 'wb') as f:
            content = await file.read()
            f.write(content)
        vector_store = CreateVectorStore(session_id)
        vector_store.invoke(file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
    return JSONResponse(status_code=200, content={"session_id": session_id})


@app.post('/chat', response_model=ChatResponse)
def chat_(request: ChatRequest):
    vector_search = VectorSearch(session_id=request.session_id)
    answer = vector_search.invoke(request.question)
    return ChatResponse(session_id=request.session_id, answer=answer)
