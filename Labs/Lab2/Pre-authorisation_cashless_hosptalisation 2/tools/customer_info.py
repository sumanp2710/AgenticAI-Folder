from pydantic import BaseModel, Field
from typing import Optional
from ibm_watsonx_orchestrate.agent_builder.tools import tool

customers_data = [
    {
        "customer_id": "CUST001",
        "full_name": "Ravi Kumar",
        "gender": "Male",
        "aadhar_number": "1234-5678-9012",
        "customer_address": "123 MG Road, Bangalore",
        "contact_number": "9876543210",
        "email_address": "cp4bautomation@gmail.com",
        "residential_address": "123 MG Road, Bangalore",
        "mailing_address": "PO Box 456, Bangalore",
        "occupation": "Software Engineer"
    }
]

class CustomerInfoRequest(BaseModel):
    customer_id: str = Field(..., description="Customer ID")

class CustomerInfoResponse(BaseModel):
    customer_id: str
    full_name: str
    gender: str
    aadhar_number: str
    customer_address: str
    contact_number: str
    email_address: str
    residential_address: str
    mailing_address: str
    occupation: str

@tool(name="get_customer_info", description="Fetch full customer profile by customer ID")
def get_customer_info(customer_id: str) -> Optional[CustomerInfoResponse]:
    """
    Retrieve customer information based on the provided customer ID.

    :param request: CustomerInfoRequest containing the customer ID.
    :returns: CustomerInfoResponse with customer details or None if not found.
    """
    for c in customers_data:
        if c["customer_id"] == customer_id:
            return CustomerInfoResponse(**c)
    return None

if __name__ == '__main__':
    cust = get_customer_info(customer_id='CUST001')
    print(cust)