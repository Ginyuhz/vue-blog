from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.sql import func
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./blog.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
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

Base.metadata.create_all(bind=engine)

# Auth setup
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

# Schemas
class LoginRequest(BaseModel):
    username: str
    password: str

class BatchDeleteRequest(BaseModel):
    ids: List[int]

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

class CategoryCreate(BaseModel):
    name: str

class CategoryUpdate(BaseModel):
    name: str

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

# FastAPI app
app = FastAPI(title="Vue Blog API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def api_response(code: int = 200, data=None, msg: str = ""):
    return {"code": code, "data": data, "msg": msg}

async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的认证信息")
    username = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的认证信息")
    admin = db.query(Admin).filter(Admin.username == username).first()
    if admin is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")
    return admin

# Routes
@app.get("/")
async def root():
    return {"message": "Vue Blog API"}

@app.post("/api/login", response_model=ApiResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.username == request.username).first()
    if not admin or not verify_password(request.password, admin.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    token = create_access_token(data={"sub": admin.username})
    return api_response(data={"token": token})

@app.get("/api/article/list", response_model=ApiResponse)
async def get_articles(category_id: int = None, tag: str = None, keyword: str = None, db: Session = Depends(get_db)):
    query = db.query(Article).filter(Article.status == 1)
    if category_id:
        query = query.filter(Article.category_id == category_id)
    if tag:
        query = query.filter(Article.tags.contains(tag))
    if keyword:
        query = query.filter((Article.title.contains(keyword)) | (Article.content.contains(keyword)) | (Article.excerpt.contains(keyword)))
    articles = query.order_by(Article.created_at.desc()).all()
    result = []
    for article in articles:
        category_name = None
        if article.category_id:
            category = db.query(Category).filter(Category.id == article.category_id).first()
            category_name = category.name if category else None
        result.append({
            "id": article.id, "title": article.title, "content": article.content,
            "excerpt": article.excerpt, "category_id": article.category_id,
            "category_name": category_name, "tags": article.tags,
            "created_at": article.created_at.strftime("%Y/%m/%d %H:%M:%S") if article.created_at else None
        })
    return api_response(data=result)

@app.get("/api/article/{article_id}", response_model=ApiResponse)
async def get_article(article_id: int, db: Session = Depends(get_db)):
    article = db.query(Article).filter(Article.id == article_id, Article.status == 1).first()
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    category_name = None
    if article.category_id:
        category = db.query(Category).filter(Category.id == article.category_id).first()
        category_name = category.name if category else None
    return api_response(data={
        "id": article.id, "title": article.title, "content": article.content,
        "excerpt": article.excerpt, "category_id": article.category_id,
        "category_name": category_name, "tags": article.tags, "created_at": article.created_at
    })

@app.post("/api/article", response_model=ApiResponse)
async def create_article(article: ArticleCreate, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    created_at = None
    if article.created_at:
        for fmt in ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y/%m/%d"]:
            try:
                created_at = datetime.strptime(article.created_at, fmt)
                break
            except ValueError:
                continue
    db_article = Article(title=article.title, content=article.content, excerpt=article.excerpt,
                         category_id=article.category_id, tags=article.tags, created_at=created_at)
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return api_response(data={"id": db_article.id}, msg="创建成功")

@app.put("/api/article/{article_id}", response_model=ApiResponse)
async def update_article(article_id: int, article: ArticleUpdate, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    db_article = db.query(Article).filter(Article.id == article_id).first()
    if not db_article:
        raise HTTPException(status_code=404, detail="文章不存在")
    db_article.title = article.title
    db_article.content = article.content
    db_article.excerpt = article.excerpt
    db_article.category_id = article.category_id
    db_article.tags = article.tags
    db.commit()
    db.refresh(db_article)
    return api_response(data={"id": db_article.id}, msg="更新成功")

@app.delete("/api/article/{article_id}", response_model=ApiResponse)
async def delete_article(article_id: int, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    db_article = db.query(Article).filter(Article.id == article_id).first()
    if not db_article:
        raise HTTPException(status_code=404, detail="文章不存在")
    category_id = db_article.category_id
    tags = db_article.tags.split(',') if db_article.tags else []
    db.delete(db_article)
    
    if category_id:
        remaining = db.query(Article).filter(Article.category_id == category_id, Article.id != article_id).count()
        if remaining == 0:
            db_category = db.query(Category).filter(Category.id == category_id).first()
            if db_category:
                db.delete(db_category)
    
    for tag_name in tags:
        if tag_name.strip():
            tag = db.query(Tag).filter(Tag.name == tag_name.strip()).first()
            if tag:
                remaining = db.query(Article).filter(Article.tags.contains(tag_name.strip())).count()
                if remaining <= 1:
                    db.delete(tag)
    db.commit()
    return api_response(msg="删除成功")

@app.post("/api/article/batch-delete", response_model=ApiResponse)
async def batch_delete_articles(request: BatchDeleteRequest, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    ids = request.ids
    if not ids:
        raise HTTPException(status_code=400, detail="请选择要删除的文章")
    success_list = []
    fail_list = []
    deleted_category_ids = set()
    deleted_tag_names = set()
    
    for article_id in ids:
        article = db.query(Article).filter(Article.id == article_id).first()
        if article:
            if article.category_id:
                deleted_category_ids.add(article.category_id)
            tags = article.tags.split(',') if article.tags else []
            for t in tags:
                if t.strip():
                    deleted_tag_names.add(t.strip())
            db.delete(article)
            success_list.append({"id": article_id, "title": article.title})
        else:
            fail_list.append({"id": article_id, "reason": "文章不存在"})
    db.commit()
    
    for cat_id in deleted_category_ids:
        remaining = db.query(Article).filter(Article.category_id == cat_id).count()
        if remaining == 0:
            db_category = db.query(Category).filter(Category.id == cat_id).first()
            if db_category:
                db.delete(db_category)
    
    for tag_name in deleted_tag_names:
        tag = db.query(Tag).filter(Tag.name == tag_name).first()
        if tag:
            remaining = db.query(Article).filter(Article.tags.contains(tag_name)).count()
            if remaining == 0:
                db.delete(tag)
    db.commit()
    
    return api_response(data={"success": success_list, "fail": fail_list}, msg=f"删除成功 {len(success_list)} 篇，失败 {len(fail_list)} 篇")

@app.get("/api/category", response_model=ApiResponse)
async def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).all()
    result = []
    for cat in categories:
        count = db.query(Article).filter(Article.category_id == cat.id, Article.status == 1).count()
        result.append({"id": cat.id, "name": cat.name, "count": count})
    return api_response(data=result)

@app.post("/api/category", response_model=ApiResponse)
async def create_category(request: CategoryCreate, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    existing = db.query(Category).filter(Category.name == request.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="分类已存在")
    category = Category(name=request.name)
    db.add(category)
    db.commit()
    db.refresh(category)
    return api_response(data={"id": category.id, "name": category.name}, msg="创建成功")

@app.put("/api/category/{category_id}", response_model=ApiResponse)
async def update_category(category_id: int, request: CategoryUpdate, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    existing = db.query(Category).filter(Category.name == request.name, Category.id != category_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="分类名已存在")
    category.name = request.name
    db.commit()
    db.refresh(category)
    return api_response(data={"id": category.id, "name": category.name}, msg="更新成功")

@app.delete("/api/category/{category_id}", response_model=ApiResponse)
async def delete_category(category_id: int, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    count = db.query(Article).filter(Article.category_id == category_id).count()
    if count > 0:
        raise HTTPException(status_code=400, detail="该分类下存在文章，无法删除")
    db.delete(category)
    db.commit()
    return api_response(msg="删除成功")

@app.get("/api/tag", response_model=ApiResponse)
async def get_tags(db: Session = Depends(get_db)):
    tags = db.query(Tag).all()
    result = []
    for t in tags:
        count = db.query(Article).filter(Article.tags.contains(t.name), Article.status == 1).count()
        result.append({"id": t.id, "name": t.name, "count": count})
    return api_response(data=result)

@app.post("/api/tag", response_model=ApiResponse)
async def create_tag(request: TagCreate, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    existing = db.query(Tag).filter(Tag.name == request.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="标签已存在")
    tag = Tag(name=request.name)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return api_response(data={"id": tag.id, "name": tag.name, "count": 0}, msg="创建成功")

@app.put("/api/tag/{tag_id}", response_model=ApiResponse)
async def update_tag(tag_id: int, request: TagUpdate, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")
    existing = db.query(Tag).filter(Tag.name == request.name, Tag.id != tag_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="标签名称已存在")
    tag.name = request.name
    db.commit()
    db.refresh(tag)
    return api_response(data={"id": tag.id, "name": tag.name, "count": 0}, msg="更新成功")

@app.delete("/api/tag/{tag_id}", response_model=ApiResponse)
async def delete_tag(tag_id: int, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")
    db.delete(tag)
    db.commit()
    return api_response(msg="删除成功")

@app.post("/api/init", response_model=ApiResponse)
async def init_database(db: Session = Depends(get_db)):
    admin = db.query(Admin).first()
    if not admin:
        admin = Admin(username="admin", password_hash=get_password_hash("admin123"))
        db.add(admin)
    categories = db.query(Category).all()
    if not categories:
        default_categories = ["前端", "后端", "DevOps", "随笔"]
        for name in default_categories:
            db.add(Category(name=name))
    tags = db.query(Tag).all()
    if not tags:
        default_tags = ["Vue", "JavaScript", "Python", "CSS", "Node.js", "FastAPI"]
        for name in default_tags:
            db.add(Tag(name=name))
    db.commit()
    return api_response(msg="初始化成功")

@app.get("/api/profile", response_model=ApiResponse)
async def get_profile(db: Session = Depends(get_db)):
    profile = db.query(Profile).first()
    if not profile:
        profile = Profile(name="博主", bio="一名热爱技术的前端开发者，专注于 Vue、React 等现代前端技术。\n\n在这里分享学习心得、技术笔记和项目经验。",
                          skills="Vue3,JavaScript,Node.js,Python,FastAPI,SQLite", email="example@email.com", github="")
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return api_response(data={"id": profile.id, "name": profile.name, "bio": profile.bio,
                              "skills": profile.skills, "email": profile.email, "github": profile.github})

@app.put("/api/profile", response_model=ApiResponse)
async def update_profile(request: ProfileUpdate, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    profile = db.query(Profile).first()
    if not profile:
        profile = Profile()
        db.add(profile)
    if request.name is not None:
        profile.name = request.name
    if request.bio is not None:
        profile.bio = request.bio
    if request.skills is not None:
        profile.skills = request.skills
    if request.email is not None:
        profile.email = request.email
    if request.github is not None:
        profile.github = request.github
    db.commit()
    db.refresh(profile)
    return api_response(data={"id": profile.id, "name": profile.name, "bio": profile.bio,
                              "skills": profile.skills, "email": profile.email, "github": profile.github}, msg="更新成功")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
