#!/usr/bin/env python3

"""users module for defining endpoints for admin account management"""

import os

from app.dependencies.error import httpError
from app.dependencies.database import get_db
from app.dependencies.cache import get_cache
from app.dependencies.auth_dependencies import (get_user,
                                                hash_password,
                                                verify_password,
                                                validate_user,
                                                create_access_token)
from app.models.users import User, UserSignupSchema, UserOtpSchema, UserResponse, MultipleUserResponse, UserPasswordSchema, UserPINSchema, loginResponseSchema, Response, UserPasswordResetSchema, UserPINResetSchema
from app.utils.generate_otp import generate_otp
from app.utils.send_email import send_email_background
from app.utils.generate_email_templates import verificaiton_otp_html, pin_reset_otp_html, password_reset_otp_html
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from dotenv import load_dotenv


load_dotenv()
router = APIRouter(tags=["Users"])

password_token_expiration = int(os.getenv("PASSWORD_JWT_TOKEN_EXPIRY_MINUTES"))
pin_token_expiration = int(os.getenv("PIN_JWT_TOKEN_EXPIRY_MINUTES"))
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/auth/pin-login")


@router.post("/users/send-otp", status_code=201)
async def send_otp(userSchema: UserSignupSchema,
                   db: Session = Depends(get_db),
                   cache = Depends(get_cache)):
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
        print(">>>>>>>" + otp + "<<<<<<<<")
        otp_key = userDict["email"]
        # store otp in cache
        expiry = os.getenv("OTP_EXPIRY")
        cache.set(otp_key, otp, ex=expiry)

        subject = "Ouul Verification OTP"
        email_html = verificaiton_otp_html(otp)
        print(email_html)
        send_email_background(subject, userDict["email"], "", email_html)
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
                     db: Session = Depends(get_db),
                     cache = Depends(get_cache)):
    """Endpoint for verifying user by otp"""
    try:
        userDict: dict[str, str] = userSchema.model_dump()
        unverifiedUser: User = db.query(User).filter(User.email == userDict['email']).first()
        if unverifiedUser is None:
            raise httpError(status_code=404, detail="user not found")
        if unverifiedUser.isVerified:
            raise httpError(status_code=301, detail="login")
        otp_key = userDict['email']
        cache_otp = cache.get(otp_key).decode('utf-8') # "123456" # get from cache

        if cache_otp is None:
            raise httpError(status_code=401, detail="otp expired, request a new one") 
        user_otp = userDict["otp"]
        # print("=======", user_otp, cache_otp)

        if cache_otp != user_otp:
            raise httpError(status_code=400, detail="Invalid otp") 
        unverifiedUser.update(db, isVerified=True)
        user: User = db.query(User).filter(User.email == userDict['email']).first()
        cache.delete(otp_key) # delete otp from cache

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
            raise httpError(status_code=404, detail="User with email does not exist")
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

@router.post("/users/auth/password-login", status_code=200, response_model=loginResponseSchema)
async def user_login(userSchema: Annotated[OAuth2PasswordRequestForm, Depends()],
                     db: Session = Depends(get_db)):
    """Endpoint for user password login"""
    try:
        user = db.query(User).filter(User.email == userSchema.username).first()
        # userSchema.username is user's email, FastAPI just forcefully names it 'username'
        if user is None:
            raise httpError(status_code=401, detail="User with email does not exist")
        if not verify_password(userSchema.password, hashed=str(user.password)):
            raise httpError(status_code=401, detail="Invalid password")
        token = create_access_token({"userEmail": userSchema.username, "userId": user.id},
                                    expires_delta=timedelta(minutes=password_token_expiration))
        if not token:
            raise Exception("Error creating jwt")

        loggedInUser: dict = user.to_dict()

        return {
            "success": True,
            "message": "User password login successfull, login with PIN.",
            "access_token": token,
            "token_type": "bearer",
            "data": loggedInUser
        }

    except Exception as e:
        print(str(e))
        if isinstance(e, HTTPException):
            raise e
        raise httpError(status_code=500, detail=str(e))

@router.post("/users/auth/pin-login", status_code=200, response_model=loginResponseSchema)
async def user_login(userSchema: Annotated[OAuth2PasswordRequestForm, Depends()],
                     X_Password_Authorization_Token: Annotated[str, Header()],
                     db: Session = Depends(get_db)):
    """Endpoint for user pin login"""
    try:
        if X_Password_Authorization_Token is None:
            raise httpError(status_code=400, detail="X_Password_Authorization_Token header not found")
        id = validate_user(X_Password_Authorization_Token)
        user = get_user(id, db)
        if user is None:
            raise httpError(status_code=404, detail="User not found")
        
        # userSchema.password is user's 4-digit pin, FastAPI just forcefully names it 'password'
        user_pin = userSchema.password
        
        if not verify_password(user_pin, hashed=str(user.pin)):
            raise httpError(status_code=400, detail="Invalid pin")
        token = create_access_token({"userEmail": user.email, "userId": user.id},
                                    expires_delta=timedelta(minutes=pin_token_expiration))
        if not token:
            raise Exception("Error creating jwt")

        loggedInUser: dict = user.to_dict()

        return {
            "success": True,
            "message": "User pin login successfull.",
            "access_token": token,
            "token_type": "bearer",
            "data": loggedInUser
        }

    except Exception as e:
        print(str(e))
        if isinstance(e, HTTPException):
            raise e
        raise httpError(status_code=500, detail=str(e))

@router.get("/users/me", status_code=200, response_model=UserResponse)
async def get_user_details(token: Annotated[str, Depends(oauth2_scheme)],
                           db: Session = Depends(get_db)):
    """Endpoint for getting user details"""
    try:
        id = validate_user(token)
        current_user = get_user(id, db)
        if current_user is None:
            raise httpError(status_code=401, detail="User unidentified")
        data = current_user.to_dict()
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

@router.post("/users/request-pin-reset", status_code=200, response_model=Response)
async def request_pin_reset(X_Password_Authorization_Token: Annotated[str, Header()],
                            db: Session = Depends(get_db),
                            cache = Depends(get_cache)):
    """Endpoint for requesting pin reset"""
    try:
        if X_Password_Authorization_Token is None:
            raise httpError(status_code=400, detail="X_Password_Authorization_Token header not found")
        id = validate_user(X_Password_Authorization_Token)
        current_user = get_user(id, db)
        if current_user is None:
            raise httpError(status_code=401, detail="Invalid token, login with password")
        otp = generate_otp()
        print(">>>>>>>" + otp + "<<<<<<<<")
        otp_key = current_user.email
        # store otp in cache
        expiry = os.getenv("OTP_EXPIRY")
        cache.set(otp_key, otp, ex=expiry)

        subject = "Ouul PIN Reset OTP"
        email_html = pin_reset_otp_html(otp)
        print(email_html)
        send_email_background(subject, current_user.email, "", email_html)

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

@router.put("/users/reset-pin", status_code=200, response_model=UserResponse)
async def reset_pin(userSchema: UserPINResetSchema,
                    X_Password_Authorization_Token: Annotated[str, Header()],
                    db: Session = Depends(get_db),
                    cache = Depends(get_cache)):
    """Endpoint for resetting user pin"""
    try:
        if X_Password_Authorization_Token is None:
            raise httpError(status_code=400, detail="X_Password_Authorization_Token header not found")
        if userSchema.otp == "" or len(userSchema.otp) != 6:
            raise httpError(status_code=400, detail="please supply a valid 6-digit verification otp")
        id = validate_user(X_Password_Authorization_Token)
        current_user = get_user(id, db)
        if current_user is None:
            raise httpError(status_code=401, detail="User not found")
        if not current_user.isVerified:
            raise httpError(status_code=301, detail="verify user")
        otp_key = current_user.email
        cache_otp = cache.get(otp_key).decode('utf-8') # "123456" # get from cache

        if cache_otp is None:
            raise httpError(status_code=401, detail="otp expired, request a new one") 
        user_otp = userSchema.otp
        # print("=======", user_otp, cache_otp)

        if cache_otp != user_otp:
            raise httpError(status_code=400, detail="Invalid otp")
        if len(userSchema.pin) != 4:
            raise httpError(status_code=400, detail="pin must be 4 digits")
        if not userSchema.pin.isdigit():
            raise httpError(status_code=400, detail="pin must be digits")

        current_user.update(db, pin=hash_password(userSchema.pin))
        user: User = db.query(User).filter(User.email == current_user.email).first()
        cache.delete(otp_key) # delete otp from cache

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
    
@router.post("/users/{user_email}/request-password-reset", status_code=200, response_model=Response)
async def request_password_reset(user_email: str,
                                 db: Session = Depends(get_db),
                                 cache = Depends(get_cache)):
    """Endpoint for requesting password reset"""
    try:
        verifiedUser: User = db.query(User).filter(User.email == user_email).first()
        if verifiedUser is None:
            raise httpError(status_code=404, detail="user not found")
        if not verifiedUser.isVerified:
            raise httpError(status_code=301, detail="verify user")
        otp = generate_otp()
        print(">>>>>>>" + otp + "<<<<<<<<")
        otp_key = user_email
        # store otp in cache
        expiry = os.getenv("OTP_EXPIRY")
        cache.set(otp_key, otp, ex=expiry)

        subject = "Ouul Password Reset OTP"
        email_html = password_reset_otp_html(otp)
        print(email_html)
        send_email_background(subject, user_email, "", email_html)

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

@router.put("/users/reset-password", status_code=200, response_model=UserResponse)
async def reset_password(userSchema: UserPasswordResetSchema,
                         db: Session = Depends(get_db),
                         cache = Depends(get_cache)):
    """Endpoint for resetting user password"""
    try:
        otp_key = userSchema.email
        if userSchema.email == "":
            raise httpError(status_code=400, detail="please supply a valid email address")
        if userSchema.otp == "" or len(userSchema.otp) != 6:
            raise httpError(status_code=400, detail="please supply a valid 6-digit verification otp")
        if userSchema.password == "":
            raise httpError(status_code=400, detail="please supply a valid password to reset to")

        cache_otp = cache.get(otp_key).decode('utf-8') # "123456" # get from cache
        current_user: User = db.query(User).filter(User.email == userSchema.email).first()

        if current_user is None:
            raise httpError(status_code=404, detail="user not found")

        if cache_otp is None:
            raise httpError(status_code=401, detail="otp expired, request a new one") 
        user_otp = userSchema.otp
        # print("=======", user_otp, cache_otp)

        if cache_otp != user_otp:
            raise httpError(status_code=400, detail="Invalid otp")
        if len(userSchema.password) < 8:
            raise httpError(status_code=400, detail="password must be at least 8 characters")
        current_user.update(db, password=hash_password(userSchema.password))
        user: User = db.query(User).filter(User.email == current_user.email).first()
        cache.delete(otp_key) # delete otp from cache

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