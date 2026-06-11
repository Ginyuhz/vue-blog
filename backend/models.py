from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), default="博主")
    bio = Column(Text, default="")
    skills = Column(String(500), default="")
    email = Column(String(100), default="")
    github = Column(String(200), default="")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    articles = relationship("Article", back_populates="category")


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    excerpt = Column(String(500))
    category_id = Column(Integer, ForeignKey("categories.id"))
    tags = Column(String(200))
    status = Column(Integer, default=1)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    category = relationship("Category", back_populates="articles")
