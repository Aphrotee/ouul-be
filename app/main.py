#!/usr/bin/env python3

"""Main module for the ouul app"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, admins, blogs

app = FastAPI()

origins = [
    "*",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:5173",
    "http://localhost:4173"
]

app.include_router(auth.router)
app.include_router(admins.router)
app.include_router(blogs.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
