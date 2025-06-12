from pydantic import BaseModel, Field
from typing import List, Optional
from ibm_watsonx_orchestrate.agent_builder.tools import tool

policies_data = [
    {
        "customer_id": "CUST001",
        "full_name": "Ravi Kumar",
        "policy_number": "POL1001",
        "premium_amount": 12000.0,
        "policy_start_date": "2023-01-01",
        "policy_end_date": "2024-01-01",
        "status": "Active",
        "coverage_details": "Health Insurance - INR 5 Lakhs",
        "co_pay": "20%"
    }
]

class PolicyInfoRequest(BaseModel):
    customer_id: str = Field(..., description="Customer ID")

class PolicyInfo(BaseModel):
    customer_id: str
    full_name: str
    policy_number: str
    premium_amount: float
    policy_start_date: str
    policy_end_date: str
    status: str
    coverage_details: str
    co_pay: str

@tool(name="get_policy_info", description="Retrieve all policy details for a customer")
def get_policy_info(customer_id:str) -> Optional[List[PolicyInfo]]:
    """
    Retrieve policy information associated with the provided customer ID.

    :param request: PolicyInfoRequest containing the customer ID.
    :returns: List of PolicyInfo or None if not found.
    """
    matches = [p for p in policies_data if p["customer_id"] == customer_id]
    return [PolicyInfo(**policy) for policy in matches] if matches else None


if __name__ == '__main__':
    policy = get_policy_info(customer_id='CUST001')
    print(policy)