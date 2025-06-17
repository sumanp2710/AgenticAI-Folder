# Vehicle troubleshooting Assistant

## Overview

The Vehicle Troubleshooting Assistant is an AI Agent designed to help car owners identify and understand vehicle issues by interpreting natural language inputs like “My car is shaking” or “Check engine light is on.”
It combines real-time telematics data, diagnostic trouble codes (DTCs), and vehicle documentation to offer personalized, accurate diagnostics and actionable guidance such as finding nearby service centers, etc.


## Key Components

- Telematics data analyzer agent (External Agent) – Get the car telematics data and analyze it to provide a natural language summary
- Get Telematics data (Tool) – Get the telematics data of a car. (simulation)
- Get nearest service center (Tool) – Get the nearest service center. (takes lat & lon and gives results)
- Troubleshoot agent (Native wxO Agent) – A supervisor agent that orchestrate between the following:
    1. Knowledge (RAG):
        a. DTC code list.pdf
        b. Car user manual.pdf
    2. Toolset:
        a. Agents:
            i. Telematics data analyzer agent
        b. Tools:
            i. Get nearest service center

## Benefits

- **Customer Experience:** Reduces stress for drivers by providing instant, understandable insights.
- **Service Optimization:** Reduces unnecessary service visits and helps service centers prioritize real issues.
- **Brand Loyalty:** Builds trust by offering proactive, intelligent support post-purchase.
- **Data Utilization:** Leverages telematics data and DTC documentation to deliver accurate, data-driven support.
- **Scalability:** Easily extendable across vehicle models, regions, and support channels (mobile app, web, IVR).


## Instructions for running the Notebook 

### 1. Clone the Repository
Clone the GitHub repository to your colab notebook.
```bash
!git clone https://github.com/sumanp2710/AgenticAI-Folder
```
### 2. List the contents of the directory to locate the necessary files.
```bash 
!ls AgenticAI-Folder/Labs/Lab1/vehicle_maintenance_agent
```

### 3. Install the required Python package (ibm_watsonx_orchestrate).
```bash 
!pip install ibm_watsonx_orchestrate
```
### 4. Add your environment to Orchestrate using your specific URL and API key.
```bash 
!orchestrate env add --name bootcamp --url <YOUR_URL> -t ibm_iam
!orchestrate env activate bootcamp --apikey <YOUR_API_KEY>
```
### 5. Import Python scripts and their dependencies into the environment.
```bash 
!orchestrate tools import -k python -f "/content/AgenticAI-Folder/Labs/Lab1/vehicle_maintenance_agent/tools/get_nearest_service_center.py" -r "/content/AgenticAI-Folder/Labs/Lab1/vehicle_maintenance_agent/tools/requirements.txt"
!orchestrate tools import -k python -f "/content/AgenticAI-Folder/Labs/Lab1/vehicle_maintenance_agent/tools/get_vehicle_telematics.py" -r "/content/AgenticAI-Folder/Labs/Lab1/vehicle_maintenance_agent/tools/requirements.txt"
```
### 6. Import the knowledge base YAML file into the environment.
```bash 
!orchestrate knowledge-bases import -f /content/AgenticAI-Folder/Labs/Lab1/vehicle_maintenance_agent/knowledge_bases/knowledge.yaml
```
### 7. Import the agent YAML file into the environment.
```bash 
!orchestrate agents import -f /content/AgenticAI-Folder/Labs/Lab1/vehicle_maintenance_agent/agents/vehicle_telematics.yaml
```

## Test examples

1. “What does the engine temperature warning light mean?” -> Troubleshoot agent will use the Knowledge base to RAG and answer this query
2. “My car is shaking and I have the engine temperature warning light on can you diagnose it?” -> Troubleshoot agent will transfer the control to Telematics data analyzer agent which will ask follow-up questions if required and give a car health report. The car report is read, and a suggestion is provided by the Troubleshoot agent.
3. “Where is the nearest service center to me?” -> Troubleshoot agent will invoke the Get nearest service center tool and pass the lat & long received from the Telematics data analyzer agent (assumption is that car will send the current lat & long data as part of telematics data.) and get the nearest service centers from the list of service centers.
