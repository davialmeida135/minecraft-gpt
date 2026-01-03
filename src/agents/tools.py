from langchain.tools import tool
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.config import retriever

@tool
def minecraft_internet_search(term: str) -> str:
    """
    Minecraft Wiki search tool. 
    - On the term, input only the item/block name.
    - Always input in English.
    :param term: The search term for the Minecraft Wiki. Always in English.
    """

    url = f"https://minecraft.wiki/w/Special:Search?search={term.replace(' ', '+')}&go=Go"
    loader = WebBaseLoader(url)
    documents = loader.load()
    if len(documents) == 0:
        return "No relevant information found on the Minecraft Wiki."
    return documents[0].page_content.strip().replace("\n\n\n", "\n")[200:10000]  # Return a snippet of the content

# @tool
# def minecraft_recipe_search(query: str) -> str:
#     """
#     Docstring for minecraft_recipe_search
    
#     :param query: Description
#     :type query: str
#     :return: Description
#     :rtype: str
#     """
#     try:
#         print(f"Searching for: {query}")
#         docs = retriever.invoke(query)
#         print(f"Found {len(docs)} documents")
#         if not docs:
#             return "No recipes found for that query."
#         return "\n\n".join([doc.page_content for doc in docs])
#     except Exception as e:
#         print(f"Error during retrieval: {e}")
#         return f"Error searching recipes: {e}"

if __name__ == "__main__":
    # Example usage
    a = minecraft_internet_search.invoke({"query": "stone stone stone {}{}"})
    print(a)