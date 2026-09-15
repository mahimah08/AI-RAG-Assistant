import time
import streamlit as st
from src.ingest import save_uploaded_resume
from src.rag import ask_question

st.set_page_config(page_title="AI Resume Assistant", page_icon="📄", layout="wide")
st.markdown("""
<style>
.block-container {max-width:1100px; padding-top:2.5rem;}
.hero {padding:1.2rem 0 1.6rem;}
.eyebrow {color:#60a5fa; font-weight:700; letter-spacing:.09em; font-size:.78rem;}
.subtle {color:#a7b0c0; font-size:1.08rem;}
.card {background:rgba(30,41,59,.55); border:1px solid rgba(148,163,184,.18); border-radius:14px; padding:1rem; min-height:105px;}
.card h4 {margin:0 0 .4rem 0;}
.card p {color:#b7c0ce; margin:0; font-size:.9rem;}
</style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.title("📄 Resume workspace")
    st.caption("Private • local • free to run")
    uploaded_file = st.file_uploader("Upload a PDF resume", type=["pdf"])
    if uploaded_file:
        st.success(f"Selected: {uploaded_file.name}")
        if st.button("Prepare this resume", type="primary", use_container_width=True):
            try:
                with st.spinner("Extracting and indexing the resume..."):
                    sections = save_uploaded_resume(uploaded_file)
                st.session_state.messages = []
                st.success(f"Ready — {sections} searchable sections created.")
            except Exception as error:
                st.error(f"Could not prepare the resume: {error}")
    st.divider()
    st.subheader("What this demonstrates")
    st.markdown("""
- Retrieval-Augmented Generation (RAG)
- Local embeddings and vector search
- Private on-device AI with Ollama
- Grounded answers with page references
""")
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.caption("Your uploaded PDF, database, and AI processing stay on this Mac.")

st.markdown("""
<div class="hero">
<div class="eyebrow">LOCAL RAG APPLICATION</div>
<h1>AI Resume Assistant</h1>
<p class="subtle">Turn a resume into an interactive, evidence-based conversation — without sending personal data to a cloud AI service.</p>
</div>
""", unsafe_allow_html=True)

one, two, three = st.columns(3)
with one:
    st.markdown('<div class="card"><h4>🔒 Private by design</h4><p>Documents and AI processing remain on your Mac.</p></div>', unsafe_allow_html=True)
with two:
    st.markdown('<div class="card"><h4>⚡ Ask in plain English</h4><p>Explore skills, experience, education, and projects instantly.</p></div>', unsafe_allow_html=True)
with three:
    st.markdown('<div class="card"><h4>📌 Grounded responses</h4><p>Answers use only the uploaded resume and include page references.</p></div>', unsafe_allow_html=True)

st.divider()
st.subheader("Ask the resume")
st.caption("Choose an example or type your own question.")
left, middle, right = st.columns(3)
with left:
    skills = st.button("Strongest technical skills", use_container_width=True)
with middle:
    projects = st.button("Summarize projects", use_container_width=True)
with right:
    experience = st.button("Relevant experience", use_container_width=True)

if skills:
    st.session_state.pending_question = "What are the candidate's strongest technical skills?"
elif projects:
    st.session_state.pending_question = "Summarize the candidate's projects."
elif experience:
    st.session_state.pending_question = "What relevant experience does this candidate have?"

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if message.get("pages"):
            st.caption("Resume page(s): " + ", ".join(map(str, message["pages"])))

question = st.chat_input("Ask about skills, projects, education, or experience...")
if not question:
    question = st.session_state.pop("pending_question", None)
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)
    with st.chat_message("assistant"):
        try:
            started = time.perf_counter()
            with st.spinner("Searching the resume and writing an answer..."):
                answer, pages = ask_question(question)
            seconds = time.perf_counter() - started
            st.write(answer)
            st.caption("Resume page(s): " + ", ".join(map(str, pages)) + f" • Answered locally in {seconds:.1f}s")
            st.session_state.messages.append({"role": "assistant", "content": answer, "pages": pages})
        except Exception as error:
            st.error(f"Could not answer that question: {error}")
