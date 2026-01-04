import signal

from langchain.tools import tool
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import retriever, vector_store


@tool
def minecraft_internet_search(query: str) -> str:
    """
    Minecraft Wiki search tool.
    - On the query, input only the item/block name.
    - Always input in English.
    :param query: The search query for the Minecraft Wiki. Always in English.
    """

    url = (
        f"https://minecraft.wiki/w/Special:Search?search={query.replace(' ', '+')}&go=Go"
    )
    loader = WebBaseLoader(url)
    documents = loader.load()
    if len(documents) == 0:
        return "No relevant information found on the Minecraft Wiki."
    
    response = f"""Top search result from Minecraft Wiki for '{query}':
    \n\n{documents[0].page_content.strip().replace('\n\n\n', '\n')[300:8000]}"""

    return response

@tool
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
        
        recipes = "\n\n".join([doc.page_content for doc in docs])
        response = f"""
        Here are the candidate recipes I found:\n
        {recipes}
        """

        return response.strip()
    
    except Exception as e:
        print(f"Error during retrieval: {e}")
        return f"Error searching recipes: {e}"


if __name__ == "__main__":
    # First, check the vector store status
    print("=== Vector Store Diagnostics ===")
    try:
            # Test the retriever
            print("\n=== Testing retriever.invoke() ===")
            docs = minecraft_recipe_search.invoke("piston")
            print(f"Retriever returned {len(docs)} documents")
            print(docs)

    except Exception as e:
        import traceback

        print(f"Error: {e}")
        traceback.print_exc()
