from ddg import Duckduckgo
from ibm_watsonx_orchestrate.agent_builder.tools import tool, ToolPermission

@tool(name="duckduckgo_search", description="Tool to search the query over internet")
def search(query: str):
    ddg_api = Duckduckgo()
    results = ddg_api.search(query)
    if results["data"]:
        return results["data"]
    else:
        return "{}"

#if __name__ == '__main__':
#   search_result = search("show me available doctors for mental health in gurgaon")
#   print(search_result)