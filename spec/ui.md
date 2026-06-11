# UI 视觉规范
## 整体风格
简约极客风，布局整洁，仅保留基础过渡效果，无复杂动画。
我导入了一个文件DESIGN.md，这个文件是ui设计，设计系统灵感来自星巴克，我希望你在这个项目的基础上，根据这个文件修改一下样式，使得页面更好看
## 配色（使用 CSS 变量统一管理）
:root {
  --color-text: #333;
  --color-bg: #fff;
  --color-border: #eee;
  --color-primary: #2563eb;
}
/* 暗黑主题 */
.dark {
  --color-text: #e5e5e5;
  --color-bg: #1a1a1a;
  --color-border: #333;
}

## 字体
全局字体：system-ui, -apple-system, sans-serif
代码字体：Consolas, monospace

## 响应式（原生媒体查询实现）
1. 桌面端 ≥ 768px：主内容 + 侧边栏 双栏布局
2. 移动端 ＜ 768px：单列布局，侧边栏隐藏/折叠

## 样式编写 & 复用规则
1. **样式分层抽离**
   - reset.css：浏览器样式重置、标签默认样式
   - global.css：CSS变量、主题、页面基础布局
   - common.css：多组件共用样式（卡片、按钮、列表、分割线、hover效果等），**所有重复样式统一放此处**
2. **组件样式处理**
   - 多个组件样式完全一致：统一抽取到 common.css，组件直接使用对应类名，不重复写代码
   - 单个组件样式代码量大：拆分出独立 `.css` 文件，组件内通过 `@import` 引入
   - 组件独有少量样式：保留在当前组件 `<style scoped>` 内
3. 作用域要求
   - 全局样式：无 scoped
   - 组件独立样式：必须加 `scoped`，防止样式污染
4. 基础样式约定
   - 基础过渡效果：transition: all 0.2s ease;
   - 容器、卡片统一圆角 4px
5. 类名规范
   采用语义化命名，通用样式使用统一类名，方便跨组件复用。