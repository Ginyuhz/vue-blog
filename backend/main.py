from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

import models
import schemas
from database import engine, get_db, Base
from auth import verify_password, get_password_hash, create_access_token, get_current_admin

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Vue Blog API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def api_response(code: int = 200, data=None, msg: str = ""):
    return {"code": code, "data": data, "msg": msg}


@app.get("/")
async def root():
    return {"message": "Vue Blog API"}


@app.post("/api/login", response_model=schemas.ApiResponse)
async def login(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    admin = db.query(models.Admin).filter(models.Admin.username == request.username).first()
    if not admin or not verify_password(request.password, admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    token = create_access_token(data={"sub": admin.username})
    return api_response(data={"token": token})


@app.get("/api/article/list", response_model=schemas.ApiResponse)
async def get_articles(
    category_id: int = None,
    tag: str = None,
    keyword: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Article).filter(models.Article.status == 1)
    if category_id:
        query = query.filter(models.Article.category_id == category_id)
    if tag:
        query = query.filter(models.Article.tags.contains(tag))
    if keyword:
        keyword_filter = f"%{keyword}%"
        query = query.filter(
            (models.Article.title.contains(keyword)) |
            (models.Article.content.contains(keyword)) |
            (models.Article.excerpt.contains(keyword))
        )

    articles = query.order_by(models.Article.created_at.desc()).all()
    result = []
    for article in articles:
        category_name = None
        if article.category_id:
            category = db.query(models.Category).filter(models.Category.id == article.category_id).first()
            category_name = category.name if category else None
        result.append({
            "id": article.id,
            "title": article.title,
            "content": article.content,
            "excerpt": article.excerpt,
            "category_id": article.category_id,
            "category_name": category_name,
            "tags": article.tags,
            "created_at": article.created_at.strftime("%Y/%m/%d %H:%M:%S") if article.created_at else None
        })
    return api_response(data=result)


@app.get("/api/article/{article_id}", response_model=schemas.ApiResponse)
async def get_article(article_id: int, db: Session = Depends(get_db)):
    article = db.query(models.Article).filter(
        models.Article.id == article_id,
        models.Article.status == 1
    ).first()
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")

    category_name = None
    if article.category_id:
        category = db.query(models.Category).filter(models.Category.id == article.category_id).first()
        category_name = category.name if category else None

    return api_response(data={
        "id": article.id,
        "title": article.title,
        "content": article.content,
        "excerpt": article.excerpt,
        "category_id": article.category_id,
        "category_name": category_name,
        "tags": article.tags,
        "created_at": article.created_at
    })


@app.post("/api/article", response_model=schemas.ApiResponse)
async def create_article(
    article: schemas.ArticleCreate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    # 解析创建时间（如果提供）
    created_at = None
    if article.created_at:
        print(f"[DEBUG] 收到 created_at: {article.created_at}")
        try:
            # 支持多种日期格式
            for fmt in ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y/%m/%d"]:
                try:
                    created_at = datetime.strptime(article.created_at, fmt)
                    print(f"[DEBUG] 成功解析日期: {created_at}")
                    break
                except ValueError:
                    continue
        except Exception as e:
            print(f"[DEBUG] 日期解析失败: {e}")
            created_at = None
    else:
        print("[DEBUG] 未收到 created_at 字段")
    
    db_article = models.Article(
        title=article.title,
        content=article.content,
        excerpt=article.excerpt,
        category_id=article.category_id,
        tags=article.tags,
        created_at=created_at
    )
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return api_response(data={"id": db_article.id}, msg="创建成功")


@app.put("/api/article/{article_id}", response_model=schemas.ApiResponse)
async def update_article(
    article_id: int,
    article: schemas.ArticleUpdate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    db_article = db.query(models.Article).filter(models.Article.id == article_id).first()
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


@app.delete("/api/article/{article_id}", response_model=schemas.ApiResponse)
async def delete_article(
    article_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    db_article = db.query(models.Article).filter(models.Article.id == article_id).first()
    if not db_article:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    # 获取文章关联的分类和标签
    category_id = db_article.category_id
    tags = db_article.tags.split(',') if db_article.tags else []
    
    # 删除文章
    db.delete(db_article)
    
    # 清理空分类
    if category_id:
        remaining = db.query(models.Article).filter(
            models.Article.category_id == category_id,
            models.Article.id != article_id
        ).count()
        if remaining == 0:
            db_category = db.query(models.Category).filter(models.Category.id == category_id).first()
            if db_category:
                db.delete(db_category)
    
    # 清理空标签
    for tag_name in tags:
        if tag_name.strip():
            tag = db.query(models.Tag).filter(models.Tag.name == tag_name.strip()).first()
            if tag:
                remaining = db.query(models.Article).filter(
                    models.Article.tags.contains(tag_name.strip())
                ).count()
                if remaining <= 1:  # 刚删除的文章
                    db.delete(tag)
    
    db.commit()
    return api_response(msg="删除成功")


@app.post("/api/article/batch-delete", response_model=schemas.ApiResponse)
async def batch_delete_articles(
    request: schemas.BatchDeleteRequest,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    ids = request.ids
    if not ids:
        raise HTTPException(status_code=400, detail="请选择要删除的文章")
    
    success_list = []
    fail_list = []
    deleted_category_ids = set()
    deleted_tag_names = set()
    
    for article_id in ids:
        article = db.query(models.Article).filter(models.Article.id == article_id).first()
        if article:
            # 记录要清理的分类和标签
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
    
    # 清理空分类
    for cat_id in deleted_category_ids:
        remaining = db.query(models.Article).filter(
            models.Article.category_id == cat_id
        ).count()
        if remaining == 0:
            db_category = db.query(models.Category).filter(models.Category.id == cat_id).first()
            if db_category:
                db.delete(db_category)
    
    # 清理空标签
    for tag_name in deleted_tag_names:
        tag = db.query(models.Tag).filter(models.Tag.name == tag_name).first()
        if tag:
            remaining = db.query(models.Article).filter(
                models.Article.tags.contains(tag_name)
            ).count()
            if remaining == 0:
                db.delete(tag)
    
    db.commit()
    
    return api_response(data={
        "success": success_list,
        "fail": fail_list
    }, msg=f"删除成功 {len(success_list)} 篇，失败 {len(fail_list)} 篇")


@app.get("/api/category", response_model=schemas.ApiResponse)
async def get_categories(db: Session = Depends(get_db)):
    categories = db.query(models.Category).all()
    result = []
    for cat in categories:
        count = db.query(models.Article).filter(
            models.Article.category_id == cat.id,
            models.Article.status == 1
        ).count()
        result.append({"id": cat.id, "name": cat.name, "count": count})
    return api_response(data=result)


@app.post("/api/category", response_model=schemas.ApiResponse)
async def create_category(
    request: schemas.CategoryCreate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    existing = db.query(models.Category).filter(models.Category.name == request.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="分类已存在")
    
    category = models.Category(name=request.name)
    db.add(category)
    db.commit()
    db.refresh(category)
    return api_response(data={"id": category.id, "name": category.name}, msg="创建成功")


@app.put("/api/category/{category_id}", response_model=schemas.ApiResponse)
async def update_category(
    category_id: int,
    request: schemas.CategoryUpdate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    
    existing = db.query(models.Category).filter(
        models.Category.name == request.name,
        models.Category.id != category_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="分类名已存在")
    
    category.name = request.name
    db.commit()
    db.refresh(category)
    return api_response(data={"id": category.id, "name": category.name}, msg="更新成功")


@app.delete("/api/category/{category_id}", response_model=schemas.ApiResponse)
async def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    
    count = db.query(models.Article).filter(models.Article.category_id == category_id).count()
    if count > 0:
        raise HTTPException(status_code=400, detail="该分类下存在文章，无法删除")
    
    db.delete(category)
    db.commit()
    return api_response(msg="删除成功")


@app.post("/api/category/batch-delete", response_model=schemas.ApiResponse)
async def batch_delete_categories(
    request: schemas.BatchDeleteRequest,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    ids = request.ids
    if not ids:
        raise HTTPException(status_code=400, detail="请选择要删除的分类")
    
    success_list = []
    fail_list = []
    
    for category_id in ids:
        category = db.query(models.Category).filter(models.Category.id == category_id).first()
        if not category:
            fail_list.append({"id": category_id, "reason": "分类不存在"})
            continue
        
        count = db.query(models.Article).filter(models.Article.category_id == category_id).count()
        if count > 0:
            fail_list.append({"id": category_id, "name": category.name, "reason": f"该分类下存在 {count} 篇文章"})
            continue
        
        db.delete(category)
        success_list.append({"id": category_id, "name": category.name})
    
    db.commit()
    
    return api_response(data={
        "success": success_list,
        "fail": fail_list
    }, msg=f"删除成功 {len(success_list)} 个，失败 {len(fail_list)} 个")


@app.get("/api/tag", response_model=schemas.ApiResponse)
async def get_tags(db: Session = Depends(get_db)):
    tags = db.query(models.Tag).all()
    result = []
    for t in tags:
        count = db.query(models.Article).filter(
            models.Article.tags.contains(t.name),
            models.Article.status == 1
        ).count()
        result.append({"id": t.id, "name": t.name, "count": count})
    return api_response(data=result)


@app.post("/api/tag", response_model=schemas.ApiResponse)
async def create_tag(
    request: schemas.TagCreate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    existing = db.query(models.Tag).filter(models.Tag.name == request.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="标签已存在")
    
    tag = models.Tag(name=request.name)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return api_response(data={"id": tag.id, "name": tag.name, "count": 0}, msg="创建成功")


@app.put("/api/tag/{tag_id}", response_model=schemas.ApiResponse)
async def update_tag(
    tag_id: int,
    request: schemas.TagUpdate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    tag = db.query(models.Tag).filter(models.Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")
    
    existing = db.query(models.Tag).filter(
        models.Tag.name == request.name,
        models.Tag.id != tag_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="标签名称已存在")
    
    tag.name = request.name
    db.commit()
    db.refresh(tag)
    return api_response(data={"id": tag.id, "name": tag.name, "count": 0}, msg="更新成功")


@app.delete("/api/tag/{tag_id}", response_model=schemas.ApiResponse)
async def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    tag = db.query(models.Tag).filter(models.Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")
    
    db.delete(tag)
    db.commit()
    return api_response(msg="删除成功")


@app.post("/api/tag/batch-delete", response_model=schemas.ApiResponse)
async def batch_delete_tags(
    request: schemas.BatchDeleteRequest,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    ids = request.ids
    if not ids:
        raise HTTPException(status_code=400, detail="请选择要删除的标签")
    
    success_list = []
    fail_list = []
    
    for tag_id in ids:
        tag = db.query(models.Tag).filter(models.Tag.id == tag_id).first()
        if not tag:
            fail_list.append({"id": tag_id, "reason": "标签不存在"})
            continue
        
        db.delete(tag)
        success_list.append({"id": tag_id, "name": tag.name})
    
    db.commit()
    
    return api_response(data={
        "success": success_list,
        "fail": fail_list
    }, msg=f"删除成功 {len(success_list)} 个，失败 {len(fail_list)} 个")


@app.post("/api/init", response_model=schemas.ApiResponse)
async def init_database(db: Session = Depends(get_db)):
    admin = db.query(models.Admin).first()
    if not admin:
        admin = models.Admin(
            username="admin",
            password_hash=get_password_hash("admin123")
        )
        db.add(admin)

    categories = db.query(models.Category).all()
    if not categories:
        default_categories = ["前端", "后端", "DevOps", "随笔"]
        for name in default_categories:
            db.add(models.Category(name=name))

    tags = db.query(models.Tag).all()
    if not tags:
        default_tags = ["Vue", "JavaScript", "Python", "CSS", "Node.js", "FastAPI"]
        for name in default_tags:
            db.add(models.Tag(name=name))

    db.commit()
    return api_response(msg="初始化成功")


# 个人信息API
@app.get("/api/profile", response_model=schemas.ApiResponse)
async def get_profile(db: Session = Depends(get_db)):
    profile = db.query(models.Profile).first()
    if not profile:
        # 创建默认个人信息
        profile = models.Profile(
            name="博主",
            bio="一名热爱技术的前端开发者，专注于 Vue、React 等现代前端技术。\n\n在这里分享学习心得、技术笔记和项目经验。",
            skills="Vue3,JavaScript,Node.js,Python,FastAPI,SQLite",
            email="example@email.com",
            github=""
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    
    return api_response(data={
        "id": profile.id,
        "name": profile.name,
        "bio": profile.bio,
        "skills": profile.skills,
        "email": profile.email,
        "github": profile.github
    })


@app.put("/api/profile", response_model=schemas.ApiResponse)
async def update_profile(
    request: schemas.ProfileUpdate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    profile = db.query(models.Profile).first()
    if not profile:
        profile = models.Profile()
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
    
    return api_response(data={
        "id": profile.id,
        "name": profile.name,
        "bio": profile.bio,
        "skills": profile.skills,
        "email": profile.email,
        "github": profile.github
    }, msg="更新成功")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
