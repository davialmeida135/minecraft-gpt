import sys
import traceback
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.document_loaders import JSONLoader
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

# Use absolute paths based on project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
FAISS_INDEX_PATH = PROJECT_ROOT / "faiss_index"
ITEMS_JSON_PATH = PROJECT_ROOT / "data" / "raw" / "items.json"


def encode_items_to_vector_store():
    print(f"Loading items from: {ITEMS_JSON_PATH}")
    print(f"Saving FAISS index to: {FAISS_INDEX_PATH}")

    if not ITEMS_JSON_PATH.exists():
        print(f"ERROR: {ITEMS_JSON_PATH} does not exist!")
        return

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    loader = JSONLoader(
        file_path=str(ITEMS_JSON_PATH),
        jq_schema=".[]",
        text_content=False,
    )

    documents = loader.load()
    print(f"Loaded {len(documents)} documents from JSON")

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    splits = splitter.split_documents(documents)
    print(f"Split into {len(splits)} chunks")

    # Test embedding with a single document first
    print("Testing embedding with a single document...")

    # Create FAISS index from documents
    print("Creating FAISS index from all documents...")
    try:
        vector_store = FAISS.from_documents(splits, embeddings)
        print(f"✓ FAISS index created with {len(splits)} documents")
    except Exception as e:
        print(f"✗ FAISS index creation failed: {e}")
        traceback.print_exc()
        return

    # Save the index locally
    print(f"Saving FAISS index to {FAISS_INDEX_PATH}...")
    try:
        vector_store.save_local(str(FAISS_INDEX_PATH))
        print("✓ FAISS index saved successfully!")
    except Exception as e:
        print(f"✗ Failed to save FAISS index: {e}")
        traceback.print_exc()
        return
    
    print("Done!")


if __name__ == "__main__":
    encode_items_to_vector_store()
