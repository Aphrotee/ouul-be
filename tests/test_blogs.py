#!/usr/bin/env python3

import unittest
from app.main import app
from fastapi.testclient import TestClient
from app.models.blogs import Blog
from tests.tests_base import TestsBase


client = TestClient(app)

class BlogsTest(TestsBase):
    def deleteRow(self, row):
        """Delete a row used in this testcase from the database"""
        self.db.delete(row)
        self.db.commit()

    def test_create_blog(self):
        blogData = {
            "title": "Test Blog",
            "content": "This is a test published blog",
            "status": "published",
            "tags": []
        }
        response = client.post("/blogs/new", json=blogData, headers=self.adminHeaders)
        data = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["message"], "Blog post published successfully")
        publishedBlog = self.db.query(Blog).filter(Blog.id == data["data"]["id"]).first()
        self.assertIsNotNone(publishedBlog)
        self.assertEqual(data["data"]["id"], publishedBlog.id)
        self.assertEqual(publishedBlog.title, blogData["title"])
        self.assertEqual(publishedBlog.status, "published")
        blogData["content"] = "This is a test draft blog"
        blogData["status"] = "draft"
        response = client.post("/blogs/new", json=blogData, headers=self.adminHeaders)
        data = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertTrue(data["success"])
        self.assertEqual(data["message"], "Blog post saved to draft successfully")
        draftedBlog = self.db.query(Blog).filter(Blog.id == data["data"]["id"]).first()
        self.assertIsNotNone(draftedBlog)
        self.assertEqual(data["data"]["id"], draftedBlog.id)
        self.assertEqual(draftedBlog.title, blogData["title"])
        self.assertEqual(draftedBlog.status, "draft")
        self.deleteRow(draftedBlog)
        self.deleteRow(publishedBlog)
    
    def test_create_blog_with_incomplete_parameters(self):
        """Test creating a blog with incomplete parameters"""
        blogData = {
            "title": "",
            "content": "This is a test published blog",
            "status": "published",
            "tags": []
        }
        response = client.post("/blogs/new", json=blogData, headers=self.adminHeaders)
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertFalse(data["detail"]["success"])
        self.assertEqual(data["detail"]["message"], "To publish a blog, the title and content fields need to be filled")
    
    def test_create_blog_with_invalid_status(self):
        """Test creating a blog with an invalid status"""
        blogData = {
            "title": "Test Blog",
            "content": "This is a test published blog",
            "status": "invalid",
            "tags": []
        }
        response = client.post("/blogs/new", json=blogData, headers=self.adminHeaders)
        data = response.json()
        print(data)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data["detail"][0]["msg"], "Input should be 'draft', 'published' or 'deleted'")
    
    def test_create_blog_with_delete_status(self):
        """Test creating a blog with a delete status"""
        blogData = {
            "title": "Test Blog",
            "content": "This is a test published blog",
            "status": "deleted",
            "tags": []
        }
        response = client.post("/blogs/new", json=blogData, headers=self.adminHeaders)
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertFalse(data["detail"]["success"])
        self.assertEqual(data["detail"]["message"], "You cannot create a deleted blog")
    
    # def test_update_draft_blog(self):
    #     """Test updating a blog"""
    #     blogData = {
    #         "title": "Test Blog",
    #         "content": "This is a test draft blog",
    #         "status": "draft",
    #         "tags": []
    #     }
    #     response = client.post("/blogs/new", json=blogData, headers=self.adminHeaders)
    #     data = response.json()
    #     self.assertEqual(response.status_code, 201)
    #     self.assertTrue(data["success"])
    #     self.assertEqual(data["message"], "Blog post saved to draft successfully")
    #     draftedBlog = self.db.query(Blog).filter(Blog.id == data["data"]["id"]).first()
    #     self.assertIsNotNone(draftedBlog)
    #     self.assertEqual(data["data"]["id"], draftedBlog.id)
    #     self.assertEqual(draftedBlog.title, blogData["title"])
    #     self.assertEqual(draftedBlog.status, "draft")
    #     blogData["content"] = "This is an updated test draft blog"
    #     blogData["status"] = "draft"
    #     response = client.put(f"/blogs/{draftedBlog.id}/update", json=blogData, headers=self.adminHeaders)
    #     data = response.json()
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTrue(data["success"])
    #     self.assertEqual(data["message"], "Blog post updated successfully")
    #     self.updatedBlog = self.db.query(Blog).filter(Blog.id == draftedBlog.id).first()
    #     self.assertIsNotNone(self.updatedBlog)
    #     self.assertEqual(data["data"]["id"], self.updatedBlog.id)
    #     self.assertEqual(self.updatedBlog.title, blogData["title"])
    #     self.assertEqual(self.updatedBlog.status, "draft")
    
    # def test_update_published_blog_by_admin(self):
    #     draftedBlog = self.updatedBlog
    #     blogData = {
    #         "title": draftedBlog.title,
    #         "content": draftedBlog.content,
    #         "status": "published",
    #         "author_id": draftedBlog.author_id,
    #         "tags": draftedBlog.tags
    #     }
    #     response = client.put(f"/blogs/{draftedBlog.id}/update", json=blogData, headers=self.adminHeaders)
    #     data = response.json()
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTrue(data["success"])
    #     self.assertEqual(data["message"], "Blog post updated successfully")
    #     updatedBlog = self.db.query(Blog).filter(Blog.id == draftedBlog.id).first()
    #     self.assertIsNotNone(updatedBlog)
    #     self.assertEqual(data["data"]["id"], updatedBlog.id)
    #     self.assertEqual(updatedBlog.title, blogData["title"])
    #     self.assertEqual(updatedBlog.status, "published")
    #     blogData["content"] = "This is an updated test published blog"
    #     response = client.put(f"/blogs/{updatedBlog.id}/update", json=blogData, headers=self.adminHeaders)
    #     data = response.json()
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTrue(data["success"])
    #     self.assertEqual(data["message"], "Blog post updated successfully")
    #     self.updatedBlog = self.db.query(Blog).filter(Blog.id == draftedBlog.id).first()
    #     self.assertIsNotNone(self.updatedBlog)
    #     self.assertEqual(data["data"]["id"], self.updatedBlog.id)
    #     self.assertEqual(self.updatedBlog.title, blogData["title"])
    #     self.assertEqual(self.updatedBlog.status, "published")
    #     response = client.put(f"/blogs/{updatedBlog.id}", json=blogData, headers=self.adminHeaders)
    #     data = response.json()
    #     self.assertEqual(response.status_code, 400)
    #     self.assertFalse(data["detail"]["success"])
    #     self.assertEqual(data["detail"]["message"], "You cannot convert an already published blog into a draft")
    #     self.deleteRow(self.updatedBlog)


if "__name__" == "__main__":
    unittest.main()