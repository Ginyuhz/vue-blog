# 页面结构规范
## 前台公开页面
1. 首页 /
2. 文章详情页 /article/:id
3. 分类页面 /category
4. 标签页面 /tag
5. 关于我页面 /about

## 后台管理页面（路由前缀 /admin）
1. 登录页 /admin/login
2. 文章管理列表 /admin/article
3. 文章新增/编辑页 /admin/article/edit

## 公共组件
导航栏、页脚、侧边栏、Markdown 编辑器封装为独立公共组件，样式全部使用原生CSS。