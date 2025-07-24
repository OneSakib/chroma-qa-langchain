from langchain.chains import RetrievalQA
import chromadb
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from uuid import uuid4

load_dotenv()


class CreateVectorStore:
    def __init__(self, session_id) -> None:
        self.session_id = session_id
        self.collection_name = f"qa_chat_{session_id}"
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500, chunk_overlap=50)

    def preprocess(self, file_path):
        # Read PDF FILE
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        self.doc = self.text_splitter.split_documents(documents)
        self.persist_directory = "./db"

    def remove_collection(self):
        client = chromadb.PersistentClient(path=self.persist_directory)
        try:
            client.delete_collection(name=self.collection_name)
        except Exception:
            pass

    def invoke(self, file_path):
        self.preprocess(file_path)
        self.remove_collection()
        vector_store = Chroma(
            embedding_function=self.embeddings,
            collection_name=self.collection_name,
            persist_directory=self.persist_directory
        )
        uuids = [str(uuid4()) for _ in range(len(self.doc))]
        vector_store.add_documents(documents=self.doc, ids=uuids)


class VectorSearch:
    def __init__(self, session_id) -> None:
        self.session_id = session_id
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
        self.collection_name = f"qa_chat_{session_id}"
        self.persist_directory = "./db"
        self.llm = ChatOpenAI(model="gpt-4o")

    def invoke(self, question):
        vector_store = Chroma(
            embedding_function=self.embeddings,
            collection_name=self.collection_name,
            persist_directory=self.persist_directory)
        retriever = vector_store.as_retriever(
            search_type="mmr", search_kwargs={"k": 1, "fetch_k": 5})
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm, retriever=retriever)
        result = qa_chain.invoke(question)
        return result['result']
