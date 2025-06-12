from langchain_core.tools import tool
from tavily import TavilyClient

@tool("search", parse_docstring=True)
def web_search(query: str) -> list[str]:
    """
    Search the web for a security's market value concentration, sector exposure, asset volatility, and diversification.

    Args:
        query: User query to search in web.

    Returns:
        list: list of web search results.
    """
    tavily_client = TavilyClient(api_key="API_KEY_HERE")  # Replace with your Tav
    response = tavily_client.search(query=query, max_results=5, include_answer=True)
    return response