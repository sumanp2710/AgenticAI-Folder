import json
import time
from datetime import datetime
import logging
# from enum import Enum

from ibm_watsonx_orchestrate.agent_builder.tools import tool, ToolPermission
# import requests

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Creating an object
logger = logging.getLogger()

# Setting the threshold of logger to DEBUG
logger.setLevel(logging.INFO)


# ---- MOCK EXTERNAL DATABASES / APIs ----

# Mock Policy Definitions
MOCK_POLICY_DB = {
    "HMO_SILVER": {
        "plan_year": 2023,
        "deductible_individual": 1500.00,
        "deductible_family": 3000.00,
        "oop_max_individual": 5000.00,
        "oop_max_family": 10000.00,
        "benefits": {
            "SpecialistVisit_InNetwork": {"copay": 50, "applies_to_deductible": False, "coinsurance": 0.0}, # Copay only
            "SpecialistVisit_OutOfNetwork": {"deductible_applies": True, "coinsurance": 0.4}, # 40% after ded
            "Lab_InNetwork": {"copay": 10, "applies_to_deductible": False, "coinsurance": 0.0}, # Copay only
            "Lab_OutOfNetwork": {"deductible_applies": True, "coinsurance": 0.4},
            "Inpatient_InNetwork": {"deductible_applies": True, "coinsurance": 0.2}, # 20% after ded
            "Default_InNetwork": {"deductible_applies": True, "coinsurance": 0.2}, # Default rule
            "Default_OutOfNetwork": {"deductible_applies": True, "coinsurance": 0.4},
        }
    },
    "PPO_GOLD": {
         "plan_year": 2023,
        "deductible_individual": 500.00,
        "deductible_family": 1000.00,
        "oop_max_individual": 3000.00,
        "oop_max_family": 6000.00,
        "benefits": {
            "SpecialistVisit_InNetwork": {"deductible_applies": True, "coinsurance": 0.1}, # 10% after ded
            "SpecialistVisit_OutOfNetwork": {"deductible_applies": True, "coinsurance": 0.3}, # 30% after ded
            "Lab_InNetwork": {"copay": 0, "applies_to_deductible": False, "coinsurance": 0.0}, # Covered 100%
            "Lab_OutOfNetwork": {"deductible_applies": True, "coinsurance": 0.3},
            "Default_InNetwork": {"deductible_applies": True, "coinsurance": 0.1},
            "Default_OutOfNetwork": {"deductible_applies": True, "coinsurance": 0.3},
        }
    }
}

# Mock Accumulators (Needs to be mutable!) - Keyed by member_id + benefit_year
MOCK_ACCUMULATORS_DB = {
    "MEMBER456_2023": {"deductible_met_individual": 200.00, "oop_max_met_individual": 350.00},
    "MEMBER123_2023": {"deductible_met_individual": 0.00, "oop_max_met_individual": 50.00},
    # Add family accumulators if needed
}

# Mock Pre-Authorization Database
MOCK_PRE_AUTH_DB = {
    "MEMBER456_99214_M54.5": {"required": False}, # Specialist visit for back pain
    "MEMBER456_80053_M54.5": {"required": False}, # Lab panel for back pain
    "MEMBER123_64493_M54.5": {"required": True, "status": "Approved", "auth_number": "PA12345"}, # Specific injection
    "MEMBER123_64494_G56.0": {"required": True, "status": "Missing"}, # Another procedure, auth missing
}

# Mock Coverage Guidelines (Very Simplified)
MOCK_COVERAGE_GUIDELINES = {
    "99214_M54.5": "Generally Payable", # Specialist visit for low back pain
    "80053_M54.5": "Generally Payable", # Basic lab panel
    "12345_X99.9": "Requires Review - Experimental Code",
    "64493_M54.5": "Payable with PreAuth",
    "64494_G56.0": "Payable with PreAuth"
}

# --- Mock API Call Functions ---
def call_mock_policy_api(plan_id: str) -> dict:
    logger.info(f"[MockPolicyAPI] Fetching policy details for Plan ID: {plan_id}")
    time.sleep(0.2)
    policy = MOCK_POLICY_DB.get(plan_id)
    if policy:
        return {"status_code": 200, "body": policy}
    return {"status_code": 404, "body": {"message": f"Policy '{plan_id}' not found."}}

def call_mock_accumulator_api_get(member_id: str, benefit_year: int) -> dict:
    key = f"{member_id}_{benefit_year}"
    logger.info(f"[MockAccumulatorAPI] Fetching accumulators for: {key}")
    time.sleep(0.2)
    accumulators = MOCK_ACCUMULATORS_DB.get(key)
    if accumulators:
        return {"status_code": 200, "body": accumulators.copy()} # Return a copy
    # Return default if not found (assuming new member or year start)
    return {"status_code": 200, "body": {"deductible_met_individual": 0.0, "oop_max_met_individual": 0.0}}

def call_mock_accumulator_api_update(member_id: str, benefit_year: int, updates: dict) -> dict:
    key = f"{member_id}_{benefit_year}"
    logger.info(f"[MockAccumulatorAPI] Updating accumulators for: {key} with {updates}")
    time.sleep(0.2)
    if key not in MOCK_ACCUMULATORS_DB:
        MOCK_ACCUMULATORS_DB[key] = {"deductible_met_individual": 0.0, "oop_max_met_individual": 0.0}

    # In reality, this would be atomic and handle concurrency
    MOCK_ACCUMULATORS_DB[key]["deductible_met_individual"] += updates.get("deductible_applied", 0.0)
    MOCK_ACCUMULATORS_DB[key]["oop_max_met_individual"] += updates.get("oop_applied", 0.0)

    logger.info(f"[MockAccumulatorAPI] New accumulator state for {key}: {MOCK_ACCUMULATORS_DB[key]}")
    return {"status_code": 200, "body": {"message": "Accumulators updated successfully."}}


def call_mock_preauth_api(member_id: str, cpt_code: str, diagnosis_code: str) -> dict:
    key = f"{member_id}_{cpt_code}_{diagnosis_code}"
    logger.info(f"[MockPreAuthAPI] Checking pre-auth for: {key}")
    time.sleep(0.2)
    auth_info = MOCK_PRE_AUTH_DB.get(key)
    if auth_info:
        return {"status_code": 200, "body": auth_info}
    # Default: Not required if not found in DB (safer default)
    return {"status_code": 200, "body": {"required": False}}

def call_mock_guidelines_api(cpt_code: str, diagnosis_code: str) -> dict:
    key = f"{cpt_code}_{diagnosis_code}"
    logger.info(f"[MockGuidelinesAPI] Checking guidelines for: {key}")
    time.sleep(0.1)
    status = MOCK_COVERAGE_GUIDELINES.get(key, "Requires Review - Unknown Code Combo")
    return {"status_code": 200, "body": {"coverage_status": status}}


# ---- PBAA's TOOLS ----

class CorePolicySystemAPIClient:
    def get_member_policy_details(self, plan_id: str) -> tuple[bool, dict | None, str | None]:
        logger.info(f"[CorePolicyClient] Getting policy details for Plan: {plan_id}")
        response = call_mock_policy_api(plan_id)
        if response["status_code"] == 200:
            return True, response["body"], None
        return False, None, response["body"].get("message", "Failed to retrieve policy details.")

    def get_member_accumulators(self, member_id: str, benefit_year: int) -> tuple[bool, dict | None, str | None]:
        logger.info(f"[CorePolicyClient] Getting accumulators for Member: {member_id}, Year: {benefit_year}")
        response = call_mock_accumulator_api_get(member_id, benefit_year)
        if response["status_code"] == 200:
            return True, response["body"], None
        return False, None, response["body"].get("message", "Failed to retrieve accumulators.")

    def update_member_accumulators(self, member_id: str, benefit_year: int, deductible_applied_total: float, oop_applied_total: float) -> tuple[bool, str | None]:
        logger.info(f"[CorePolicyClient] Updating accumulators for Member: {member_id}, Year: {benefit_year}")
        if deductible_applied_total > 0 or oop_applied_total > 0:
             updates = {
                "deductible_applied": deductible_applied_total,
                "oop_applied": oop_applied_total
             }
             response = call_mock_accumulator_api_update(member_id, benefit_year, updates)
             if response["status_code"] == 200:
                 return True, None
             return False, response["body"].get("message", "Failed to update accumulators.")
        else:
            logger.info("[CorePolicyClient] No accumulator updates needed.")
            return True, "No updates needed." # Considered success if no change needed


class PreAuthorizationDBClient:
    def check_pre_auth_status(self, member_id: str, cpt_code: str, diagnosis_code: str) -> tuple[bool, dict | None, str | None]:
        logger.info(f"[PreAuthClient] Checking PreAuth for Member: {member_id}, CPT: {cpt_code}, ICD: {diagnosis_code}")
        if not all([member_id, cpt_code, diagnosis_code]): # Basic check
             return False, None, "Missing required fields for pre-auth check (MemberID, CPT, ICD10)."
        response = call_mock_preauth_api(member_id, cpt_code, diagnosis_code)
        if response["status_code"] == 200:
            return True, response["body"], None
        return False, None, response["body"].get("message", "Failed to check pre-authorization.")

class MedicalGuidelinesTool:
    def check_coverage_guidelines(self, cpt_code: str, diagnosis_code: str) -> tuple[bool, dict | None, str | None]:
        logger.info(f"[GuidelinesTool] Checking Guidelines for CPT: {cpt_code}, ICD: {diagnosis_code}")
        if not all([cpt_code, diagnosis_code]):
            return False, None, "Missing CPT or ICD10 for guideline check."
        response = call_mock_guidelines_api(cpt_code, diagnosis_code)
        if response["status_code"] == 200:
            return True, response["body"], None
        return False, None, response["body"].get("message", "Failed to check coverage guidelines.")


class BenefitsEngineTool:
    def get_benefit_rule(self, service_type_key: str, policy_benefits: dict, network_status: str) -> dict:
        """Helper to find the specific benefit rule, falling back to default."""
        # Construct specific key first (e.g., SpecialistVisit_InNetwork)
        specific_key = f"{service_type_key}_{network_status}"
        if specific_key in policy_benefits:
            return policy_benefits[specific_key]

        # Fallback to default for the network status
        default_key = f"Default_{network_status}"
        if default_key in policy_benefits:
            logger.info(f"[BenefitsEngine] Warning: No specific rule for '{specific_key}', using default '{default_key}'.")
            return policy_benefits[default_key]

        # Ultimate fallback (should not happen with good policy definitions)
        logger.info(f"[BenefitsEngine] Error: No benefit rule found for '{specific_key}' or default '{default_key}'.")
        return {"copay": 0, "deductible_applies": True, "coinsurance": 1.0} # Default to 100% member resp if no rule

    def adjudicate_claim_line(self, claim_line: dict, policy_details: dict, current_accumulators: dict) -> dict:
        """
        Adjudicates a single claim line based on policy and accumulators.
        Returns a dictionary with calculated amounts for the line.
        IMPORTANT: This MUTATES current_accumulators for the next line within the same claim.
        """
        logger.info(f"[BenefitsEngine] Adjudicating Line - CPT: {claim_line.get('cpt_code')}, Charge: {claim_line.get('charge_amount')}")

        results = {
            "line_status": "Processing",
            "allowed_amount": 0.0, # In real system, this comes from fee schedules based on network
            "copay_applied": 0.0,
            "deductible_applied": 0.0,
            "coinsurance_member_owes": 0.0,
            "member_responsibility": 0.0,
            "insurer_payment": 0.0,
            "notes": [],
            "applied_to_deductible_this_line": 0.0, # How much accumulators should increase
            "applied_to_oop_max_this_line": 0.0,
        }

        # --- Basic Setup ---
        charge_amount = claim_line.get("charge_amount", 0.0)
        network_status = claim_line.get("network_status", "Unknown")
        if network_status not in ["In-Network", "Out-of-Network"]:
            results["notes"].append(f"Warning: Network status '{network_status}' treating as Out-of-Network.")
            network_status = "Out-of-Network"

        # ** Allowed Amount Determination (Simplified) **
        # Real system: Look up fee schedule based on CPT, modifiers, provider contract, network status.
        # Here, we'll naively use the charge amount, maybe with a small reduction for OON.
        if network_status == "In-Network":
            results["allowed_amount"] = charge_amount # Assume charge equals allowed for simplicity
        else:
            results["allowed_amount"] = charge_amount * 0.8 # Example: Allow 80% of charge for OON
        allowed = results["allowed_amount"]
        remaining_allowed = allowed # Amount left to apply benefits to

        # --- Get Policy Rules ---
        # Need to map CPT/service type to policy keys (e.g., "SpecialistVisit", "Lab")
        # Simplified mapping for this example:
        service_type_key = "Default"
        cpt = claim_line.get("cpt_code")
        if cpt in ["99213", "99214", "99203", "99204"]: service_type_key = "SpecialistVisit" # Assuming these are specialist
        if cpt in ["80053", "80048"]: service_type_key = "Lab"
        if cpt in ["64493", "64494"]: service_type_key = "Inpatient" # Example mapping

        benefit_rule = self.get_benefit_rule(service_type_key, policy_details["benefits"], network_status)

        # --- Benefit Application Order ---
        deductible_limit = policy_details.get("deductible_individual", 0.0)
        oop_max_limit = policy_details.get("oop_max_individual", 0.0)
        deductible_met = current_accumulators.get("deductible_met_individual", 0.0)
        oop_max_met = current_accumulators.get("oop_max_met_individual", 0.0)

        member_resp_this_line = 0.0
        insurer_pay_this_line = 0.0
        applied_to_deductible = 0.0
        applied_to_oop = 0.0 # Tracks only amounts subject to OOP Max

        # 1. Apply Copay (if applicable and BEFORE deductible)
        copay = benefit_rule.get("copay", 0.0)
        # Copay typically applies *instead* of deductible/coinsurance if applies_to_deductible is False
        if copay > 0 and not benefit_rule.get("applies_to_deductible", True): # Check if copay applies *before* ded
            amount_to_pay = min(copay, remaining_allowed) # Can't pay more copay than allowed amount
            results["copay_applied"] = amount_to_pay
            member_resp_this_line += amount_to_pay
            applied_to_oop += amount_to_pay # Copays usually count towards OOP Max
            remaining_allowed -= amount_to_pay
            results["notes"].append(f"Applied ${amount_to_pay:.2f} Copay.")

        # 2. Apply Deductible (if applicable)
        if remaining_allowed > 0 and benefit_rule.get("deductible_applies", False):
            remaining_deductible = max(0, deductible_limit - deductible_met)
            if remaining_deductible > 0:
                amount_to_apply_to_ded = min(remaining_allowed, remaining_deductible)
                results["deductible_applied"] = amount_to_apply_to_ded
                member_resp_this_line += amount_to_apply_to_ded
                applied_to_deductible += amount_to_apply_to_ded # Track for accumulator update
                applied_to_oop += amount_to_apply_to_ded # Deductible counts towards OOP Max
                remaining_allowed -= amount_to_apply_to_ded
                results["notes"].append(f"Applied ${amount_to_apply_to_ded:.2f} towards deductible.")

        # 3. Apply Coinsurance (if applicable)
        if remaining_allowed > 0:
            coinsurance_rate = benefit_rule.get("coinsurance", 0.0) # Member's portion
            if coinsurance_rate > 0:
                member_coinsurance_amount = remaining_allowed * coinsurance_rate
                results["coinsurance_member_owes"] = member_coinsurance_amount
                member_resp_this_line += member_coinsurance_amount
                applied_to_oop += member_coinsurance_amount # Coinsurance counts towards OOP Max
                remaining_allowed -= member_coinsurance_amount # What's left is insurer portion
                results["notes"].append(f"Applied {coinsurance_rate*100:.0f}% coinsurance (${member_coinsurance_amount:.2f}).")

        # 4. Calculate Insurer Payment
        insurer_pay_this_line = remaining_allowed # What's left after copay/ded/coins

        # 5. Check Out-of-Pocket Max
        potential_total_oop = oop_max_met + applied_to_oop
        if potential_total_oop > oop_max_limit:
            overage = potential_total_oop - oop_max_limit
            results["notes"].append(f"OOP Max Limit (${oop_max_limit:.2f}) reached. Reducing member responsibility by ${overage:.2f}.")
            # Reduce member responsibility by the overage, increase insurer payment
            actual_oop_applied_this_line = applied_to_oop - overage
            member_resp_this_line -= overage
            insurer_pay_this_line += overage # Insurer pays the difference
            applied_to_oop = actual_oop_applied_this_line # Cap OOP applied at the limit

        # Final assignment
        results["member_responsibility"] = round(member_resp_this_line, 2)
        results["insurer_payment"] = round(insurer_pay_this_line, 2)
        results["applied_to_deductible_this_line"] = round(applied_to_deductible, 2)
        results["applied_to_oop_max_this_line"] = round(applied_to_oop, 2)
        results["line_status"] = "Adjudicated"

        # --- IMPORTANT: Update accumulators for the *next line* ---
        current_accumulators["deductible_met_individual"] += results["applied_to_deductible_this_line"]
        current_accumulators["oop_max_met_individual"] += results["applied_to_oop_max_this_line"]

        logger.info(f"[BenefitsEngine] Line Result: Member Owes: ${results['member_responsibility']:.2f}, Insurer Pays: ${results['insurer_payment']:.2f}, Applied Ded: ${results['applied_to_deductible_this_line']:.2f}, Applied OOP: ${results['applied_to_oop_max_this_line']:.2f}")
        return results
    

def get_benefit_year(date_of_service: str) -> int:
    """Determines the benefit year from the date of service."""
    try:
        return datetime.strptime(date_of_service, "%Y-%m-%d").year
    except (ValueError, TypeError):
        return datetime.now().year # Fallback to current year


@tool
def adjudicate_claim(validated_claim_data: str) -> tuple[bool, dict | None, list[str]]:
    """
    This method is to check and apply policy benifits and adjudication based on the validated claim data for further processing.

    Parameters:
    - validated_claim_data: validated claim data (from CIVA).
        Here's an example of validated_claim_data format:
        ```
        {
            "member_id": "MEMBER456",
            "patient_name": "Sarah Member",
            "member_eligibility": {"member_id": "MEMBER456", "date_of_service": "2023-10-26", "is_eligible": True, "plan_id": "HMO_SILVER"},
            "services": [
                {
                    "date_of_service": "2023-10-26",
                    "cpt_code": "99214",
                    "icd_10_code": "M54.5",
                    "provider_npi": "1234567890",
                    "charge_amount": 250.00,
                    "network_status": "In-Network"
                },
                {
                    "date_of_service": "2023-10-26",
                    "cpt_code": "80053",
                    "icd_10_code": "M54.5",
                    "provider_npi": "0987654321", # Assumed In-Network from CIVA
                    "charge_amount": 120.00,
                    "network_status": "In-Network"
                }
            ]
        }
        ```
    :returns: (success_status, adjudicated_claim_data, list_of_messages/errors)
    """
    try:
        processed_claim_data: dict = json.loads(validated_claim_data)  
        logger.info(f"\n[PBAA] Received validated claim for adjudication. processed_claim_data: {processed_claim_data}")      
    except json.JSONDecodeError as e:
        logger.info("Error decoding JSON:", e)
    
    policy_client = CorePolicySystemAPIClient()
    preauth_client = PreAuthorizationDBClient()
    guidelines_tool = MedicalGuidelinesTool()
    benefits_engine = BenefitsEngineTool()
    
    adjudicated_data = processed_claim_data.copy() # Work on a copy
    messages = []
    claim_level_status = "Processing"
    needs_clinical_review = False

    # 1. Get Basic Info
    member_id = adjudicated_data.get("member_id")
    if not member_id:
        return False, adjudicated_data, ["Critical Error: Missing Member ID."]
    
    # Use DOS from first line to determine benefit year and get policy/accumulators
    # Real system might need to handle claims spanning benefit years.
    first_line_dos = adjudicated_data.get("services", [{}])[0].get("date_of_service")
    if not first_line_dos:
            return False, adjudicated_data, ["Critical Error: Missing Date of Service on first line."]
    benefit_year = get_benefit_year(first_line_dos)

    plan_id = adjudicated_data.get("member_eligibility", {}).get("plan_id")
    if not plan_id:
        return False, adjudicated_data, ["Critical Error: Missing Plan ID from eligibility data."]

    # 2. Fetch Policy and Initial Accumulators
    policy_ok, policy_details, policy_err = policy_client.get_member_policy_details(plan_id)
    if not policy_ok:
        return False, adjudicated_data, [f"Failed to get policy details: {policy_err}"]

    accum_ok, initial_accumulators, accum_err = policy_client.get_member_accumulators(member_id, benefit_year)
    if not accum_ok:
        return False, adjudicated_data, [f"Failed to get initial accumulators: {accum_err}"]

    # Keep track of accumulators AS THIS CLAIM is processed
    # Need a deep copy if accumulators dict contains mutable types, fine for simple floats.
    current_claim_accumulators = initial_accumulators.copy()

    # Track overall claim totals and accumulator changes from this claim
    total_member_responsibility = 0.0
    total_insurer_payment = 0.0
    total_applied_to_deductible = 0.0
    total_applied_to_oop = 0.0

    # 3. Adjudicate Each Line
    claim_lines = adjudicated_data.get("services", [])
    for i, line in enumerate(claim_lines):
        logger.info(f"\n[PBAA] Processing Line {i+1} - CPT: {line.get('cpt_code')}")
        line_adjudication_result = None
        line_status = "Pending"
        line_messages = []

        # Check Pre-Authorization
        cpt = line.get("cpt_code")
        icd = line.get("icd_10_code", "Unknown") # Need a default if missing
        auth_ok, auth_info, auth_err = preauth_client.check_pre_auth_status(member_id, cpt, icd)

        if not auth_ok:
            line_status = "Adjudication Error"
            line_messages.append(f"Pre-auth check failed: {auth_err}")
            needs_clinical_review = True # Flag for review
        elif auth_info.get("required") and auth_info.get("status") != "Approved":
            line_status = "Denied - PreAuth Missing/Not Approved"
            line_messages.append(f"Pre-authorization required but status is '{auth_info.get('status', 'Unknown')}'.")
            # Decide policy: Deny line or pend for review. Here we deny.
            line_adjudication_result = { # Set financial result for denied line
                    "line_status": line_status, "allowed_amount": 0.0, "copay_applied": 0.0, "deductible_applied": 0.0,
                    "coinsurance_member_owes": 0.0, "member_responsibility": line.get("charge_amount", 0.0), # Member owes full charge if denied this way
                    "insurer_payment": 0.0, "notes": line_messages,
                    "applied_to_deductible_this_line": 0.0, "applied_to_oop_max_this_line": 0.0
            }
        else: # Pre-auth OK or not required
            if auth_info.get("required"):
                line_messages.append(f"Pre-authorization approved (Auth #: {auth_info.get('auth_number', 'N/A')}).")

            # Optional: Check Guidelines
            guide_ok, guide_info, guide_err = guidelines_tool.check_coverage_guidelines(cpt, icd)
            coverage_status = "Unknown"
            if not guide_ok:
                line_messages.append(f"Guideline check failed: {guide_err}")
                needs_clinical_review = True
            elif guide_info:
                coverage_status = guide_info.get("coverage_status", "Unknown")
                line_messages.append(f"Guideline check: {coverage_status}")
                if "Requires Review" in coverage_status:
                    needs_clinical_review = True
                if "Not Covered" in coverage_status: # Example policy: deny if guidelines say not covered
                        line_status = "Denied - Not Covered per Guidelines"
                        line_adjudication_result = { # Denied line result
                        "line_status": line_status, "allowed_amount": 0.0, "copay_applied": 0.0, "deductible_applied": 0.0,
                        "coinsurance_member_owes": 0.0, "member_responsibility": line.get("charge_amount", 0.0),
                        "insurer_payment": 0.0, "notes": line_messages,
                        "applied_to_deductible_this_line": 0.0, "applied_to_oop_max_this_line": 0.0
                        }

        # Adjudicate Financially (if not already denied)
        if line_adjudication_result is None:
            line_adjudication_result = benefits_engine.adjudicate_claim_line(
                line,
                policy_details,
                current_claim_accumulators # Pass the mutable dict
            )
            line_status = line_adjudication_result.get("line_status", "Error")
            line_messages.extend(line_adjudication_result.get("notes", []))


        # Update line data and totals
        line.update(line_adjudication_result) # Add adjudication results to the line dict
        line["processing_messages"] = line_messages # Keep messages specific to the line

        total_member_responsibility += line.get("member_responsibility", 0.0)
        total_insurer_payment += line.get("insurer_payment", 0.0)
        total_applied_to_deductible += line.get("applied_to_deductible_this_line", 0.0)
        total_applied_to_oop += line.get("applied_to_oop_max_this_line", 0.0)

    # 4. Finalize Claim Level Info
    adjudicated_data["claim_summary"] = {
        "total_charge_amount": sum(l.get("charge_amount", 0.0) for l in claim_lines),
        "total_allowed_amount": round(sum(l.get("allowed_amount", 0.0) for l in claim_lines), 2),
        "total_member_responsibility": round(total_member_responsibility, 2),
        "total_insurer_payment": round(total_insurer_payment, 2),
        "total_applied_to_deductible": round(total_applied_to_deductible, 2),
        "total_applied_to_oop_max": round(total_applied_to_oop, 2),
        "adjudication_timestamp": datetime.now().isoformat(),
        "initial_accumulators": initial_accumulators, # Show state before this claim
        "final_accumulators_after_claim": current_claim_accumulators, # Show state after this claim
        "needs_clinical_review": needs_clinical_review,
    }

    if any(l.get("line_status", "").startswith("Denied") for l in claim_lines):
        claim_level_status = "Processed - Partially or Fully Denied"
    elif needs_clinical_review:
            claim_level_status = "Processed - Pending Clinical Review"
    elif all(l.get("line_status") == "Adjudicated" for l in claim_lines):
            claim_level_status = "Processed - Adjudicated"
    else:
            claim_level_status = "Processed - With Errors" # Some lines failed processing

    adjudicated_data["claim_level_status"] = claim_level_status
    messages.append(f"Claim adjudication status: {claim_level_status}")

    # 5. Update Accumulators in Core System (only if claim processed without critical errors stopping adjudication)
    if total_applied_to_deductible > 0 or total_applied_to_oop > 0:
        update_ok, update_err = policy_client.update_member_accumulators(
            member_id,
            benefit_year,
            total_applied_to_deductible,
            total_applied_to_oop
        )
        if not update_ok:
            messages.append(f"CRITICAL WARNING: Failed to update accumulators in core system: {update_err}")
            # This would likely require manual intervention / retry logic
        else:
                messages.append("Core accumulators updated successfully.")


    return True, adjudicated_data, messages
