import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from mcpq import Minecraft

from src.agents.sqlalchemy_store import SQLAlchemyStore

load_dotenv()

print("Loading configuration...")
print("Connecting to Minecraft server...")
mc = Minecraft(host="192.168.9.132", port=14445)

print("Setting up LLM...")
llm = ChatOpenAI(model="gpt-4.1-nano")

PROJECT_ROOT = Path(__file__).parent.parent

print("Initializing vector store...")
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Load FAISS index if it exists, otherwise create empty one
FAISS_INDEX_PATH = PROJECT_ROOT / "faiss_index"
if FAISS_INDEX_PATH.exists():
    print(f"Loading FAISS index from {FAISS_INDEX_PATH}")
    vector_store = FAISS.load_local(
        str(FAISS_INDEX_PATH), embeddings, allow_dangerous_deserialization=True
    )
else:
    print("FAISS index not found. Run src/data/encode_json.py to create it.")
    vector_store = None

retriever = vector_store.as_retriever() if vector_store else None

print("Setting up message store...")
store = SQLAlchemyStore(os.getenv("DATABASE_URL", "sqlite:///langgraph_store.db"))

SUPERVISOR_PROMPT_PATH = Path(__file__).parent / "agents" / "prompts" / "supervisor.md"
SUPERVISOR_PROMPT = (
    SUPERVISOR_PROMPT_PATH.read_text(encoding="utf-8")
    if SUPERVISOR_PROMPT_PATH.exists()
    else ""
)

RESPONSE_PROMPT_PATH = Path(__file__).parent / "agents" / "prompts" / "response.md"
RESPONSE_PROMPT = (
    RESPONSE_PROMPT_PATH.read_text(encoding="utf-8")
    if RESPONSE_PROMPT_PATH.exists()
    else ""
)

WIKI_PROMPT_PATH = Path(__file__).parent / "agents" / "prompts" / "wiki.md"
WIKI_PROMPT = (
    WIKI_PROMPT_PATH.read_text(encoding="utf-8") if WIKI_PROMPT_PATH.exists() else ""
)

MESSAGE_HISTORY_LIMIT = int(
    os.getenv("MESSAGE_HISTORY_LIMIT", 6)
)  # Accounts for all messages, both user and AI, so 3 exchanges.

print("Configuration loaded successfully.")

if __name__ == "__main__":
    # Check how many documents are in the collection
    collection = vector_store._collection
    print(f"Documents in vector store: {collection.count()}")
