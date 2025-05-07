#!/usr/bin/env python3

"""auth module for defining endpoints for admin registration and authentication"""

import os

from app.dependencies.error import httpError
from app.dependencies.database import get_db
from app.dependencies.auth_dependencies import (check_adminSignupSchema,
                                                create_access_token,
                                                hash_password,
                                                validate_admin,
                                                verify_password,
                                                get_admin)
from app.models.admins import Admin, AdminSignupSchema, AdminResponse, loginResponseSchema

from datetime import timedelta, datetime
from typing import Annotated
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session



# Load the environment variables from the .env file
load_dotenv()

router = APIRouter(tags=["Authentication"])

token_expiration = int(os.getenv("ADMIN_JWT_TOKEN_EXPIRY_MINUTES"))
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@router.post("/auth/superuser/signup", status_code=201, response_model=AdminResponse)
async def super_admin_signup(adminSchema: AdminSignupSchema,
                             adminAuthorization: Annotated[str, Header()]=None,
                             db: Session = Depends(get_db)):
    """Endpoint for superuser registration"""
    try:
        if adminAuthorization is None:
            raise httpError(status_code=401, detail="Authorization header is required")
        if verify_password(adminAuthorization, os.getenv("SUPERUSER_SECRET")):
            raise httpError(status_code=401, detail="Unauthorized")
        adminDict: dict[str, str] = adminSchema.model_dump()
        check_adminSignupSchema(adminDict, db)
        adminDict['password'] = hash_password(adminDict['password'])
        adminDict['role'] = "superuser"
        adminDict['permissions'] = {
            "create": True,
            "read": True,
            "update": True,
            "delete": True
        }
        admin = Admin(**adminDict)
        admin.save(db)
        newAdmin: Admin = db.query(Admin).filter(Admin.email == adminDict['email']).first()
        newAdminDict: dict = newAdmin.to_dict()
        return {
            "success": True,
            "message": "Superuser created successfully.",
            "data": newAdminDict
        }
    except Exception as e:
        print(str(e))
        if isinstance(e, HTTPException):
            raise e
        raise httpError(status_code=500, detail=str(e))


@router.post("/auth/admins/signup", status_code=201, response_model=AdminResponse)
async def admin_signup(token: Annotated[str, Depends(oauth2_scheme)],
                       adminSchema: AdminSignupSchema,
                       db: Session = Depends(get_db)):
    """Endpoint for admin registration"""
    try:
        id = validate_admin(token)
        admin = get_admin(id, db)
        if admin is None:
            raise httpError(status_code=404, detail="Admin not found")
        if admin.role != "superuser":
            raise httpError(status_code=403, detail="You don't have access to this resource.")
        adminDict: dict[str, str] = adminSchema.model_dump()
        check_adminSignupSchema(adminDict, db)
        adminDict['password'] = hash_password(adminDict['password'])
        admin = Admin(**adminDict)
        admin.save(db)
        newAdmin: Admin = db.query(Admin).filter(Admin.email == adminDict['email']).first()
        newAdminDict: dict = newAdmin.to_dict()
        return {
            "success": True,
            "message": "Admin created successfully.",
            "data": newAdminDict
        }
    except Exception as e:
        print(str(e))
        if isinstance(e, HTTPException):
            raise e
        raise httpError(status_code=500, detail=str(e))


@router.post("/auth/admins/login", status_code=200, response_model=loginResponseSchema)
async def admin_login(adminSchema: Annotated[OAuth2PasswordRequestForm, Depends()],
                      db: Session = Depends(get_db)):
    """Endpoint for admin login"""
    try:
        admin = db.query(Admin).filter(Admin.username == adminSchema.username).first()
        if not admin:
            raise httpError(status_code=401, detail="Invalid credentials")
        if not verify_password(adminSchema.password, hashed=str(admin.password)):
            raise httpError(status_code=401, detail="Invalid credentials")
        token = create_access_token({"adminUsername": adminSchema.username, "adminId": admin.id},
                                    expires_delta=timedelta(minutes=token_expiration))
        if not token:
            raise Exception("Error creating jwt")
        
        last_login = datetime.now()
        loggedInAdmin: dict = admin.to_dict()

        # Record the last date and time the admin logged in
        loggedInAdmin['last_login'] = last_login
        admin.update(db, last_login=last_login)

        return {
            "success": True,
            "message": "Admin logged in successfully.",
            "access_token": token,
            "token_type": "bearer",
            "data": loggedInAdmin
        }

    except Exception as e:
        print(str(e))
        if isinstance(e, HTTPException):
            raise e
        raise httpError(status_code=500, detail=str(e))