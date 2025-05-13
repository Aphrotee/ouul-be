#!/usr/bin/env python

from dotenv import load_dotenv
from app.dependencies.error import httpError

# Load the environment variables from the .env file
load_dotenv()

def is_company_verified(company_name, company_number, country):
    return True

def check_company_parameters(companyDict):
    """
    Check if the company parameters are valid
    """
    if not companyDict['is_registered']:
        raise httpError(status_code=400, detail="Company is not registered")
    if not companyDict['company_number']:
        raise httpError(status_code=400, detail="Company number is required")
    if not companyDict['company_number'].isdigit():
        raise httpError(status_code=400, detail="Company number must be numeric")
    if not companyDict['company_name']:
        raise httpError(status_code=400, detail="Company name is required")
    if not companyDict['headquarters_country']:
        raise httpError(status_code=400, detail="Headquarters country is required")
    if not companyDict['headquarters_city']:
        raise httpError(status_code=400, detail="Headquarters city is required")
    if not companyDict['company_website_url']:
        raise httpError(status_code=400, detail="Company website url is required")
    if not companyDict['year_established']:
        raise httpError(status_code=400, detail="Year of company establishment is required")
    if not companyDict['industry_sector']:
        raise httpError(status_code=400, detail="Industry sector is required")
    if not companyDict['type_of_entity']:
        raise httpError(status_code=400, detail="Type of entity is required")
    if not companyDict['tax_identification_number']:
        raise httpError(status_code=400, detail="Tax identification number is required")