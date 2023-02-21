import requests
import csv

# API endpoint URLs
GET_COMPANIES_URL = "https://api.hubapi.com/companies/v2/companies"
CREATE_COMPANY_URL = "https://api.hubapi.com/companies/v2/companies"
ASSOCIATE_COMPANY_URL = "https://api.hubapi.com/crm-associations/v1/associations"

# HubSpot API key
HUBSPOT_API_KEY = "<c0e69b01-07dd-4f7d-9bce-8b68afcd8e69>"

# Read the CSV file to get the company names
with open(r'C:\Users\manu\company_names.csv', newline='') as csvfile:
    reader = csv.reader(csvfile)
    company_names = [row[0] for row in reader]

# Get all the companies in the HubSpot account
response = requests.get(GET_COMPANIES_URL, params={"hapikey": HUBSPOT_API_KEY})
companies = response.json()

# Iterate through the companies to identify the child companies
child_companies = []
parent_company_ids = {}
for company in companies:
    if isinstance(company, dict) and company.get("properties", {}).get("client_parent_company_id") in company_names:
        child_companies.append(company)
        parent_company_ids[company["companyId"]] = company["properties"]["client_parent_company_id"]
# Update the company name using the supplied CSV as a reference
for company in child_companies:
    company_name = next((row[1] for row in company_names if row[0] == company["properties"]["client_parent_company_id"]), None)
    if company_name:
        company_data = {
            "properties": [
                {
                    "name": "name",
                    "value": company_name
                }
            ]
        }
        update_url = f"{CREATE_COMPANY_URL}/{company['companyId']}"
        response = requests.put(update_url, params={"hapikey": HUBSPOT_API_KEY}, json=company_data)

# Create parent companies (if needed)
for parent_company_id in set(parent_company_ids.values()):
    parent_company_data = {
        "properties": [
            {
                "name": "name",
                "value": f"{parent_company_id} (Parent)"
            },
            {
                "name": "client_company_location_id",
                "value": parent_company_id
            }
        ]
    }
    create_response = requests.post(CREATE_COMPANY_URL, params={"hapikey": HUBSPOT_API_KEY}, json=parent_company_data)
    parent_company_id = create_response.json()["companyId"]
