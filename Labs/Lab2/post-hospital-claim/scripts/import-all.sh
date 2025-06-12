#!/usr/bin/env bash
set -x

## IMPORTING/UPDATING TOOLS 
pip install -r ../tools/common/requirements.txt
pip install -r ../tools/insurance/requirements.txt

orchestrate tools import -k python -f ../tools/common/pubsub.py -r ../tools/common/requirements.txt
orchestrate tools import -k python -f ../tools/common/authenticate.py -r ../tools/common/requirements.txt

for python_tool in common/create_service_now_incident.py common/get_my_service_now_incidents.py common/get_service_now_incident_by_number.py; do
  orchestrate tools import -k python -f ../tools/${python_tool} -r ../tools/common/requirements.txt --app-id service-now
done

for python_tool in insurance/get_healthcare_benefits.py insurance/search_healthcare_providers.py insurance/claim_validation_tools.py insurance/policy_adjudication_tools.py ; do
  orchestrate tools import -k python -f ../tools/${python_tool} -r ../tools/common/requirements.txt
done
sleep 0.5

## IMPORTING KNOWLDEGE
# orchestrate knowledge-bases remove --name health_insurance_generic_knowledge
orchestrate knowledge-bases import -f ../knowledge-base/health_insurance_faq.yaml
# orchestrate knowledge-bases patch -n health_insurance_generic_knowledge -f ../knowledge-base/health_insurance_faq.yaml
sleep 0.5


## IMPORTING/UPDATING AGENTS 

orchestrate agents import -f ../agents/service_now_agent.yaml 
orchestrate agents import -f ../agents/policy_adjudication_agent.yaml
orchestrate agents import -f ../agents/claim_intake_validation_agent.yaml
orchestrate agents import -f ../agents/frontend_conversational_agent.yaml

## OBSERVABILITY

# orchestrate settings observability langfuse configure --config-file=../observability/langfuse.yaml



