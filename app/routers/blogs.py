#!/usr/bin/env python3

""" Module containaning routes returning data for the blogs on the landing page """

from fastapi import HTTPException, APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer

from app.dependencies.database import get_db
from app.dependencies.error import httpError
from app.dependencies.auth_dependencies import validate_admin, get_admin
from app.models.blogs import Blog, BlogUploadSchema, BlogUpdateSchema, SingleBlogResponse, MultipleBlogsResponse


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

router = APIRouter(tags=["Blogs"])


@router.post("/blogs/new", status_code=201, response_model=SingleBlogResponse)
async def upload_blog(token: Annotated[str, Depends(oauth2_scheme)],
                      blog: BlogUploadSchema,
                      db: Session = Depends(get_db)):
    """
    Create a new blog as a draft or published blog
    """
    try:
        id = validate_admin(token)
        admin = get_admin(id, db)
        if admin is None:
            raise httpError(status_code=404, detail="Admin not found")
        if not admin.is_active:
            raise httpError(status_code=403, detail="You cannot access this resource because your account is not activated")
        if not admin.permissions["create"]:
            raise httpError(status_code=403, detail="You do not have permission to create this resource")

        blogDict = blog.model_dump()
        blogDict['author'] = admin.username
        blogDict['author_id'] = admin.id
        if blogDict.get("status") == "deleted":
                raise httpError(status_code=400, detail="You cannot create a deleted blog")
        if not len(blogDict.get("title")) or not len(blogDict.get("content")) or not len(blogDict.get("status")):
            if blogDict.get("status") == "published":
                raise httpError(status_code=400, detail="To publish a blog, the title and content fields need to be filled")
            elif blogDict.get("status") == "draft":
                pass
            else:
                raise httpError(status_code=400, detail="Invalid blog status. Status must be either 'draft' or 'published'")

        newBlog = Blog(**blogDict)
        newBlog.save(db)
        if newBlog.status == "published":
            return {
                "success": True,
                "message": "Blog post published successfully",
                "data": newBlog.to_dict(),
            }
        elif newBlog.status == "draft":
            return {
                "success": True,
                "message": "Blog post saved to draft successfully",
                "data": newBlog.to_dict(),
            }
    except Exception as e:
        print(str(e))
        if isinstance(e, HTTPException):
            raise e
        raise httpError(status_code=500, detail=str(e))


@router.get("/blogs/published/all", response_model=MultipleBlogsResponse)
async def get_published_blogs(db: Session = Depends(get_db)):
    """
    Retrieves all published blogs from the database
    """
    try:
        publishedBlogs = db.query(Blog).filter_by(status = "published").all()
        publishedBlogs = list(map(lambda x: x.to_dict(), publishedBlogs))
        return {
            "success": True,
            "message": "Published blogs retrieved successfully",
            "data": {
                "count": len(publishedBlogs),
                "blogs": publishedBlogs
            }
        }
    except Exception as e:
        print(str(e))
        if isinstance(e, HTTPException):
            raise e
        raise httpError(status_code=500, detail=str(e))


@router.get("/blogs/drafts/all", response_model=MultipleBlogsResponse)
async def get_drafted_blogs(token: Annotated[str, Depends(oauth2_scheme)],
                            db: Session = Depends(get_db)):
    """
    Retrieves all drafted and unpublished blogs from the database
    """
    try:
        id = validate_admin(token)
        admin = get_admin(id, db)
        if admin is None:
            raise httpError(status_code=404, detail="Admin not found")
        if not admin.is_active:
            raise httpError(status_code=403, detail="You cannot access this resource because your account is not activated")
        draftedBlogs = db.query(Blog).filter_by(status = "draft").all()
        draftedBlogs = list(map(lambda x: x.to_dict(), draftedBlogs))
        return {
            "success": True,
            "message": "Drafted blogs retrieved successfully",
            "data": {
                "count": len(draftedBlogs),
                "blogs": draftedBlogs
            }
        }
    except Exception as e:
        print(str(e))
        if isinstance(e, HTTPException):
            raise e
        raise httpError(status_code=500, detail=str(e))


@router.get("/blogs/deleted/all", response_model=MultipleBlogsResponse)
async def get_deleted_blogs(token: Annotated[str, Depends(oauth2_scheme)],
                            db: Session = Depends(get_db)):
    """
    Retrieves all deleted blogs from the database
    """
    try:
        id = validate_admin(token)
        admin = get_admin(id, db)
        if admin is None:
            raise httpError(status_code=404, detail="Admin not found")
        if not admin.is_active:
            raise httpError(status_code=403, detail="You cannot access this resource because your account is not activated")
        deletedBlogs = db.query(Blog).filter_by(status = "deleted").all()
        deletedBlogs = list(map(lambda x: x.to_dict(), deletedBlogs))
        return {
            "success": True,
            "message": "Deleted blogs retrieved successfully",
            "data": {
                "count": len(deletedBlogs),
                "blogs": deletedBlogs
            }
        }
    except Exception as e:
        print(str(e))
        if isinstance(e, HTTPException):
            raise e
        raise httpError(status_code=500, detail=str(e))
    

@router.put("/blogs/{blog_id}/update", response_model=SingleBlogResponse)
async def update_blog(token: Annotated[str, Depends(oauth2_scheme)],
                      blog_id: str,
                      blog: BlogUpdateSchema,
                      db: Session = Depends(get_db)):
    """
    Update a blog post
    """
    try:
        id = validate_admin(token)
        admin = get_admin(id, db)
        if admin is None:
            raise httpError(status_code=404, detail="Admin not found")
        if not admin.is_active:
            raise httpError(status_code=403, detail="You cannot access this resource because your account is not activated")
        if not admin.permissions["update"]:
            raise httpError(status_code=403, detail="You do not have permission to update this resource")
        blogDict = blog.model_dump()
        oldBlog: Blog = db.query(Blog).filter_by(id = blog_id).first()
        if admin.id != oldBlog.author_id and admin.role != "admin" and admin.role != "superuser":
            raise httpError(status_code=403, detail="You are not authorized to update this blog")
        if oldBlog is None:
            raise httpError(status_code=404, detail="Blog not found")
        if oldBlog.status == "deleted":
            raise httpError(status_code=400, detail="Blog has been deleted")
        if blogDict.get("status") == "deleted":
            raise httpError(status_code=400, detail="To delete a blog, use the delete endpoint")
        if not len(blogDict.get("title")) or not len(blogDict.get("content")) or not len(blogDict.get("status")):
            if blogDict.get("status") == "published":
                raise httpError(status_code=400, detail="To publish a blog, the title and content fields need to be filled")
            elif blogDict.get("status") == "draft":
                if oldBlog.status == "draft":
                    pass
                elif oldBlog.status == "published":
                    raise httpError(status_code=400, detail="You cannot convert an already published blog into a draft")
            else:
                raise httpError(status_code=400, detail="Required fields not filled correctly")
        if oldBlog.status == "published" and blogDict.get("status") == "draft":
            raise httpError(status_code=400, detail="You cannot convert an already published blog into a draft")
        print("to update {}, id {}".format(blogDict, oldBlog.id))
        oldBlog.update(db, **blogDict)

        newBlog: Blog = db.query(Blog).filter_by(id = blog_id).first()
        return {
            "success": True,
            "message": "Blog post updated successfully",
            "data": newBlog.to_dict(),
        }
    except Exception as e:
        print(str(e))
        if isinstance(e, HTTPException):
            raise e
        raise httpError(status_code=500, detail=str(e))
    

@router.delete("/blogs/{blog_id}/delete", status_code=204)
async def delete_blog(token: Annotated[str, Depends(oauth2_scheme)],
                      blog_id: str,
                      db: Session = Depends(get_db)):
    """
    Delete a blog post
    """
    try:
        id = validate_admin(token)
        admin = get_admin(id, db)
        if admin is None:
            raise httpError(status_code=404, detail="Admin not found")
        if not admin.is_active:
            raise httpError(status_code=403, detail="You cannot access this resource because your account is not activated")
        if not admin.permissions["delete"]:
            raise httpError(status_code=403, detail="You do not have permission to delete this resource")
        blog = db.query(Blog).filter_by(id = blog_id).first()
        if blog is None:
            raise httpError(status_code=404, detail="Blog not found")
        if admin.id != blog.author_id and admin.role != "superuser":
            raise httpError(status_code=403, detail="You are not authorized to delete this blog")
        if blog.status == "deleted":
            raise httpError(status_code=400, detail="Blog has been deleted")
        blog.update(db, status="deleted")
        return {
            "success": True,
            "message": "Blog post deleted successfully",
            "data": None
        }
    except Exception as e:
        print(str(e))
        if isinstance(e, HTTPException):
            raise e
        raise httpError(status_code=500, detail=str(e))