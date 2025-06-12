#!/bin/bash
set -e
# This script sets up the agent environment and installs necessary dependencies.

# Deploy the tools
orchestrate tools import -k python \
    -f "tools/get_nearest_service_center.py" \
    -r "tools/requirements.txt"

orchestrate tools import -k python \
    -f "tools/get_vehicle_telematics.py" \
    -r "tools/requirements.txt"

# Deploy the Knowledge
orchestrate knowledge-bases import -f knowledge_bases/knowledge.yaml

# Deploy the Agents
orchestrate agents import -f agents/vehicle_telematics.yaml
orchestrate agents import -f agents/agent.yaml

# List everything
orchestrate agents list
orchestrate knowledge-bases list
orchestrate tools list

# Start the UI
orchestrate chat start