import os
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()

PERSIST_DIRECTORY = "data/db/chroma_db"

_embeddings = None
_vector_store = None

def get_vector_store():
    """Initializes or loads the vector store with caching."""
    global _embeddings, _vector_store
    
    if _embeddings is None:
        _embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    
    if _vector_store is None:
        if os.path.exists(PERSIST_DIRECTORY):
            _vector_store = Chroma(persist_directory=PERSIST_DIRECTORY, embedding_function=_embeddings)
        else:
            # Create an empty one if it doesn't exist
            _vector_store = Chroma(persist_directory=PERSIST_DIRECTORY, embedding_function=_embeddings)
            
    return _vector_store

def index_invoice(text, metadata):
    """Indexes invoice text into the vector store."""
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = text_splitter.create_documents([text], metadatas=[metadata])
    
    vector_store = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory=PERSIST_DIRECTORY
    )
    return vector_store

def search_invoices(query, k=3):
    """Searches for relevant invoice snippets."""
    vector_store = get_vector_store()
    results = vector_store.similarity_search(query, k=k)
    return results
