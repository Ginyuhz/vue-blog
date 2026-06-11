# 后端接口规范
基础请求路径：/api
统一返回格式：{ "code": 状态码, "data": 数据, "msg": 提示信息 }

## 管理员接口
- POST /api/login  管理员登录，返回鉴权 Token

## 文章接口
- GET /api/article/list  获取全部文章列表
- GET /api/article/:id   获取单篇文章详情
- POST /api/article      新增文章（需携带 Token）
- PUT /api/article/:id   编辑已有文章（需携带 Token）
- DELETE /api/article/:id 删除文章（需携带 Token）

## 分类 & 标签接口
- GET /api/category  获取全部分类
- GET /api/tag       获取全部标签

## 权限规则
所有新增、编辑、删除类写接口，请求头必须携带 Authorization 字段的 Token 完成鉴权。