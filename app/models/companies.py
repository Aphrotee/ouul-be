#!/usr/bin/env python3

"""module for deefining Company data model"""


from datetime import datetime
from app.models.models import Base, Basemodel, Response
from pydantic import BaseModel
from sqlalchemy import Column, ForeignKey, String, Boolean, Integer
from sqlalchemy.orm import relationship
from typing import List

class Company(Basemodel, Base):
    """Company data model"""
    __tablename__ = "companies"

    user_id = Column(String, ForeignKey('users.id'), nullable=False) # id of the user that created the Company (owner)
    is_registered = Column(Boolean, nullable=False) # registration status of the Company
    country_of_incorporation = Column(String, nullable=False) # country of incorporation
    type_of_company = Column(String, nullable=False, default="") # type of Company
    company_number = Column(String, nullable=False, default="") # Company incorporation number
    company_name = Column(String, nullable=False, default="") # Company name
    year_established = Column(Integer, nullable=False, default=datetime.now().year) # year of establishment
    company_logo_url = Column(String, nullable=False, default="") # url of the Company logo
    company_website_url = Column(String, nullable=False, default="") # url of the Company website
    headquarters_city = Column(String, nullable=False, default="") # city of the Company headquarters
    headquarters_country = Column(String, nullable=False, default="") # country of the Company headquarters
    industry_sector = Column(String, nullable=False, default="") # industry sector of Company
    type_of_entity = Column(String, nullable=False, default="") # type of entity (private, public, startup, sme, other)
    tax_identification_number = Column(String, nullable=False, default="") # company tax identification number
    company_contact_person_name = Column(String, nullable=False, default="") # company contact person name
    company_contact_person_position = Column(String, nullable=False, default="") # company contact person position
    company_contact_person_email = Column(String, nullable=False, default="") # company contact person email
    company_contact_person_phone_number = Column(String, nullable=False, default="") # company contact person phone number
    company_description = Column(String, nullable=False, default="") # description of the Company
    company_mission_statement = Column(String, nullable=False, default="") # mission statement of the Company
    company_vision_statement = Column(String, nullable=False, default="") # vision statement of the Company
    company_core_values = Column(String, nullable=False, default="") # values of the Company
    company_products_services = Column(String, nullable=False, default="") # products and services of the Company
    company_value_proposition = Column(String, nullable=False, default="") # value proposition of the Company
    users = relationship("User", back_populates="Companies") # Company owner's data


class CompanySchema(BaseModel):
    is_registered: bool
    country_of_incorporation: str
    type_of_company: str
    company_number: str
    company_name: str
    year_established: int
    company_logo_url: str
    company_website_url: str
    headquarters_city: str
    headquarters_country: str
    industry_sector: str
    type_of_entity: str
    tax_identification_number: str

class CompanyResponseSchema(BaseModel):
    id: str
    created_at: datetime
    updated_at: datetime
    user_id: str
    is_registered: bool
    country_of_incorporation: str
    type_of_company: str
    company_number: str
    company_name: str
    year_established: int
    company_logo_url: str
    company_website_url: str
    headquarters_city: str
    headquarters_country: str
    industry_sector: str
    type_of_entity: str
    tax_identification_number: str
    company_contact_person_name: str
    company_contact_person_position: str
    company_contact_person_email: str
    company_contact_person_phone_number:str
    company_description: str
    company_mission_statement: str
    company_vision_statement: str
    company_core_values: str
    company_products_services: str
    company_value_proposition: str
    

class SingleCompanyResponse(Response):
    data: CompanyResponseSchema

class Data(BaseModel):
    count: int # number of returned Companys
    Companies: List[CompanyResponseSchema]

class MultipleCompaniesResponse(Response):
    data: Data