# 功能需求文档

> 本文档记录博客系统的所有功能实现，每次新增或修改功能时都需要更新此文档。
> 最后更新：2026-06-12

---

## 已完成功能

### 1. 用户认证

- [x] 管理员登录（用户名：admin，密码：admin123）
- [x] JWT Token 认证
- [x] 登录状态持久化（localStorage）
- [x] 登录后显示后台管理入口

### 2. 前台页面

- [x] 首页文章列表
  - 显示文章标题、摘要、发布日期、分类
  - 标签显示（支持多种格式）
  - 分页功能
- [x] 文章详情页
  - Markdown 渲染（支持代码高亮、emoji）
  - 文章目录（自动解析 ##、### 标题）
  - 标签显示
  - 阅读量统计
- [x] 标签页
  - 按标签筛选文章
  - 显示文章数量
- [x] 分类页
  - 按分类筛选文章
- [x] 关于页面
  - 显示博主信息（名称、个人简介、技术栈、联系方式）
  - 登录后可编辑

### 3. 后台管理

#### 3.1 文章管理
- [x] 文章列表（分页显示）
- [x] 新增文章（Markdown 编辑器）
- [x] 编辑文章
- [x] 删除文章
- [x] 单文件 MD 导入（解析 front matter）
- [x] 批量导入 MD 文件
  - 支持多文件同时导入
  - 自动解析 front matter（title、category、tags、excerpt）
  - 自动创建不存在的分类
  - 自动创建不存在的标签
  - 显示详细的导入结果（成功列表、失败原因）

#### 3.2 分类管理
- [x] 分类列表
- [x] 新增分类
- [x] 编辑分类
- [x] 删除分类（需确认无关联文章）
- [x] 批量删除分类（显示失败原因）

#### 3.3 标签管理
- [x] 标签列表
- [x] 新增标签
- [x] 编辑标签
- [x] 删除标签
- [x] 批量删除标签

#### 3.4 个人信息管理
- [x] 查看个人信息
- [x] 编辑个人信息
  - 名称
  - 个人简介
  - 技术栈
  - 邮箱
  - GitHub 地址

### 4. UI/UX 功能

- [x] 响应式布局（适配移动端）
- [x] 黑暗模式切换
  - 背景变为深色
  - 文字变为浅白色
  - 主题状态持久化
- [x] 登录后前台页面显示编辑/删除按钮
- [x] 后台文章管理按钮响应式布局（小屏幕上下对齐）

### 5. 系统优化

- [x] 移除底部版权信息
- [x] 标签解析优化（支持 `[tag1, tag2]` 格式）
- [x] 文章管理标签显示优化
- [x] 错误处理和加载状态

---

## 待开发功能

- [ ] 文章搜索功能
- [ ] 评论/留言功能
- [ ] 文章点赞功能
- [ ] 访问统计
- [ ] RSS 订阅
- [ ] SEO 优化
- [ ] 图片上传功能
- [ ] 文章草稿功能
- [ ] 用户权限管理（多用户支持）

---

## 技术栈

### 前端
- Vue 3 (Composition API)
- Vue Router 4
- Pinia (状态管理)
- Axios
- markdown-it (Markdown 渲染)
- Prism.js (代码高亮)
- Vite (构建工具)

### 后端
- FastAPI
- SQLAlchemy
- SQLite
- JWT (python-jose)
- Python 3

---

## 数据库模型

### Article（文章）
- id: 主键
- title: 标题
- content: 内容（Markdown）
- excerpt: 摘要
- category_id: 分类 ID
- tags: 标签（逗号分隔）
- views: 阅读量
- status: 状态（0=草稿，1=发布）
- created_at: 创建时间
- updated_at: 更新时间

### Category（分类）
- id: 主键
- name: 分类名称
- created_at: 创建时间

### Tag（标签）
- id: 主键
- name: 标签名称

### Admin（管理员）
- id: 主键
- username: 用户名
- password_hash: 密码哈希
- created_at: 创建时间

### Profile（个人信息）
- id: 主键
- name: 名称
- bio: 个人简介
- skills: 技术栈
- email: 邮箱
- github: GitHub 地址
- updated_at: 更新时间

---

## API 接口

### 认证
- `POST /api/login` - 登录

### 文章
- `GET /api/article/list` - 获取文章列表
- `GET /api/article/{id}` - 获取文章详情
- `POST /api/article` - 创建文章
- `PUT /api/article/{id}` - 更新文章
- `DELETE /api/article/{id}` - 删除文章
- `POST /api/article/batch-delete` - 批量删除文章

### 分类
- `GET /api/category` - 获取分类列表
- `POST /api/category` - 创建分类（需认证）
- `PUT /api/category/{id}` - 更新分类（需认证）
- `DELETE /api/category/{id}` - 删除分类（需认证）
- `POST /api/category/batch-delete` - 批量删除分类（需认证）

### 标签
- `GET /api/tag` - 获取标签列表
- `POST /api/tag` - 创建标签（需认证）
- `PUT /api/tag/{id}` - 更新标签（需认证）
- `DELETE /api/tag/{id}` - 删除标签（需认证）
- `POST /api/tag/batch-delete` - 批量删除标签（需认证）

### 个人信息
- `GET /api/profile` - 获取个人信息
- `PUT /api/profile` - 更新个人信息（需认证）

### 系统
- `POST /api/init` - 初始化数据库

---

## 变更记录

### 2026-06-12（本次更新）
1. 添加批量导入功能（支持多文件）
2. 添加后台标签管理页面
3. 添加导入时自动创建标签功能
4. 添加文章阅读页目录导航
5. 生成功能需求文档 requirements.md
6. 添加批量管理功能（文章、分类、标签）
7. 改进批量导入结果提示，显示详细的成功/失败列表及原因
8. 添加后端批量删除 API
9. 删除文章时自动清理无文章的分类和标签
10. 修复分类数组/字符串格式兼容问题
11. 文章编辑页面添加固定定位保存按钮
12. 添加退出登录按钮
13. 实现搜索功能（按标题搜索）
14. 搜索功能包含文章内容
15. 修复导航栏分类/标签点击跳转功能

### 2026-06-11
1. 实现黑暗模式切换
2. 添加登录后前台编辑/删除按钮
3. 添加关于页面编辑功能
4. 创建个人信息编辑页面
5. 移除底部版权信息
6. 优化标签解析（支持数组格式）
