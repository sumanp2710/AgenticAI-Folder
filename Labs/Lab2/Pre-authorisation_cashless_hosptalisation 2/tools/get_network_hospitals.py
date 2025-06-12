from ibm_watsonx_orchestrate.agent_builder.tools import tool


@tool (name="get_network_hospitals", description="Tool to fetch the list of network hospitals")
def get_network_hospitals():
    """
    Retrieve list of network hospitals from Insurer EIS system and returns the same
    For bootcamp perspective we are keeping the sample json message directly in the def
    """
    network_hospitals= [
        {
          "hospital_id": "HOSP001",
          "name": "City General Hospital",
          "address": {
            "street": "123 Medical Center Drive",
            "city": "Metropolis",
            "state": "California",
            "postal_code": "90210",
            "country": "USA"
          },
          "contact": {
            "phone": "+1-555-123-4567",
            "email": "info@citygeneral.org",
            "website": "www.citygeneral.org"
          },
          "specialties": ["Cardiology", "Oncology", "Emergency Medicine"],
          "beds": 450,
          "accreditation": ["JCI", "NABH"],
          "insurance_accepted": True,
          "hospital_tier": 1
        },
        {
          "hospital_id": "HOSP002",
          "name": "Green Valley Medical Center",
          "address": {
            "street": "456 Health Park Avenue",
            "city": "Springfield",
            "state": "Illinois",
            "postal_code": "62704",
            "country": "USA"
          },
          "contact": {
            "phone": "+1-555-987-6543",
            "email": "contact@gvmc.org",
            "website": "www.gvmc.org"
          },
          "specialties": ["Pediatrics", "Orthopedics", "Neurology"],
          "beds": 280,
          "accreditation": ["NABH"],
          "insurance_accepted": True,
          "hospital_tier": 2
        },
        {
          "hospital_id": "HOSP003",
          "name": "Sunrise Specialty Clinic",
          "address": {
            "street": "789 Wellness Lane",
            "city": "Portland",
            "state": "Oregon",
            "postal_code": "97205",
            "country": "USA"
          },
          "contact": {
            "phone": "+1-555-456-7890",
            "email": "support@sunrisespecialty.com",
            "website": "www.sunrisespecialty.com"
          },
          "specialties": ["Dermatology", "Ophthalmology", "Plastic Surgery"],
          "beds": 120,
          "accreditation": [],
          "insurance_accepted": False,
          "hospital_tier": 3
        }
      ]
    return network_hospitals
