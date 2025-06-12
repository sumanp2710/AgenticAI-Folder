#!/bin/bash

# List of tool files to import
TOOL_FILES=(
    "tools/customer_info.py"
    "tools/get_network_hospitals.py"
    "tools/policy_info.py"
    "tools/read_email.py"
    "tools/send_email.py"
    "tools/calculate_preauth_amount.py"
)

TOOL_FILES_SN=(
    "tools/create_service_now_incident.py"
)

# Common requirements file
REQUIREMENTS="tools/requirements.txt"

# Import each tool
for tool_file in "${TOOL_FILES[@]}"; do
    echo "Importing $tool_file..."
    orchestrate tools import -k python \
        -f "$tool_file" \
        -r "$REQUIREMENTS"
    
    # Add a small delay if needed between imports
    sleep 1
done

for tool_file_sn in "${TOOL_FILES_SN[@]}"; do
    echo "Importing $tool_file..."
    orchestrate tools import -k python \
        -f "$tool_file_sn" \
        -r "$REQUIREMENTS" \
        --app-id service-now
    
    # Add a small delay if needed between imports
    sleep 1
done

echo "All tools imported successfully."