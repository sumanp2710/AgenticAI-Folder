import json
import time # To simulate network delay

from ibm_watsonx_orchestrate.agent_builder.tools import tool

# ---- MOCK AUTHENTICATION SERVICE ----
# In a real system, this would be a separate microservice or API endpoint.
# For this example, it's just a function.

MOCK_MEMBER_DATABASE = {
    "MEMBER123": {
        "date_of_birth": "1990-01-15",
        "full_name": "Alice Wonderland",
        "is_active": True,
        "security_token": "dummy_token_alice_123" # In reality, tokens are generated dynamically
    },
    "MEMBER456": {
        "date_of_birth": "1985-07-22",
        "full_name": "Sarah Johnson",
        "is_active": True,
        "security_token": "dummy_token_bob_456"
    },
    "MEMBER789": {
        "date_of_birth": "2000-11-01",
        "full_name": "Carol Danvers",
        "is_active": False, # Example of an inactive member
        "security_token": "dummy_token_carol_789"
    }
}

def call_external_auth_api(member_id: str, date_of_birth: str) -> dict:
    """
    Simulates calling an external authentication API.
    In a real system, this would involve:
    - An HTTP POST request to a secure endpoint.
    - Sending member_id and date_of_birth in the request body (e.g., as JSON).
    - Receiving a JSON response.
    - Proper error handling for network issues, timeouts, etc.
    """
    print(f"[AuthAPI_SIM] Received auth request for Member ID: {member_id}, DOB: {date_of_birth}")
    time.sleep(0.5) # Simulate network latency

    member_data = MOCK_MEMBER_DATABASE.get(member_id)

    if member_data:
        if member_data["date_of_birth"] == date_of_birth:
            if member_data["is_active"]:
                print("[AuthAPI_SIM] Authentication successful.")
                return {
                    "status_code": 200,
                    "body": {
                        "authenticated": True,
                        "member_id": member_id,
                        "full_name": member_data["full_name"],
                        "session_token": member_data["security_token"], # Or a newly generated session token
                        "message": "Authentication successful."
                    }
                }
            else:
                print("[AuthAPI_SIM] Authentication failed: Member account is inactive.")
                return {
                    "status_code": 403, # Forbidden
                    "body": {
                        "authenticated": False,
                        "message": "Authentication failed: Member account is inactive."
                    }
                }
        else:
            print("[AuthAPI_SIM] Authentication failed: Date of birth mismatch.")
            return {
                "status_code": 401, # Unauthorized
                "body": {
                    "authenticated": False,
                    "message": "Authentication failed: Invalid credentials (DOB)."
                }
            }
    else:
        print("[AuthAPI_SIM] Authentication failed: Member ID not found.")
        return {
            "status_code": 404, # Not Found
            "body": {
                "authenticated": False,
                "message": "Authentication failed: Invalid credentials (Member ID)."
            }
        }

@tool
def authenticate_member(member_id: str, date_of_birth: str) -> tuple[bool, dict]:
    """
    Uses the (simulated) external authentication API to verify a member.
    :param member_id: Member's ID 
    :param date_of_birth: Member's date of birth in format yyyy-mm-dd. For example, 26th January 1981 should be converted as 1981-01-26 format. 
    :returns:
        A tuple: (bool: authentication_status, dict: response_data)
        response_data contains more details like full_name or error messages.
    """
    print(f"[FCA_AuthTool] Attempting to authenticate Member ID: {member_id}")

    # --- Input Validation (Basic) ---
    if not member_id or not date_of_birth:
        # This basic validation might happen even before calling the tool,
        # within the FCA's conversational logic.
        print("[FCA_AuthTool] Error: Member ID and Date of Birth cannot be empty.")
        return False, {"message": "Member ID and Date of Birth are required."}
    # Add more validation for format if needed (e.g., DOB format YYYY-MM-DD)

    try:
        # This is where the call to the actual external API would happen
        api_response = call_external_auth_api(member_id, date_of_birth)

        # Process the API response
        if api_response["status_code"] == 200:
            auth_result = api_response["body"]["authenticated"]
            message = api_response["body"]["message"]
            member_details = {
                "full_name": api_response["body"].get("full_name"),
                "session_token": api_response["body"].get("session_token") # IMPORTANT for subsequent API calls
            }
            print(f"[FCA_AuthTool] Authentication API response: {message}")
            return auth_result, {**api_response["body"], **member_details}
        else:
            # Handle API errors (401, 403, 404, 500, etc.)
            error_message = api_response["body"].get("message", "An unknown authentication error occurred.")
            print(f"[FCA_AuthTool] Authentication API error: {error_message} (Status: {api_response['status_code']})")
            return False, {"message": error_message, "status_code": api_response["status_code"]}

    except Exception as e:
        # Catch-all for unexpected errors (e.g., network issue if it were a real call)
        print(f"[FCA_AuthTool] Critical error during authentication: {str(e)}")
        return False, {"message": f"A system error occurred during authentication: {str(e)}"}