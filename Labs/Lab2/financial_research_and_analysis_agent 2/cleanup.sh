#!/bin/bash
set -e
# This script cleans up the agent environment by removing the agent and its associated resources.
orchestrate tools remove --name portfolio_retriever
orchestrate tools remove --name transcript_retriever
orchestrate tools remove --name web_search

orchestrate knowledge-bases remove --name goldman_sachs_reports
orchestrate agents remove --name risk_assessment_agent --kind external

orchestrate connections remove --app-id tavily

orchestrate agents remove --name report_generator_agent --kind native
orchestrate agents remove --name financial_research_and_analysis_agent --kind native

orchestrate agents list
orchestrate knowledge-bases list
orchestrate tools list