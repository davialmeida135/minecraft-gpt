from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.store.sqlite.aio import AsyncSqliteStore
from mcpq import Minecraft
from dotenv import load_dotenv
from pathlib import Path
import aiosqlite

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

async def get_async_stores():
    print("Setting up async stores...")
    conn = await aiosqlite.connect(PROJECT_ROOT / "langgraph_checkpoints.db")
    store = AsyncSqliteStore(conn)
    checkpointer = AsyncSqliteSaver(conn)
    await store.setup()
    print("Async stores set up.")
    return store, checkpointer

if __name__ == "__main__":
    # Check how many documents are in the collection
    collection = vector_store._collection
    print(f"Documents in vector store: {collection.count()}")
