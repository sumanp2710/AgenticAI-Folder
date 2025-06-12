from pydantic import Field, BaseModel
from typing import Optional
from ibm_watsonx_orchestrate.agent_builder.tools import tool
import requests

class SendEmailResponse(BaseModel):
    message: str = Field(..., description='message from send Email API')



@tool(name="send_email", description="send email to recipients")
def send_email(
        email_recipients: str,
        email_body: str,
        email_subject:str
) -> dict:
    """
    Sends the email to 'email_recipients' using the email API.
    This tool is using automation squad specific gmail account.
    """
    try:

        req = {
            "to": email_recipients,
            "subject": email_subject,
            "body": email_body
        }
        base_url = "https://application-53.1f0o357viivn.us-south.codeengine.appdomain.cloud/send-email"
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
            message=f"Error: {str(e)}"
        )


# if __name__ == '__main__':
#     status = send_email(email_recipients="shwetrai@in.ibm.com",
#                                       email_body="This is test email from tool",
#                                       email_subject="Tool email")
#     print(status)
