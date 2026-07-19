import os
import tempfile
from uuid import uuid4
import streamlit as st
from dotenv import load_dotenv

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from groq import Groq

# Load environment variables
parent_dotenv = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
if os.path.exists(parent_dotenv):
    load_dotenv(parent_dotenv)
else:
    load_dotenv()

# Configuration
QDRANT_URL = os.getenv("QDRANT_END_POINT")
QDRANT_API_KEY = os.getenv("QDRANT_API")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Set up Page Config
st.set_page_config(
    page_title="RAG Chatbot Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium Styling
st.markdown("""
<style>
    /* Styling headers and fonts */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    .main-title {
        background: linear-gradient(90deg, #FF4B4B, #FF8F8F);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        color: #888888;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* Enhance sidebar background and aesthetic */
    section[data-testid="stSidebar"] {
        background-color: #0f1116;
        border-right: 1px solid #1f2937;
    }
    
    /* Custom status badges */
    .status-badge {
        padding: 6px 12px;
        border-radius: 8px;
        font-weight: 600;
        display: inline-block;
        margin-top: 10px;
    }
    .status-indexed {
        background-color: rgba(16, 185, 129, 0.15);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    .status-empty {
        background-color: rgba(239, 68, 68, 0.15);
        color: #ef4444;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Caching Resources
# -----------------------------------------------------------------------------
@st.cache_resource
def get_embedding_model():
    """Load and cache HuggingFace embeddings model."""
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

@st.cache_resource
def get_qdrant_client():
    """Configure and cache Qdrant Client connection."""
    if not QDRANT_URL or not QDRANT_API_KEY:
        st.error("Missing Qdrant configuration in env variables.")
        return None
    return QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

@st.cache_resource
def get_groq_client():
    """Configure and cache Groq Client."""
    if not GROQ_API_KEY:
        st.error("Missing GROQ_API_KEY in env variables.")
        return None
    return Groq(api_key=GROQ_API_KEY)

# Initialize cached components
embedding_model = get_embedding_model()
qdrant_client = get_qdrant_client()
groq_client = get_groq_client()

# -----------------------------------------------------------------------------
# Ingestion helper
# -----------------------------------------------------------------------------
def ingest_pdf_file(uploaded_file, collection_name):
    """process and upload pdf content to qdrant."""
    if not qdrant_client or not embedding_model:
        return False
        
    try:
        # Create temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            temp_path = tmp_file.name
            
        with st.spinner("Parsing PDF pages..."):
            loader = PyPDFLoader(temp_path)
            documents = loader.load()
            
        with st.spinner("Chunking text content..."):
            splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
            chunks = splitter.split_documents(documents)
            
        with st.spinner("Generating embeddings (SentenceTransformers)..."):
            texts = [doc.page_content for doc in chunks]
            embeddings = embedding_model.embed_documents(texts)
            
        with st.spinner(f"Updating Qdrant Collection ({collection_name})..."):
            # Check if collection exists, if not create it (to allow incremental load / append)
            try:
                collections = qdrant_client.get_collections().collections
                exist = any(c.name == collection_name for c in collections)
            except Exception:
                exist = False
                
            if not exist:
                qdrant_client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=len(embeddings[0]),
                        distance=Distance.COSINE,
                    ),
                )
            
            # Prepare points JSON
            points = []
            for doc, vector in zip(chunks, embeddings):
                points.append(
                    PointStruct(
                        id=str(uuid4()),
                        vector=vector,
                        payload={
                            "text": doc.page_content,
                            "source": uploaded_file.name,
                            "page": doc.metadata.get("page", 0) + 1,
                        },
                    )
                )
            
            # Upsert
            qdrant_client.upsert(collection_name=collection_name, points=points)
            
        # Cleanup temp file
        try:
            os.remove(temp_path)
        except Exception:
            pass
            
        return len(points)
    except Exception as e:
        st.error(f"Failed to ingest PDF: {e}")
        return None

# -----------------------------------------------------------------------------
# Sidebar layout
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### � User Info")
    user_name = st.text_input("Enter your username:", value="guest").strip()
    
    # Sanitize username so it's a valid Qdrant collection name
    import re
    username_sanitized = re.sub(r'[^a-zA-Z0-9_-]', '', user_name).lower()
    if not username_sanitized:
        username_sanitized = "guest"
    collection_name = f"rag_{username_sanitized}"
    
    st.markdown("---")
    st.markdown("### �📎 Document Ingestion")
    uploaded_file = st.file_uploader(
        "Upload a PDF context document:",
        type=["pdf"],
        help="Only PDF files are supported."
    )
    
    # Session state settings
    if "indexed_file" not in st.session_state:
        st.session_state.indexed_file = None
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    if uploaded_file is not None:
        # Check if this file is already indexed
        if st.session_state.indexed_file != (collection_name + "_" + uploaded_file.name):
            st.warning("New file detected. Click index to begin ingestion.")
            if st.button("🚀 Index Document", use_container_width=True):
                chunk_count = ingest_pdf_file(uploaded_file, collection_name)
                if chunk_count:
                    st.session_state.indexed_file = collection_name + "_" + uploaded_file.name
                    st.session_state.messages = [] # Clear history on new document
                    st.success(f"Indexed {chunk_count} chunks successfully!")
                    st.rerun()
        else:
            st.markdown(f'<div class="status-badge status-indexed">🟢 Current: {uploaded_file.name}</div>', unsafe_allow_html=True)
            if st.button("🗑️ Clear Indexed Data", use_container_width=True):
                st.session_state.indexed_file = None
                st.session_state.messages = []
                if qdrant_client:
                    try:
                        qdrant_client.delete_collection(collection_name)
                    except Exception:
                        pass
                st.rerun()
    else:
        st.markdown('<div class="status-badge status-empty">🔴 No active document indexed</div>', unsafe_allow_html=True)
        # Reset if file removed
        if st.session_state.indexed_file is not None:
            st.session_state.indexed_file = None
            st.session_state.messages = []
            st.rerun()
            
    st.markdown("---")
    st.markdown("### ⚙️ LLM Configuration")
    llm_model = st.selectbox(
        "Select LLM Model:",
        ["llama-3.3-70b-versatile", "qwen/qwen3.6-27b", "openai/gpt-oss-120b"],
        index=0
    )
    retrieval_limit = st.slider(
        "Context Chunks Limit:",
        min_value=1,
        max_value=10,
        value=3
    )

# -----------------------------------------------------------------------------
# Main panel
# -----------------------------------------------------------------------------
st.markdown('<div class="main-title">RAG Chatbot</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Upload a PDF in the sidebar to ask questions and chat with the document content.</div>', unsafe_allow_html=True)

# Check if document is uploaded
if not st.session_state.indexed_file:
    st.info("👈 Please start by uploading and indexing a PDF document in the sidebar.")
else:
    # Display chat messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    # Input box
    if user_query := st.chat_input("Ask a question about the document..."):
        # Append user message
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)
            
        with st.chat_message("assistant"):
            if not qdrant_client or not groq_client:
                st.write("Clients are not configured. Please check console.")
            else:
                progress_placeholder = st.empty()
                
                try:
                    # 1. Search contexts
                    progress_placeholder.info("Searching document context...")
                    query_vector = embedding_model.embed_query(user_query)
                    
                    search_result = qdrant_client.query_points(
                        collection_name=collection_name,
                        query=query_vector,
                        limit=retrieval_limit,
                        with_payload=True
                    )
                    
                    hits = search_result.points
                    
                    context_texts = []
                    for hit in hits:
                        payload = hit.payload
                        txt = payload.get("text", "")
                        src = payload.get("source", "Unknown")
                        pg = payload.get("page", "Unknown")
                        context_texts.append(f"Source: {src} (Page {pg})\nContent: {txt}\n---")
                        
                    # Clean progress info
                    progress_placeholder.empty()
                    
                    # 2. Build prompting context
                    context_str = "\n".join(context_texts) if context_texts else "No relevant context found."
                    
                    system_prompt = f"""You are a helpful assistant.
                    
Answer the question ONLY using the supplied context below.

If the answer is not present, reply exactly:
'I cannot find the answer in the provided document.'

Context:
{context_str}
"""
                    
                    # 3. Request streaming response from Groq
                    messages_payload = [
                        {"role": "system", "content": system_prompt}
                    ]
                    
                    # Append history (excluding system prompt helper)
                    # We send up to 8 of context history turns
                    for msg in st.session_state.messages[-8:-1]:
                        messages_payload.append({"role": msg["role"], "content": msg["content"]})
                        
                    # Add current query
                    messages_payload.append({"role": "user", "content": user_query})
                    
                    def stream_generator():
                        response_stream = groq_client.chat.completions.create(
                            model=llm_model,
                            messages=messages_payload,
                            temperature=0.2,
                            stream=True
                        )
                        for chunk in response_stream:
                            val = chunk.choices[0].delta.content
                            if val is not None:
                                yield val
                                
                    response_text = st.write_stream(stream_generator())
                    
                    # Store assistance response
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                    
                except Exception as e:
                    progress_placeholder.empty()
                    st.error(f"An error occurred during query generation: {e}")
