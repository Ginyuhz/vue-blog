# 技术规范
## 整体技术栈
### 前端
构建工具：Vite
框架：Vue 3 + JavaScript + <script setup>
路由：Vue Router 4
状态管理：Pinia
网络请求：Axios
内容渲染：vue-markdown + prismjs
样式：纯原生 CSS，使用 CSS 变量、媒体查询，不引入任何 CSS 框架
**全局禁止使用 TypeScript，所有脚本文件后缀为 .js**

### 后端
语言：Python 3
Web 框架：FastAPI
数据库：SQLite（文件型数据库，无需独立服务）
ORM 框架：SQLAlchemy
身份鉴权：JWT Token

## 目录与文件规则
1. frontend 下所有脚本文件统一使用 `.js`，不使用 `.ts`
2. 全局样式统一归类至 src/assets/css/ 目录，分 reset / global / common 三个文件
3. 多组件重复样式必须抽取至 common.css，禁止代码冗余
4. 单个组件样式过长时，拆分独立 CSS 文件，组件内部引入
5. 组件局部样式使用 `<style scoped>` 原生 CSS

## 编码规则
1. Vue 组件统一使用 `<script setup>` 组合式语法
2. CSS 类名采用语义化命名，通过 CSS 变量管理主题色
3. 区分开发环境、生产环境接口地址配置
4. 后端接口遵循 RESTful 设计风格
5. 后端接口统一返回固定格式，后台操作接口必须校验 Token