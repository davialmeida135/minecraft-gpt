from langchain_community.document_loaders import JSONLoader
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from dotenv import load_dotenv

load_dotenv()


def encode_items_to_vector_store():
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    vector_store = Chroma(
        collection_name="minecraft_items",
        embedding_function=embeddings,
        persist_directory="./chroma_langchain_db",
    )

    loader = JSONLoader(
        file_path="data/raw/items.json",
        jq_schema=".[]",  # Adjust based on your JSON structure
        text_content=False,  # Allow dict content to be serialized as string
    )

    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    splits = splitter.split_documents(documents)

    # Add to vector store
    vector_store.add_documents(splits)
    print(f"Added {len(splits)} document chunks to vector store")


if __name__ == "__main__":
    encode_items_to_vector_store()
