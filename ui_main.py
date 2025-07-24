import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"  # Replace with your actual FastAPI server URL

st.title("📄 Chroma QA Langchain App")

# Session state for storing session_id
if "session_id" not in st.session_state:
    st.session_state.session_id = None

# 1. Upload PDF Section
st.header("Upload Your PDF")
uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

if uploaded_file is not None:
    with st.spinner("Uploading and processing..."):
        files = {"file": uploaded_file.getvalue()}
        response = requests.post(
            f"{API_URL}/upload_pdf", files={"file": uploaded_file})
        if response.status_code == 200:
            session_id = response.json()["session_id"]
            st.session_state.session_id = session_id
            st.success(f"PDF uploaded! Session ID: {session_id}")
        else:
            st.error(f"Upload failed: {response.text}")

# 2. Question Answering Section
if st.session_state.session_id:
    st.header("Ask Questions")
    question = st.text_input("Enter your question about the PDF:")

    if st.button("Get Answer") and question.strip() != "":
        payload = {
            "session_id": st.session_state.session_id,
            "question": question
        }
        with st.spinner("Thinking..."):
            response = requests.post(f"{API_URL}/chat", json=payload)
            if response.status_code == 200:
                answer = response.json()["answer"]
                st.success("Answer:")
                st.write(answer)
            else:
                st.error(f"Error getting answer: {response.text}")
else:
    st.info("Please upload a PDF to start.")
