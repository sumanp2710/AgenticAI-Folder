from ibm_watsonx_orchestrate.agent_builder.tools import tool, ToolPermission

@tool(name="portfolio_retriever", description="Get user's portfolio", permission=ToolPermission.READ_ONLY)
def portfolio_retriever(user_name: str) -> str:
    """
    This tool fetches the user's portfolio based on the provided user name.
    Args:
        user_name (str): The name of the user whose portfolio is to be fetched.
    Returns:
        str: A string representation of the user's portfolio in a tabular format.
    """

    # Connection to DB2
    # TODO: Add Logic for connecting to DB2 and fetching the portfolio data

    mock_portfolio = """|   ID | Security Name    |   Market Value (USD) |   Y2Y % | Industry Sector   |
|-----:|:-----------------|---------------------:|--------:|:------------------|
|    1 | S&P 500          |              8500000 |      15 | Index Fund        |
|    2 | MSCI AC World    |              6000000 |      12 | Index Fund        |"""
    
    return mock_portfolio