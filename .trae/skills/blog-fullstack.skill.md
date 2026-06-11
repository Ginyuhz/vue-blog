# Skill：Vue3 + FastAPI 全栈博客（纯JS + 原生CSS + 在线编辑）
## 适用场景
前后端分离个人博客，支持线上登录、在线编辑文章，**全程不使用 TypeScript**

## 强制约束
1. 严格遵循 /spec/ 目录下所有规范文档
2. 前端全部使用 JavaScript，禁止 TypeScript，文件后缀为 .js
3. 样式仅使用原生 CSS，不引入任何 CSS 框架
4. 前端使用 Vue3 <script setup>，后端使用 FastAPI + SQLite
5. **样式强制复用规则**：
   - 多个组件重复样式，统一抽取到 src/assets/css/common.css
   - 单个组件样式代码过多，拆分独立 CSS 文件并在组件内引入
   - 全局基础样式、重置样式拆分到对应独立文件

## 依赖清单
### 前端依赖
vue, vue-router@4, pinia, axios, vue-markdown, prismjs

### 后端依赖
fastapi, uvicorn, sqlalchemy, python-jose, passlib

## 标准执行流程
1. 使用 Vite 初始化 **纯 JavaScript** 版 Vue3 项目，配置路由、Pinia、Axios
2. 创建 src/assets/css/ 目录，拆分 reset.css / global.css / common.css
3. 编写全局原生 CSS、CSS 变量主题、媒体查询响应式，通用组件样式写入 common.css
4. 按照 pages.md 开发全部前台页面与公共组件，重复样式直接引用通用类名
5. 样式代码量大的组件，拆分独立 CSS 文件并通过 @import 引入
6. 封装 Markdown 编辑器组件，实现编辑区 + 实时预览双栏布局
7. 开发后台登录页、文章管理页、文章编辑页
8. 初始化 Python FastAPI 项目，连接 SQLite 数据库，创建数据模型
9. 按照 api.md 编写所有接口，实现登录、Token 鉴权、文章 CRUD
10. 前后端联调，测试浏览、登录、新增、编辑、删除、权限校验
11. 本地同时启动前后端服务，全功能自测，保证无控制台报错、无样式冗余
12. 生成生产启动脚本、环境配置、线上部署说明

## 交付要求
1. 前后端本地可正常运行、联调
2. 深浅色主题、响应式、在线编辑功能全部可用
3. 代码结构清晰，注释完善，文件后缀统一为 .js
4. 样式按规范分层抽离，无重复 CSS 代码，长样式已拆分独立文件