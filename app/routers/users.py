#!/usr/bin/env python3

"""users module for defining endpoints for admin account management"""

from app.dependencies.error import httpError
from app.dependencies.database import get_db
from app.dependencies.auth_dependencies import (validate_admin,
                                                get_admin,
                                                hash_password,
                                                verify_password)
from app.models.users import User, UserSignupSchema, UserOtpSchema, UserResponse, MultipleUserResponse, UserPasswordSchema, UserPINSchema
from app.utils.generate_otp import generate_otp
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session


router = APIRouter(tags=["Users"])

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@router.post("/users/send-otp", status_code=201)
async def send_otp(userSchema: UserSignupSchema,
                   db: Session = Depends(get_db)):
    """Endpoint for sending otp for user verificarion"""
    try:
        userDict: dict[str, str] = userSchema.model_dump()
        existingUser: User = db.query(User).filter(User.email == userDict['email']).first()
        if existingUser is not None:
            if existingUser.isVerified:
                raise httpError(status_code=301, detail="login")
        else:
            user = User(**userDict)
            user.save(db)
        otp = generate_otp()
        otp_key = userDict["email"]
        # store otp in cache
        # await send_verification(userDict["email"], otp)
        return {
            "success": True,
            "message": "Otp sent to user email successfully.",
            "data":  None
        }
    except Exception as e:
        print(str(e))
        if isinstance(e, HTTPException):
            raise e
        raise httpError(status_code=500, detail=str(e))


@router.put("/users/verify-otp", status_code=200, response_model=UserResponse)
async def verify_otp(userSchema: UserOtpSchema,
                     db: Session = Depends(get_db)):
    """Endpoint for verifying user by otp"""
    try:
        userDict: dict[str, str] = userSchema.model_dump()
        unverifiedUser: User = db.query(User).filter(User.email == userDict['email']).first()
        if unverifiedUser is None:
            raise httpError(status_code=404, detail="user not found")
        if unverifiedUser.isVerified:
            raise httpError(status_code=301, detail="login")
        cache_otp = "123456" # get from cache

        if not cache_otp:
            raise httpError(status_code=401, detail="otp expired, request a new one") 
        user_otp = userDict["otp"]

        if cache_otp != user_otp:
            raise httpError(status_code=400, detail="Invalid otp") 
        unverifiedUser.update(db, isVerified=True)
        user: User = db.query(User).filter(User.email == userDict['email']).first()

        return {
            "success": True,
            "message": "User verified successfully.",
            "data":  user
        }
    except Exception as e:
        print(str(e))
        if isinstance(e, HTTPException):
            raise e
        raise httpError(status_code=500, detail=str(e))
    
@router.put("/users/set-password", status_code=200, response_model=UserResponse)
async def set_password(userSchema: UserPasswordSchema,
                       db: Session = Depends(get_db)):
    """Endpoint for setting user password"""
    try:
        userDict: dict[str, str] = userSchema.model_dump()
        verifiedUser: User = db.query(User).filter(User.email == userDict['email']).first()
        if verifiedUser is None:
            raise httpError(status_code=404, detail="user not found")
        if not verifiedUser.isVerified:
            raise httpError(status_code=301, detail="verify user")
        if len(userDict['password']) < 8:
            raise httpError(status_code=400, detail="password must be at least 8 characters")
        verifiedUser.update(db, password=hash_password(userDict['password']))

        user: User = db.query(User).filter(User.email == userDict['email']).first()

        return {
            "success": True,
            "message": "User password updated successfully.",
            "data":  user
        }
    except Exception as e:
        print(str(e))
        if isinstance(e, HTTPException):
            raise e
        raise httpError(status_code=500, detail=str(e))

@router.put("/users/set-pin", status_code=200, response_model=UserResponse)
async def set_pin(userSchema: UserPINSchema,
                       db: Session = Depends(get_db)):

    """Endpoint for setting user password"""
    try:
        userDict: dict[str, str] = userSchema.model_dump()
        verifiedUser: User = db.query(User).filter(User.email == userDict['email']).first()
        if verifiedUser is None:
            raise httpError(status_code=404, detail="user not found")
        if not verifiedUser.isVerified:
            raise httpError(status_code=301, detail="verify user")
        if not verify_password(userSchema.password, hashed=str(verifiedUser.password)):
            raise httpError(status_code=401, detail="Invalid password")
        if len(userDict['pin']) != 4:
            raise httpError(status_code=400, detail="pin must be 4 digits")
        if not userDict['pin'].isdigit():
            raise httpError(status_code=400, detail="pin must be digits")

        verifiedUser.update(db, pin=hash_password(userDict['pin']))
        user: User = db.query(User).filter(User.email == userDict['email']).first()

        return {
            "success": True,
            "message": "User PIN updated successfully.",
            "data":  user
        }
    except Exception as e:
        print(str(e))
        if isinstance(e, HTTPException):
            raise e
        raise httpError(status_code=500, detail=str(e))