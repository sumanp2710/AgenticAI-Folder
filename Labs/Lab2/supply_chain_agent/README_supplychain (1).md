# Supply Chain Agent

## Overview

This use case demonstrates how AI-powered agents can streamline end-to-end supply chain operations by handling domain-specific tasks and collaborating autonomously to achieve operational efficiency and business continuity.
At the planning stage, the Forecast Agent estimates product demand trends using historical data. This drives informed decisions for stock replenishment and production.
Simultaneously, the Inventory Agent evaluates stock levels, identifying shortages or surpluses and triggering replenishment tasks if needed. If new materials are required, the Procurement Agent negotiates purchases based on pricing logic and supplier policies.
The Logistics Agent handles routing and delivery schedules, ensuring cost-effective and timely distribution. Throughout this process, the Compliance Agent ensures all actions align with internal business rules and external regulations.
The Controller Agent serves as the central decision-maker, dynamically delegating tasks across agents based on the user's query or business trigger.


## The Problem

Traditional supply chain workflows are highly siloed, manual, and sequential. This leads to:
- ⏱️ Slow response times when demand changes
- ⚠️ Missed cost-saving opportunities due to poor procurement coordination
- 🚚 Inefficient routing and logistics delays
- 📉 High overhead in compliance reporting

As a result, enterprises face:
🔄 Disconnected planning across departments
🧾 Manual reviews for every adjustment or policy check
💸 Operational costs due to rework and poor visibility


## Key Components

- 🤖 1. Forecast Agent
Predicts future demand trends using historical data
Drives smarter procurement and production
- 📦 2. Inventory Agent
Continuously monitors stock levels
Raises restock alerts or triggers orders automatically
- 📥 3. Procurement Agent
Finds optimal vendors and initiates purchase orders
Supports dynamic price and volume negotiation logic
- 🚛 4. Logistics Agent
Plans distribution schedules and delivery routes
Simulates estimated arrival times
- ✅ 5. Compliance Agent
Checks if each action complies with internal/external policy
Prevents policy violations proactively

## Instructions for running the Notebook 

### 1. Clone the Repository
Clone the GitHub repository to your colab notebook.
```bash
!git clone https://github.com/sumanp2710/AgenticAI-Folder
```
### 2. List the contents of the directory to locate the necessary files.
```bash 
!ls AgenticAI-Folder/Labs/Lab2/supply_chain_agent
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

> <span style="color:red">⚠️</span> **Warning:** Before proceeding to step 5, ensure all code snippets for the agents and tools are filled in as outlined in the lab guide.


### 5. Import all the tools and agents using this shell script
```bash 
!chmod +x AgenticAI-Folder/Labs/Lab2/supply_chain_agent/import-all.sh
!./AgenticAI-Folder/Labs/Lab2/supply_chain_agent/import-all.sh
```


## Test your agent-

Use the controller agent to handle business queries such as:

- "Forecast sales for SKU001 for the next month"
- "We need to restock SKU001 and choose the best vendor."
- "Can you do a end to end planning for the upcoming cycle?"
- "Verify compliance of Supplier A with ESG norms."
