from pydantic import Field, BaseModel
from requests.auth import HTTPBasicAuth
from ibm_watsonx_orchestrate.agent_builder.tools import tool, ToolPermission


# Constants
GMAIL_USER = 'cp4bautomation@gmail.com'
GMAIL_PASSWORD = 'nzukjpajmuwulukv'

class EmailContext(BaseModel):
    """
    Represents the response of read_email tool.
    It return the email body containing treatment details
    """
    email_body: str= Field(..., description='The full email body')
    email_from: str= Field(..., description='email received from')
    email_subject: str= Field(..., description='subject of the email')


@tool (name="read_email", description="Tool to fetch the new email event from TPA inbox")
def read_emails() ->EmailContext:
    """
    This is a mock tool for now.
    Future implementation should include
    1. Connection to inbox
    2. apply the filter passed as a input
    3. Get the email context
    4. return the data
    """
    return EmailContext(
        email_body= """Patient Information
                        
                        Name: Ravi Kumar
                       
                        Diagnosis (ICD-10 Codes)
                        Primary Diagnosis: e.g., H65.91 (Unspecified otitis media, right ear)
                        Secondary Diagnosis (if applicable): e.g., H72.90 (Unspecified perforation of tympanic membrane)
                        Proposed Procedure (CPT Code)
                        Procedure: e.g., Myringoplasty (69610) or Tympanoplasty (69631)
                        Laterality: Right/Left/Bilateral
                        Anesthesia: Local/General (specify)
                        Clinical Justification
                        Brief history of symptoms (e.g., chronic ear infections, hearing loss, tympanic membrane perforation).
                        Failed conservative treatments (e.g., antibiotics, ear drops).
                        Diagnostic findings (e.g., audiometry, otoscopy, CT scan if applicable).
                        Medical Necessity: Explain why surgery is required (e.g., restore hearing, prevent recurrent infections).
                        
                        Hospital Name : City General Hospital
                        Disease category: major
                        
                        Estimated Costs & Facility
                        Total cost (INR): 100000
                        Surgeon Fees (INR): 25000
                        Anesthesia Fees (INR): 15000
                        OT Fee (INR): 50000
                        Other Fee (INR): 10000
                        Expected Length of Stay: Outpatient/Inpatient
                        """,
        email_from="ent.doctordesk@unitedhealthcare.com",
        email_subject="Unspecified otitis media, right ear "
    )

#if __name__ == '__main__':
#    email_context = read_emails()
#    print(email_context)