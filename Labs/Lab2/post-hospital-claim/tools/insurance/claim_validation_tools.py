from enum import Enum
import re
import json
import time
from datetime import datetime
import logging
from typing import List, Optional

from pydantic import Field, BaseModel
# from enum import Enum

from ibm_watsonx_orchestrate.agent_builder.tools import tool, ToolPermission
# import requests

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Creating an object
logger = logging.getLogger()

# Setting the threshold of logger to DEBUG
logger.setLevel(logging.INFO)

# Mock Member Eligibility API
MOCK_MEMBER_ELIGIBILITY_DB = {
    "MEMBER123": {"active_on_2023-11-15": True, "plan_id": "PPO_GOLD"},
    "MEMBER456": {"active_on_2023-10-26": True, "plan_id": "HMO_SILVER"},
    "MEMBER789": {"active_on_2023-10-26": False, "plan_id": "PPO_BRONZE"}, # Inactive
}
def call_mock_member_eligibility_api(member_id: str, date_of_service: str) -> dict:
    """Simulates checking member eligibility."""
    logger.info(f"[MockMemberAPI] Checking eligibility for Member ID: {member_id} on {date_of_service}")
    time.sleep(0.3)
    key = f"active_on_{date_of_service}"
    member_info = MOCK_MEMBER_ELIGIBILITY_DB.get(member_id)
    if member_info and key in member_info:
        return {
            "status_code": 200,
            "body": {
                "member_id": member_id,
                "date_of_service": date_of_service,
                "is_eligible": member_info[key],
                "plan_id": member_info.get("plan_id")
            }
        }
    elif member_info and not member_info.get(key, False) : # Member found but not eligible on that date
         return {
            "status_code": 200,
            "body": {
                "member_id": member_id,
                "date_of_service": date_of_service,
                "is_eligible": False,
                "plan_id": member_info.get("plan_id"),
                "reason": "Not active on date of service"
            }
        }
    return {"status_code": 404, "body": {"message": "Member ID not found."}}


# Mock Provider Network API
MOCK_PROVIDER_NETWORK_DB = {
    "1234567890": {"plan_HMO_SILVER": "In-Network", "plan_PPO_GOLD": "Out-of-Network"}, # Dr. Carter
    "0987654321": {"plan_HMO_SILVER": "In-Network", "plan_PPO_GOLD": "In-Network"},   # Quest
    "1112223333": {"plan_HMO_SILVER": "Out-of-Network"},                             # Another Provider
}

def call_mock_provider_network_api(provider_npi: str, plan_id: str) -> dict:
    """Simulates checking provider network status."""
    logger.info(f"[MockProviderAPI] Checking network status for NPI: {provider_npi} with Plan: {plan_id}")
    time.sleep(0.3)
    provider_info = MOCK_PROVIDER_NETWORK_DB.get(provider_npi)
    plan_key = f"plan_{plan_id}"
    if provider_info and plan_key in provider_info:
        return {
            "status_code": 200,
            "body": {
                "provider_npi": provider_npi,
                "plan_id": plan_id,
                "network_status": provider_info[plan_key]
            }
        }
    elif provider_info: # Provider known, but not for that plan
        return {
            "status_code": 200, # It's not an error per se, just not in network for THAT plan
            "body": {
                "provider_npi": provider_npi,
                "plan_id": plan_id,
                "network_status": "Not Found for Plan" # Or a default like "Out-of-Network"
            }
        }
    return {"status_code": 404, "body": {"message": "Provider NPI not found."}}

@tool
def check_eligibility(member_id: str, date_of_service: str) -> tuple[bool, dict | None, str | None]:
    """
    Verifies member eligibility for the claim processing.

    :param member_id: member_id in insurance documents
    :param date_of_service: Date of service

    :returns: (is_eligible_api_success, eligibility_data, error_message)
    eligibility_data itself will contain an 'is_eligible' boolean.
    """
    logger.info(f"[MemberEligibilityTool] Checking eligibility for Member: {member_id}, DOS: {date_of_service}")
    if not member_id or not date_of_service:
        return False, None, "Member ID and Date of Service are required for eligibility check."
    response = call_mock_member_eligibility_api(member_id, date_of_service)
    if response["status_code"] == 200:
        return True, response["body"], None
    else:
        return False, None, response["body"].get("message", "Eligibility check failed.")
    
@tool
def check_network_status(provider_npi: str, plan_id: str) -> tuple[bool, dict | None, str | None]:
    """
    Checks provider network status for the service taken

    Parameters:
    - provider_npi: Service provider's network id
    - plan_id: Member's insurance policy plan

    :returns: (api_success, network_data, error_message)
    network_data will contain 'network_status'.
    """
    logger.info(f"[ProviderNetworkTool] Checking NPI: {provider_npi} for Plan: {plan_id}")
    if not provider_npi or not plan_id:
        return False, None, "Provider NPI and Plan ID are required for network check."
    response = call_mock_provider_network_api(provider_npi, plan_id)
    if response["status_code"] == 200:
        return True, response["body"], None
    else:
        return False, None, response["body"].get("message", "Provider network check failed.")
    
@tool
def validate_claim_data(claimInfo: str) -> tuple[bool, list[str]]:
    """
    Performs basic validation on structured claim data.

    Parameters:
    - claimInfo: Dict with following fields:
        - member_id: Member Id (required field)
        - patient_name: Patient's name (required field)
        - services: List of services taken, each with:
            - 'date_of_service'
            - 'cpt_code'
            - 'icd_10_code'
            - 'provider_npi'
            - 'charge_amount'

    :returns: (is_valid, structured_claim_data, list_of_errors_or_messages)
    """
    logger.info("[BasicValidationRulesTool] Performing basic validation rules.")

    try:
        structured_claim_data: dict = json.loads(claimInfo)        
    except json.JSONDecodeError as e:
        logger.info("Error decoding JSON:", e)

    errors = []
    if not structured_claim_data:
        errors.append("No structured claim data provided.")
        return False, errors

    # Validate top-level info
    if not structured_claim_data.get("member_id"):
        errors.append("Missing Member ID in extracted data.")

    claim_lines = structured_claim_data.get("services", [])
    if not claim_lines:
        errors.append("No service lines found in extracted data.")

    for i, line in enumerate(claim_lines):
        line_num = i + 1
        if not line.get("date_of_service"):
            errors.append(f"Line {line_num}: Missing Date of Service.")
        else:
            try:
                datetime.strptime(line["date_of_service"], "%Y-%m-%d")
            except ValueError:
                errors.append(f"Line {line_num}: Invalid Date of Service format (expected YYYY-MM-DD).")

        if not line.get("cpt_code"):
            errors.append(f"Line {line_num}: Missing CPT code.")
        if not line.get("provider_npi"):
            errors.append(f"Line {line_num}: Missing Provider NPI.")
        if line.get("charge_amount") is None or not isinstance(line.get("charge_amount"), (int, float)) or line.get("charge_amount") < 0:
            errors.append(f"Line {line_num}: Missing or invalid charge amount (must be a non-negative number).")
        # ICD-10 might be optional depending on rules, or sometimes required.
        # if not line.get("icd_10_code"):
        #     errors.append(f"Line {line_num}: Missing ICD-10 code.")

    return not errors, structured_claim_data, errors

# @tool
# def process_claim_submission(claimInfo: str) -> tuple[bool, dict | None, list[str]]:
#     """
#     Claim processing method to initiate claim intake and validation process. This tool is used to validate the claim submission.

#     Parameters:
#     - claimInfo: Dict with following fields:
#         - member_id: Member Id (required field)
#         - patient_name: Patient's name (required field)
#         - services: List of services taken, each with:
#             - 'date_of_service'
#             - 'cpt_code'
#             - 'icd_10_code'
#             - 'provider_npi'
#             - 'charge_amount'

#     :returns: (overall_success, validated_claim_data, list_of_errors_or_messages)
#     """
#     logger.info(f"\n[CIVA] Received new claim submission. claimInfo: {claimInfo}")
#     errors = []

#     try:
#         processed_claim_data: dict = json.loads(claimInfo)        
#     except json.JSONDecodeError as e:
#         logger.info("Error decoding JSON:", e)
  
#     # processed_claim_data = claimInfo.model_dump()
#     # 3. Basic Validation Rules
#     is_structurally_valid, validation_errors = _validate_claim_data(processed_claim_data)
#     if not is_structurally_valid:
#         errors.extend(validation_errors)
#         # Decide if we stop here or continue with API checks if some data is present
#         # For this example, we'll stop if structural validation fails badly.
#         logger.info(f"[CIVA] Basic validation failed: {validation_errors}")
#         return False, processed_claim_data, errors
#     logger.info("[CIVA] Basic data structure validation passed.")

#     # 4. Member Eligibility Check (using extracted Member ID and DOS)
#     # Assume member_id and DOS are consistent per claim, or take from first line if varies.
#     # Real system needs to handle multiple DOS or members in one submission if allowed.
#     member_id = processed_claim_data.get("member_id")
#     # For simplicity, take DOS from the first line if available globally or per line.
#     dos_to_check = processed_claim_data.get("services")[0].get("date_of_service") if processed_claim_data.get("services") else None

#     if member_id and dos_to_check:
#         elig_api_ok, elig_data, elig_error = _check_eligibility(member_id, dos_to_check)
#         if not elig_api_ok:
#             errors.append(f"Eligibility API call failed: {elig_error}")
#         elif elig_data and not elig_data.get("is_eligible"):
#             errors.append(f"Member {member_id} not eligible on {dos_to_check}. Reason: {elig_data.get('reason', 'Not specified')}")
#             # This is a major validation failure for the claim.
#             return False, processed_claim_data, errors
#         elif elig_data: # Eligible
#             processed_claim_data["member_eligibility"] = elig_data
#             logger.info(f"[CIVA] Member {member_id} is eligible. Plan ID: {elig_data.get('plan_id')}")
#         else: # Should not happen if elig_api_ok is True without data
#             errors.append("Eligibility check inconclusive.")
#     else:
#         errors.append("Missing Member ID or Date of Service for eligibility check.")
#         # This might be a hard stop depending on rules.
#         return False, processed_claim_data, errors

#     # 5. Provider Network Check (for each provider NPI on each line)
#     plan_id = processed_claim_data.get("member_eligibility", {}).get("plan_id")
#     if not plan_id:
#         errors.append("Cannot check provider network status without Plan ID from eligibility.")
#     else:
#         for line in processed_claim_data.get("services", []):
#             npi = line.get("provider_npi")
#             if npi:
#                 net_api_ok, net_data, net_error = _check_network_status(npi, plan_id)
#                 if not net_api_ok:
#                     errors.append(f"Network check API call failed for NPI {npi}: {net_error}")
#                     line["network_status"] = "Error checking status"
#                 elif net_data:
#                     line["network_status"] = net_data.get("network_status")
#                     logger.info(f"[CIVA] Provider NPI {npi} network status: {line['network_status']}")
#                 else:
#                     line["network_status"] = "Unknown"
#             else:
#                 errors.append(f"Line with CPT {line.get('cpt_code')} missing Provider NPI for network check.")
#                 line["network_status"] = "Missing NPI"


#     if errors:
#         logger.info(f"[CIVA] Validation completed with errors: {errors}")
#         return False, processed_claim_data, errors

#     logger.info("[CIVA] All intake and validation checks passed successfully.")
#     return True, processed_claim_data, ["Validation successful."]


# # ---- Example Usage ----
# if __name__ == "__main__":
#     # --- Example Claim Data (output from FCA) ---
#     fca_output_claim_1 = {
#         "member_id": "MEMBER789",
#         "patient_name": "Carol Danvers",
#         "services": [
#             {
#                 "date_of_service": "2023-10-26",
#                 "cpt_code": "99203",
#                 "icd_10_code": "R07.9", # Chest pain
#                 "provider_npi": "1112223333",
#                 "charge_amount": 150.00
#             }
#         ]
#     }
#     logger.info("\n--- Scenario 1: Standard Claim  ---")
#     success, processed_claim_data, messages_1 = process_claim_submission(submission_type='structured', claim_info=fca_output_claim_1)

#     logger.info(f"\nCIVA Scenario1 Final Status: {'Success' if success else 'Failed'}")
#     logger.info(f"Messages: {messages_1}")

#     fca_output_claim_2 = {
#         "member_id": "MEMBER456",
#         "patient_name": "Sarah Member",
#         "services": [
#             {
#                 "date_of_service": "2023-10-26",
#                 "cpt_code": "99214",
#                 "icd_10_code": "M54.5",
#                 "provider_npi": "1234567890",
#                 "charge_amount": 250.0
#             },
#             {
#                 "date_of_service": "2023-10-26",
#                 "cpt_code": "80053",
#                 "provider_npi": "0987654321",
#                 "charge_amount": 120.0
#             }
#         ]
#     }
#     logger.info("\n--- Scenario 2: Standard Claim  ---")
#     success, processed_claim_data, messages_2 = process_claim_submission(submission_type='structured', claim_data=fca_output_claim_2)

#     logger.info(f"\nCIVA Scenario 2 Final Status: {'Success' if success else 'Failed'}")
#     logger.info(f"Messages: {messages_2}")
    