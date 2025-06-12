#!/bin/bash

# List of agent files to import
AGENT_FILES=(
    "agents/service_now_agent.yaml"
    "agents/claim_adjudication_agent.yaml"
    "agents/claim_intake_validation_agent.yaml"
    "agents/claim_process_support_agent.yaml"
    "agents/policy_support_agent.yaml"
    "agents/claim_report_agent.yaml"
    "agents/claim_support_desk_agent.yaml"
    "agents/claim_analyst_agent.yaml"
)

# Import each agent
for agent_file in "${AGENT_FILES[@]}"; do
    echo "Importing $agent_file..."
    orchestrate agents import -f "$agent_file"
    
    # Add a small delay between imports if needed
    sleep 1
done

echo "All agents imported successfully."