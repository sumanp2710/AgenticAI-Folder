#!/usr/bin/env bash
set -x

## REMOVING TOOLS 

for python_tool in get_healthcare_benefits search_healthcare_providers; do
  orchestrate tools remove -n ${python_tool}  
done

for python_tool in create_service_now_incident get_my_service_now_incidents get_service_now_incident_by_number; do
  orchestrate tools remove -n ${python_tool}
done

orchestrate tools remove -n process_claim_submission
orchestrate tools remove -n adjudicate_claim

## REMOVING KNOWLDEGE
orchestrate knowledge-bases remove --name health_insurance_generic_knowledge

## REMOVING AGENTS 

orchestrate agents remove -n service_now_agent -k native
orchestrate agents remove -n policy_benefits_adjudication -k native
orchestrate agents remove -n claim_intake_validation -k native
orchestrate agents remove -n frontend_conversational -k native




