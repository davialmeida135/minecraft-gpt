from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from mcpq import Minecraft
from dotenv import load_dotenv
from pathlib import Path
from src.agents.sqlalchemy_store import SQLAlchemyStore
import os

load_dotenv()

mc = Minecraft(host="192.168.9.132", port=14445)

llm = ChatOpenAI(model="gpt-4.1-nano")
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

PROJECT_ROOT = Path(__file__).parent.parent
CHROMA_DB_PATH = PROJECT_ROOT / "chroma_langchain_db"
print(str(CHROMA_DB_PATH))

vector_store = Chroma(
    collection_name="minecraft_items",
    embedding_function=embeddings,
    persist_directory=str(CHROMA_DB_PATH),
)
retriever = vector_store.as_retriever()

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

if __name__ == "__main__":
    # Check how many documents are in the collection
    collection = vector_store._collection
    print(f"Documents in vector store: {collection.count()}")
