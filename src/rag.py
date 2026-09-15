from pathlib import Path

from langchain_chroma import Chroma
from langchain_ollama import ChatOllama, OllamaEmbeddings


PROJECT_DIR = Path(__file__).resolve().parent.parent
DATABASE_DIR = PROJECT_DIR / "chroma_db"


def ask_question(question):
    if not DATABASE_DIR.exists():
        raise FileNotFoundError("No resume database exists. Upload a resume first.")

    embeddings = OllamaEmbeddings(model="nomic-embed-text")

    database = Chroma(
        persist_directory=str(DATABASE_DIR),
        embedding_function=embeddings,
    )

    results = database.similarity_search(question, k=4)
    context = "\n\n".join(result.page_content for result in results)

    prompt = f"""
You are a professional resume assistant.

Answer only from the resume information below.
If the answer is not in the resume, say:
"I could not find that information in the resume."

Resume information:
{context}

Question: {question}

Give a clear, concise answer:
"""

    model = ChatOllama(model="llama3.2:3b", temperature=0)
    response = model.invoke(prompt)

    pages = sorted(
        {
            document.metadata.get("page", 0) + 1
            for document in results
        }
    )

    return response.content, pages