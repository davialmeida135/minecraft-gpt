import signal

from langchain.tools import tool
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import retriever, vector_store


@tool
def minecraft_internet_search(term: str) -> str:
    """
    Minecraft Wiki search tool.
    - On the term, input only the item/block name.
    - Always input in English.
    :param term: The search term for the Minecraft Wiki. Always in English.
    """

    url = (
        f"https://minecraft.wiki/w/Special:Search?search={term.replace(' ', '+')}&go=Go"
    )
    loader = WebBaseLoader(url)
    documents = loader.load()
    if len(documents) == 0:
        return "No relevant information found on the Minecraft Wiki."
    return documents[0].page_content.strip().replace("\n\n\n", "\n")[200:10000]


def minecraft_recipe_search(query: str) -> str:
    """
    Search for Minecraft recipes in the local vector store.

    :param query: The search query
    :type query: str
    :return: Recipe information or error message
    :rtype: str
    """
    try:
        print(f"Searching for: {query}")
        docs = retriever.invoke(query)
        print(f"Found {len(docs)} documents")
        if not docs:
            print("No documents found")
            return "No recipes found for that query."
        return "\n\n".join([doc.page_content for doc in docs])
    except Exception as e:
        print(f"Error during retrieval: {e}")
        return f"Error searching recipes: {e}"


if __name__ == "__main__":
    # First, check the vector store status
    print("=== Vector Store Diagnostics ===")
    try:
        if vector_store is None:
            print("\n⚠️  Vector store is not loaded!")
            print("Run: uv run python src/data/encode_json.py")
        else:
            print(f"\n✓ Vector store loaded successfully")

            # Try a simple similarity search
            print("\n=== Testing retriever ===")
            print("Attempting similarity search...")

            # Direct similarity search
            results = vector_store.similarity_search("pickaxe", k=2)
            print(f"Direct similarity search returned {len(results)} results")
            for i, doc in enumerate(results):
                print(f"  Doc {i}: {doc.page_content[:100]}...")

            # Test the retriever
            print("\n=== Testing retriever.invoke() ===")
            docs = retriever.invoke("diamond sword")
            print(f"Retriever returned {len(docs)} documents")
            for i, doc in enumerate(docs):
                print(f"  Doc {i}: {doc.page_content[:100]}...")

    except Exception as e:
        import traceback

        print(f"Error: {e}")
        traceback.print_exc()
