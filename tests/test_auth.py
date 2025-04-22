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

class SuperuserSignupTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls) -> None:
        # using random.choices()
        # generating random strings
        cls.username = ''.join(random.choices(string.ascii_lowercase, k=7))
        cls.email = f"{cls.username}@gmail.com"
        cls.password = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        cls.db_gen = get_db()
        cls.db = next(cls.db_gen)
        cls.admin = None

    @classmethod
    def tearDownClass(cls) -> None:
        print("teardown class")
        if cls.admin is not None:
            db = cls.db
            db.delete(cls.admin)
            db.commit()

    def test_create_super_admin(self):

        data = {
            "username": self.username,
            "email": self.email,
            "password": self.password
        }
        headers = {
            "Authorization": os.getenv("SUPER_ADMIN_SECRET")
        }
        response = client.post("/auth/super-admin/signup", headers=headers, json=data)

        self.assertEqual(response.status_code, 201)
        admin: dict = response.json()["data"]
        # Verify that the admin is stored in the database
        SuperuserSignupTest.admin = self.db.query(Admin).filter_by(username=self.username).first()
        self.assertIsNotNone(self.admin)
        self.assertEqual(self.username, admin["username"])
        self.assertEqual(self.email, admin["email"])
        self.assertEqual("superuser", admin["role"])
        self.assertEqual(self.username, self.admin.username)
        self.assertEqual(self.email, self.admin.email)
        self.assertTrue(response.json()["success"])
    
    def test_create_super_admin_with_no_header(self):

        data = {
            "username": self.username,
            "email": self.email,
            "password": self.password
        }
        response = client.post("/auth/super-admin/signup", json=data)
        self.assertEqual(response.status_code, 401)
        res: dict = response.json()
        self.assertEqual(res["detail"]["message"], "Authorization header is required")
        self.assertFalse(res["detail"]["success"])
    
    def test_create_super_admin_with_no_username(self):

        data = {
            "email": self.email,
            "password": self.password
        }
        headers = {
            "Authorization": os.getenv("SUPER_ADMIN_SECRET")
        }

        # Send a POST request to create an admin
        response = client.post("/auth/super-admin/signup", headers=headers, json=data)
        self.assertEqual(response.status_code, 422)
        data["username"] = ""
        response = client.post("/auth/super-admin/signup", headers=headers, json=data)
        self.assertEqual(response.status_code, 400)
        res: dict = response.json()
        self.assertEqual(res["detail"]["message"], "Admin username is required")
        self.assertFalse(res["detail"]["success"])
    
    def test_create_super_admin_duplicate(self):

        data = {
            "username": self.username,
            "email": self.email,
            "password": self.password
        }
        headers = {
            "Authorization": os.getenv("SUPER_ADMIN_SECRET")
        }

        # Send a POST request to create an admin
        response = client.post("/auth/super-admin/signup", headers=headers, json=data)
        self.assertEqual(response.status_code, 400)
        res: dict = response.json()
        self.assertEqual(res["detail"]["message"], "Admin already exists")
        self.assertFalse(res["detail"]["success"])


class AdminLoginTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # using random.choices()
        # generating random strings
        cls.username = ''.join(random.choices(string.ascii_lowercase, k=7))
        cls.email = f"{cls.username}@gmail.com"
        cls.password = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        cls.db_gen = get_db()
        cls.db = next(cls.db_gen)
        data = {
            "username": cls.username,
            "email": cls.email,
            "password": cls.password
        }
        headers = {
            "Authorization": os.getenv("SUPER_ADMIN_SECRET")
        }
        client.post("/auth/super-admin/signup", headers=headers, json=data)
        cls.admin = cls.db.query(Admin).filter_by(username=cls.username).first()

    @classmethod
    def tearDownClass(cls) -> None:
        print("teardown class")
        if cls.admin is not None:
            cls.db.delete(cls.admin)
            cls.db.commit()
    
    def setUp(self) -> None:
        self.db = get_db()
    
    def test_login(self):
        loginData = {
            "username": self.username,
            "password": self.password
        }
        response = client.post("/auth/login", data=loginData)
        res = response.json()
        print(res)
        id = res["data"]["id"]
        self.assertEqual(response.status_code, 200)
        self.assertTrue(res["success"])
        token = res["access_token"]
        auth = {
            "Authorization": f"Bearer {token}"
        }
        response = client.get("/admins/me", headers=auth)
        self.assertEqual(response.status_code, 200)
        res = response.json()
        self.assertTrue(res["success"])
        self.assertEqual(self.username, res["data"]["username"])
        self.assertEqual(self.email, res["data"]["email"])
        self.assertEqual("superuser", res["data"]["role"])
        self.assertEqual(id, res["data"]["id"])
        self.assertEqual(self.username, self.admin.username)
        self.assertEqual(self.email, self.admin.email)

    def test_login_with_wrong_password(self):
        loginData = {
            "username": self.username,
            "password": "wrongpassword"
        }
        response = client.post("/auth/login", data=loginData)
        res = response.json()
        self.assertEqual(response.status_code, 401)
        self.assertFalse(res["detail"]["success"])
        self.assertEqual(res["detail"]["message"], "Invalid credentials")
    
    def test_login_with_wrong_username(self):
        loginData = {
            "username": "wrongusername",
            "password": self.password
        }
        response = client.post("/auth/login", data=loginData)
        res = response.json()
        self.assertEqual(response.status_code, 401)
        self.assertFalse(res["detail"]["success"])
        self.assertEqual(res["detail"]["message"], "Invalid credentials")
    
    def test_login_with_no_username(self):
        loginData = {
            "password": self.password
        }
        response = client.post("/auth/login", data=loginData)
        self.assertEqual(response.status_code, 422)
        loginData["username"] = ""
        response = client.post("/auth/login", data=loginData)
        self.assertEqual(response.status_code, 422)

class EditorSignupTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls) -> None:
        # using random.choices()
        # generating random strings
        cls.username = ''.join(random.choices(string.ascii_lowercase, k=7))
        cls.email = f"{cls.username}@gmail.com"
        cls.editorUsername = ''.join(random.choices(string.ascii_lowercase, k=7))
        cls.editorEmail = f"{cls.editorUsername}@gmail.com"
        cls.password = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        cls.db_gen = get_db()
        cls.db = next(cls.db_gen)
        cls.editor = None
        data = {
            "username": cls.username,
            "email": cls.email,
            "password": cls.password
        }
        headers = {
            "Authorization": os.getenv("SUPER_ADMIN_SECRET")
        }
        client.post("/auth/super-admin/signup", headers=headers, json=data)
        cls.admin = cls.db.query(Admin).filter_by(username=cls.username).first()

    @classmethod
    def tearDownClass(cls) -> None:
        print("teardown class")
        if cls.admin is not None:
            cls.db.delete(cls.admin)
            cls.db.delete(cls.editor)
            cls.db.commit()
    
    def setUp(self) -> None:
        loginData = {
            "username": self.username,
            "password": self.password
        }
        response = client.post("/auth/login", data=loginData)
        res = response.json()
        self.token = res["access_token"]

    def test_create_admin(self):

        data = {
            "username": self.editorUsername,
            "email": self.editorEmail,
            "password": self.password
        }
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        response = client.post("/auth/signup", headers=headers, json=data)

        self.assertEqual(response.status_code, 201)
        admin: dict = response.json()["data"]
        # Verify that the Admin is stored in the database
        EditorSignupTest.editor = self.db.query(Admin).filter_by(username=self.editorUsername).first()
        self.assertIsNotNone(self.admin)
        self.assertEqual(self.editorUsername, admin["username"])
        self.assertEqual(self.editorEmail, admin["email"])
        self.assertEqual("editor", admin["role"])
        self.assertEqual(self.editorUsername, self.editor.username)
        self.assertEqual(self.editorEmail, self.editor.email)
        self.assertTrue(response.json()["success"])
    
    def test_create_admin_with_no_header(self):

        data = {
            "username": self.editorUsername,
            "email": self.editorEmail,
            "password": self.password
        }
        response = client.post("/auth/signup", json=data)
        self.assertEqual(response.status_code, 401)
        res: dict = response.json()
        print(f"Response: {res}")
        self.assertEqual(res["detail"], "Not authenticated")
    
    def test_create_admin_with_no_username(self):

        data = {
            "email": self.editorEmail,
            "password": self.password
        }
        headers = {
            "Authorization": f"Bearer {self.token}"
        }

        # Send a POST request to create an admin
        response = client.post("/auth/signup", headers=headers, json=data)
        self.assertEqual(response.status_code, 422)
        data["username"] = ""
        response = client.post("/auth/signup", headers=headers, json=data)
        self.assertEqual(response.status_code, 400)
        res: dict = response.json()
        self.assertEqual(res["detail"]["message"], "Admin username is required")
        self.assertFalse(res["detail"]["success"])
    
    def test_create_admin_duplicate(self):

        data = {
            "username": self.editorUsername,
            "email": self.editorEmail,
            "password": self.password
        }
        headers = {
            "Authorization": f"Bearer {self.token}"
        }

        # Send a POST request to create an admin
        response = client.post("/auth/signup", headers=headers, json=data)
        self.assertEqual(response.status_code, 400)
        res: dict = response.json()
        self.assertEqual(res["detail"]["message"], "Admin already exists")
        self.assertFalse(res["detail"]["success"])

if "__name__" == "__main__":
    unittest.main()