from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from mcpq import Minecraft
from dotenv import load_dotenv
from pathlib import Path
from src.agents.sqlalchemy_store import SQLAlchemyStore

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

store = SQLAlchemyStore("sqlite:///langgraph_store.db")

if __name__ == "__main__":
    # Check how many documents are in the collection
    collection = vector_store._collection
    print(f"Documents in vector store: {collection.count()}")
