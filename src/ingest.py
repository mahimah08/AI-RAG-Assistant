from pathlib import Path
import shutil

from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


PROJECT_DIR = Path(__file__).resolve().parent.parent
DOCUMENTS_DIR = PROJECT_DIR / "documents"
DATABASE_DIR = PROJECT_DIR / "chroma_db"
RESUME_FILE = DOCUMENTS_DIR / "resume.pdf"


def load_documents():
    # Prefer the resume uploaded through the app.
    pdf_files = [RESUME_FILE] if RESUME_FILE.exists() else list(DOCUMENTS_DIR.glob("*.pdf"))

    if not pdf_files:
        raise FileNotFoundError("Please upload a resume PDF first.")

    documents = []

    for pdf_file in pdf_files:
        loader = PyPDFLoader(str(pdf_file))
        documents.extend(loader.load())

    return documents


def create_vector_database():
    documents = load_documents()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
    )
    chunks = text_splitter.split_documents(documents)

    embeddings = OllamaEmbeddings(model="nomic-embed-text")

    if DATABASE_DIR.exists():
        shutil.rmtree(DATABASE_DIR)

    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(DATABASE_DIR),
    )

    return len(chunks)


def save_uploaded_resume(uploaded_file):
    DOCUMENTS_DIR.mkdir(exist_ok=True)
    RESUME_FILE.write_bytes(uploaded_file.getvalue())
    return create_vector_database()


if __name__ == "__main__":
    sections = create_vector_database()
    print(f"Done! Created {sections} searchable resume sections.")