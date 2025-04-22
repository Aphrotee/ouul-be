#!/usr/bin/env python3

"""admins module for defining endpoints for admin account management"""

from app.dependencies.error import httpError
from app.dependencies.database import get_db
from app.dependencies.auth_dependencies import (validate_admin,
                                                get_admin)
from app.models.admins import Admin, AdminResponse, MultipleAdminResponse
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session


router = APIRouter(tags=["Admins"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@router.get("/admins/me", status_code=200, response_model=AdminResponse)
async def get_user(token: Annotated[str, Depends(oauth2_scheme)],
                   db: Session = Depends(get_db)):
    """Endpoint for getting admin details"""
    try:
        id = validate_admin(token)
        current_admin = get_admin(id, db)
        if current_admin is None:
            raise httpError(status_code=401, detail="Admin unidentified")
        data = current_admin.to_dict()
        return {
            "success": True,
            "message": "",
            "data": data
        }
    except Exception as e:
        print(str(e))
        if isinstance(e, HTTPException):
            raise e
        raise httpError(status_code=500, detail=str(e))


# @router.get("/admins/me/status")
# async def get_my_status(token: Annotated[str, Depends(oauth2_scheme)],
#                         db: Session = Depends(get_db)):
#     """Endpoint for getting admin status"""
#     try:
#         id = validate_admin(token)
#         current_admin = get_admin(id, db)
#         if current_admin is None:
#             raise httpError(status_code=401, detail="Admin unidentified")
#         if current_admin.is_active:
#             return {
#                 "success": True,
#                 "message": "Your account is activated",
#                 "data": True
#             }
#         else:
#             return {
#                 "success": True,
#                 "message": "Your account is deactivated",
#                 "data": False
#             }

#     except Exception as e:
#         print(str(e))
#         if isinstance(e, HTTPException):
#             raise e
#         raise httpError(status_code=500, detail=str(e))


# @router.put("/admins/{admin_id}/activate")
# async def activate_admin_account(token: Annotated[str, Depends(oauth2_scheme)],
#                                  admin_id: str,
#                                  db: Session = Depends(get_db)):
#     """Endpoint for activating a deactivated admin account"""
#     try:
#         id = validate_admin(token)
#         administrator = get_admin(id, db)
#         admin = get_admin(admin_id, db)
#         if administrator.role != "superuser":
#             raise httpError(status_code=403, detail="You don't have access to this resource.")
#         if admin is None:
#             raise httpError(status_code=404, detail="Admin unidentified")
#         if admin.role == "superuser":
#             raise httpError(status_code=403, detail="An superuser cannot activate/deactivate another superuser")
#         if admin.is_active:
#             return {
#                 "success": True,
#                 "message": "Admin account already activated",
#                 "data": None
#             }
#         admin.is_active = True
#         data = admin.to_dict()
#         admin.save(db)
#         return {
#             "success": True,
#             "message": "Admin account activated successfully",
#             "data": data
#         }
#     except Exception as e:
#         print(str(e))
#         if isinstance(e, HTTPException):
#             raise e
#         raise httpError(status_code=500, detail=str(e))
    

# @router.put("/admins/{admin_id}/deactivate")
# async def deactivate_admin_account(token: Annotated[str, Depends(oauth2_scheme)],
#                                    admin_id: str,
#                                    db: Session = Depends(get_db)):
#     """Endpoint for deactivating a deactivated admin account"""
#     try:
#         id = validate_admin(token)
#         administrator = get_admin(id, db)
#         admin = get_admin(admin_id, db)
#         if administrator.role != "superuser":
#             raise httpError(status_code=403, detail="You don't have access to this resource")
#         if admin is None:
#             raise httpError(status_code=404, detail="Admin unidentified")
#         if admin.role == "superuser":
#             raise httpError(status_code=403, detail="An superuser cannot activate/deactivate another superuser")
#         if not admin.is_active:
#             return {
#                 "success": True,
#                 "message": "Admin account already deactivated",
#                 "data": None
#             }
#         admin.is_active = False
#         data = admin.to_dict()
#         admin.save(db)
#         return {
#             "success": True,
#             "message": "Admin account deactivated successfully",
#             "data": data
#         }
#     except Exception as e:
#         print(str(e))
#         if isinstance(e, HTTPException):
#             raise e
#         raise httpError(status_code=500, detail=str(e))


@router.get("/admins/all", response_model=MultipleAdminResponse)
async def get_all_admins(token: Annotated[str, Depends(oauth2_scheme)],
                         db: Session = Depends(get_db)):
    """
    Retrieves all admins from the database
    """
    try:
        id = validate_admin(token)
        admin = get_admin(id, db)
        if admin is None:
            raise httpError(status_code=404, detail="Admin not found")
        if not admin.is_active:
            raise httpError(status_code=403, detail="You cannot access this resource because your account is not activated")
        admins = db.query(Admin).all()
        admins = list(map(lambda x: x.to_dict() , admins))
        return {
            "success": True,
            "message": "All admins retrieved successfully",
            "data": {
                "count": len(admins),
                "admins": admins
                }
        }
    except Exception as e:
        print(str(e))
        if isinstance(e, HTTPException):
            raise e
        raise httpError(status_code=500, detail=str(e))