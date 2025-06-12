from typing import Callable

from ibm_watsonx_ai import APIClient
from langchain_ibm import ChatWatsonx
from langgraph.graph.graph import CompiledGraph
from langgraph.prebuilt import create_react_agent

from risk_assessment_agent import TOOLS


def get_graph_closure(client: APIClient, model_id: str) -> Callable:
    """Graph generator closure."""

    # Initialise ChatWatsonx
    chat = ChatWatsonx(model_id=model_id, watsonx_client=client)

    risk_system_prompt = """
    You are a FINRA-certified financial risk analyst. Analyze investment portfolios for risk and output your findings in markdown table format:
    | Security Name | Market Value (USD) | Sector | Risk Level | Rationale |
    If the user gives random input, respond with "I am a financial risk analyst. Please provide a specific investment portfolio for analysis."
    Add a disclaimer at the end of each message: ">Disclaimer: This is an AI Generated response, use it with caution and do not make any financial decisions based on the results"
    """

    def get_graph(system_prompt=risk_system_prompt) -> CompiledGraph:
        return create_react_agent(
            chat, tools=TOOLS, state_modifier=system_prompt
        )

    return get_graph