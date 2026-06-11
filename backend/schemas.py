from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class LoginRequest(BaseModel):
    username: str
    password: str


class BatchDeleteRequest(BaseModel):
    ids: List[int]


class LoginResponse(BaseModel):
    token: str


class ArticleBase(BaseModel):
    title: str
    content: str
    excerpt: Optional[str] = ""
    category_id: Optional[int] = None
    tags: Optional[str] = ""
    created_at: Optional[str] = None


class ArticleCreate(ArticleBase):
    pass


class ArticleUpdate(ArticleBase):
    pass


class ArticleResponse(ArticleBase):
    id: int
    category_name: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CategoryCreate(BaseModel):
    name: str


class CategoryUpdate(BaseModel):
    name: str


class CategoryResponse(BaseModel):
    id: int
    name: str
    count: int = 0

    class Config:
        from_attributes = True


class TagResponse(BaseModel):
    id: int
    name: str
    count: int = 0

    class Config:
        from_attributes = True


class TagCreate(BaseModel):
    name: str


class TagUpdate(BaseModel):
    name: str


class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    bio: Optional[str] = None
    skills: Optional[str] = None
    email: Optional[str] = None
    github: Optional[str] = None


class ApiResponse(BaseModel):
    code: int
    data: Optional[dict | list] = None
    msg: str = ""
