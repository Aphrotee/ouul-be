#!/usr/bin/env python3

""" Module containaning routes for managing user companies """

from datetime import datetime
from dotenv import load_dotenv
from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.dependencies.error import httpError
from app.dependencies.auth_dependencies import validate_admin, get_user
from app.dependencies.dependencies import is_company_verified, check_company_parameters
from app.utils.cloudinary_file_storage import process_file_upload, delete_file_from_cloud
from app.models.users import User
from app.models.companies import Company, CompanySchema, SingleCompanyResponse, MultipleCompaniesResponse


# Load the environment variables from the .env file
load_dotenv()

router = APIRouter(tags=["Projects"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@router.post("/companies/new", status_code=201, response_model=SingleCompanyResponse)
async def upload_company(token: Annotated[str, Depends(oauth2_scheme)],
                         is_registered: bool = Form(...),
                         country_of_incorporation: str = Form(...),
                         type_of_company: str = Form(...),
                         company_number: str = Form(...),
                         company_name: str = Form(...),
                         year_established: int = Form(...),
                         company_website_url: str = Form(...),
                         headquarters_city: str = Form(...),
                         headquarters_country: str = Form(...),
                         industry_sector: str = Form(...),
                         type_of_entity: str = Form(...),
                         tax_identification_number: str = Form(...),
                         company_logo: UploadFile = File(...),
                         db: Session = Depends(get_db)):
    """
    Create a company
    """
    try:
        id = validate_admin(token)
        user: User = get_user(id, db)
        if user is None:
            raise httpError(status_code=404, detail="User not found")
        if not user.isVerified:
            raise httpError(status_code=403, detail="You cannot access this resource because your account is not activated")
        if is_company_verified(company_name, company_number, headquarters_country):
            company = CompanySchema(
                is_registered=is_registered,
                country_of_incorporation=country_of_incorporation,
                type_of_company=type_of_company,
                company_number=company_number,
                company_name=company_name,
                year_established=year_established,
                company_logo_url="",
                company_website_url=company_website_url,
                headquarters_city=headquarters_city,
                headquarters_country=headquarters_country,
                industry_sector=industry_sector,
                type_of_entity=type_of_entity,
                tax_identification_number=tax_identification_number
            )
            companyDict = company.model_dump()

            # Determine file extension
            file_extension = company_logo.filename.split(".")[-1].lower()
            folder = company_name.replace(" ", "_").lower()

            # Define content type based on file extension
            if file_extension not in ['jpg', 'jpeg', 'png']:
                imageCount += 1
            else:
                raise httpError(status_code=400, detail="Invalid file type. Only image is allowed as company logo")
            
            check_company_parameters(companyDict)

            urls = await process_file_upload(company_logo, folder)
            companyDict['company_logo_url'] = urls["image_urls"][0]

            newCompany = Company(**companyDict)
            newCompany.save(db)
            return {
                "success": True,
                "message": "Company created successfully",
                "data": newCompany.to_dict(),
            }

    except Exception as e:
        print(str(e))
        if isinstance(e, HTTPException):
            raise e
        raise httpError(status_code=500, detail=str(e))
    

@router.put("/companies/update-company-info", status_code=201, response_model=SingleCompanyResponse)
async def upload_company(token: Annotated[str, Depends(oauth2_scheme)],
                         is_registered: bool = Form(...),
                         country_of_incorporation: str = Form(...),
                         type_of_company: str = Form(...),
                         company_number: str = Form(...),
                         company_name: str = Form(...),
                         year_established: int = Form(...),
                         company_website_url: str = Form(...),
                         headquarters_city: str = Form(...),
                         headquarters_country: str = Form(...),
                         industry_sector: str = Form(...),
                         type_of_entity: str = Form(...),
                         tax_identification_number: str = Form(...),
                         company_logo: UploadFile = File(...),
                         db: Session = Depends(get_db)):
    """
    Create a company
    """