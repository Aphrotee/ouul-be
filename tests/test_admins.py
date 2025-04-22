#!/usr/bin/env python3

from app.main import app
from fastapi.testclient import TestClient
from tests.tests_base import TestsBase


client = TestClient(app)

class AdminsTest(TestsBase):    
    def test_admin_a_deactivation(self):
        response = client.put(f"/admins/{self.editor.id}/deactivate", headers=self.adminHeaders)
        self.assertEqual(response.status_code, 200)
        res = response.json()
        self.assertTrue(res["success"])
        self.assertEqual(res["message"], "Admin account deactivated successfully")
        self.assertFalse(res["data"]["is_active"])
        response = client.put(f"/admins/{self.editor.id}/deactivate", headers=self.adminHeaders)
        self.assertEqual(response.status_code, 200)
        res = response.json()
        self.assertTrue(res["success"])
        self.assertEqual(res["message"], "Admin account already deactivated")
        response = client.get(f"/admins/me/status", headers=self.editorHeaders)
        res = response.json()
        self.assertTrue(res["success"])
        self.assertEqual(res["message"], "Your account is deactivated")
        self.assertFalse(res["data"])
        response = client.get(f"/admins/all", headers=self.editorHeaders)
        res = response.json()
        self.assertFalse(res["detail"]["success"])
        self.assertEqual(response.status_code, 403)
        self.assertEqual(res["detail"]["message"], "You cannot access this resource because your account is not activated")

    def test_admin_activation(self):
        response = client.put(f"/admins/{self.editor.id}/activate", headers=self.adminHeaders)
        self.assertEqual(response.status_code, 200)
        res = response.json()
        self.assertTrue(res["success"])
        self.assertEqual(res["message"], "Admin account activated successfully")
        self.assertTrue(res["data"]["is_active"])
        response = client.put(f"/admins/{self.editor.id}/activate", headers=self.adminHeaders)
        self.assertEqual(response.status_code, 200)
        res = response.json()
        self.assertTrue(res["success"])
        self.assertEqual(res["message"], "Admin account already activated")
        response = client.get(f"/admins/me/status", headers=self.editorHeaders)
        res = response.json()
        self.assertTrue(res["success"])
        self.assertEqual(res["message"], "Your account is activated")
        self.assertTrue(res["data"])

    def test_admin_deactivation_by_editor(self):
        response = client.put(f"/admins/{self.admin.id}/deactivate", headers=self.editorHeaders)
        self.assertEqual(response.status_code, 403)
        res = response.json()
        self.assertFalse(res["detail"]["success"])
        self.assertEqual(res["detail"]["message"], "You don't have access to this resource")

    def test_admin_deactivation_of_superuser(self):
        response = client.put(f"/admins/{self.admin.id}/deactivate", headers=self.adminHeaders)
        self.assertEqual(response.status_code, 403)
        res = response.json()
        self.assertFalse(res["detail"]["success"])
        self.assertEqual(res["detail"]["message"], "An superuser cannot activate/deactivate another Superuser")
