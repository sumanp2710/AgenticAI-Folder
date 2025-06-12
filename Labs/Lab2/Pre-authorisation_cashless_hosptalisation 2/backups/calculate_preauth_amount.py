from pydantic import Field, BaseModel
from typing import Optional
from ibm_watsonx_orchestrate.agent_builder.tools import tool
import requests

class ClaimPreauthAmountResponse(BaseModel):
    approved_amount: float = Field(..., description='Pre authorised amount')
    currency: str = Field(default="INR", description='Currency type')
    message: str = Field(default="Pre-authorization amount calculated", description='Result message')


@tool(name="calculate_preauth_amount", description="Calculates the pre-authorised amount")
def calculate_preauth_amount(
        estimated_treatment_cost: float,
        policy_coverage_limit: float,
        disease_category:str,
        hospital_tier: int,
        co_payment_percentage: float,
) -> dict:
    """
    Calculate pre-authorization amount for insurance claims.
    Accepts parameters as keyword arguments which will be converted to ClaimPreauthAmountRequest.
    """
    try:

        req = {
            "estimated_treatment_cost": estimated_treatment_cost,
            "policy_coverage_limit": policy_coverage_limit,
            "disease_category": disease_category,
            "co_payment_percentage": co_payment_percentage,
            "hospital_tier": hospital_tier
        }
        base_url = "https://application-2a.1f0o357viivn.us-south.codeengine.appdomain.cloud/preauth/calculate"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        response = requests.post(
            base_url,
            headers=headers,
            json=req
        )
        response.raise_for_status()

        response_data = response.json()
        return response_data

    except Exception as e:
        return dict(
            approved_amount=0,
            currency="INR",
            message=f"Error: {str(e)}"
        )


# if __name__ == '__main__':
#     result = calculate_preauth_amount(estimated_treatment_cost=50000,
#                                       policy_coverage_limit=100000,
#                                       disease_category="critical",
#                                       co_payment_percentage=10,
#                                       hospital_tier=1)
#     print(result)
