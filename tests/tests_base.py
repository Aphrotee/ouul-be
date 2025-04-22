#!/usr/bin/env python3

import os
import random
import string
import unittest
from app.main import app
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from app.models.admins import Admin
from app.dependencies.database import get_db

# Load the environment variables from the .env file
load_dotenv()

client = TestClient(app)

class TestsBase(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        # using random.choices()
        # generating random strings
        cls.adminUsername = ''.join(random.choices(string.ascii_lowercase, k=7))
        cls.adminEmail = f"{cls.adminUsername}@gmail.com"
        cls.editorUsername = ''.join(random.choices(string.ascii_lowercase, k=7))
        cls.editorEmail = f"{cls.editorUsername}@gmail.com"
        cls.password = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        cls.db_gen = get_db()
        cls.db = next(cls.db_gen)
        data = {
            "username": cls.adminUsername,
            "email": cls.adminEmail,
            "password": cls.password
        }
        headers = {
            "Authorization": os.getenv("SUPER_ADMIN_SECRET")
        }
        client.post("/auth/super-admin/signup", headers=headers, json=data)
        cls.admin = cls.db.query(Admin).filter_by(username=cls.adminUsername).first()
        adminLoginData = {
            "username": cls.adminUsername,
            "password": cls.password
        }
        response = client.post("/auth/login", data=adminLoginData)
        res = response.json()
        cls.adminToken = res["access_token"]
        data = {
            "username": cls.editorUsername,
            "email": cls.editorEmail,
            "password": cls.password
        }
        cls.adminHeaders = {
            "Authorization": f"Bearer {cls.adminToken}"
        }
        
        response = client.post("/auth/signup", headers=cls.adminHeaders, json=data)
        print(response.json())
        cls.editor = cls.db.query(Admin).filter_by(username=cls.editorUsername).first()
        editorLoginData = {
            "username": cls.editorUsername,
            "password": cls.password
        }
        response = client.post("/auth/login", data=editorLoginData)
        res = response.json()
        cls.editorToken = res["access_token"]
        cls.editorHeaders = {
            "Authorization": f"Bearer {cls.editorToken}"
        }

    @classmethod
    def tearDownClass(cls) -> None:
        print("teardown class")
        if cls.admin is not None:
            cls.db.delete(cls.admin)
            cls.db.delete(cls.editor)
            cls.db.commit()