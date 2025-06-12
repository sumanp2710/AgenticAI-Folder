#!/bin/bash
set -e
# This script sets up the agent environment and installs necessary dependencies.

# Deploy the tools
orchestrate tools import -k python -f "tools/portfolio_retriever_tool/portfolio_retriever.py" -r "tools/portfolio_retriever_tool/requirements.txt"

orchestrate tools import -k python -f "tools/transcript_retriever_tool/transcript_retriever.py" -r "tools/transcript_retriever_tool/requirements.txt"

orchestrate connections add -a tavily
orchestrate connections configure --app-id tavily --environment draft -t team -k key_value
orchestrate connections set-credentials --app-id=tavily --env draft -e TAVILY_API_KEY="your_tavily_api_key_here"

orchestrate tools import -k python -f "tools/web_search_tool/web_search.py" -r "tools/web_search_tool/requirements.txt" --app-id tavily


# Deploy the Knowledge
orchestrate knowledge-bases import -f knowledge_bases/knowledge.yaml

# Define external agents
orchestrate agents import -f collaborators/external_agent.yaml

# Deploy the Agents
orchestrate agents import -f agents/report_generator_agent.yaml
orchestrate agents import -f agents/agent.yaml

# List everything
orchestrate agents list
orchestrate knowledge-bases list
orchestrate tools list