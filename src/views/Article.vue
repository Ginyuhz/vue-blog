<template>
  <div class="page-wrapper">
    <main class="page-main">
      <article class="article-detail card" v-if="article">
        <header class="article-header">
          <div class="article-header-content">
            <h1 class="article-title">{{ article.title }}</h1>
            <div class="article-meta">
              <span class="article-meta-item">
                <span>📅</span>
                {{ formatDate(article.created_at) }}
              </span>
              <span class="article-meta-item">
                <span>📁</span>
                {{ article.category_name }}
              </span>
            </div>
            <div class="tag-list mt-2" v-if="getTags(article.tags).length">
              <span v-for="tag in getTags(article.tags)" :key="tag" class="tag">
                {{ tag }}
              </span>
            </div>
          </div>
          <div class="article-actions" v-if="authStore.isLoggedIn">
            <router-link :to="`/admin/article/edit?id=${article.id}`" class="btn btn-outline btn-sm">
              编辑
            </router-link>
            <button class="btn btn-danger btn-sm" @click="handleDelete">
              删除
            </button>
          </div>
        </header>
        <div class="divider"></div>
        
        <!-- 搜索框 -->
        <div class="in-content-search" v-if="article">
          <input 
            type="text" 
            class="form-input search-input" 
            placeholder="在文章中搜索..." 
            v-model="searchKeyword"
            @input="performSearch"
          />
          
          <!-- 搜索结果列表 -->
          <div class="search-results-dropdown" v-if="showDropdown && searchResults.length">
            <div 
              class="search-result-item" 
              v-for="(result, index) in searchResults" 
              :key="index"
              :class="{ active: index === currentResultIndex }"
              @click="jumpToResult(index)"
            >
              <span class="result-context" v-html="getResultContext(result)"></span>
            </div>
          </div>
          <div class="search-results-dropdown empty" v-if="showDropdown && searchKeyword && !searchResults.length && !searching">
            未找到匹配内容
          </div>
        </div>
        
        <div class="article-content" v-html="highlightedContent" ref="contentRef"></div>
      </article>
      <div v-if="loading" class="loading">
        <div class="loading-spinner"></div>
        <span>加载中...</span>
      </div>
      <div v-if="error" class="empty-state">
        <div class="empty-state-icon">❌</div>
        <p>{{ error }}</p>
        <router-link to="/" class="btn btn-primary mt-2">返回首页</router-link>
      </div>
      <div v-if="!loading && !article && !error" class="empty-state">
        <div class="empty-state-icon">🔍</div>
        <p>文章不存在</p>
        <router-link to="/" class="btn btn-primary mt-2">返回首页</router-link>
      </div>
    </main>
    <aside class="page-aside">
      <!-- 文章目录 -->
      <div class="card toc-card" v-if="toc.length">
        <h3 class="toc-title">目录</h3>
        <nav class="toc-nav">
          <a
            v-for="item in toc"
            :key="item.id"
            :href="'#' + item.id"
            class="toc-link"
            :class="{ 'toc-h2': item.level === 2, 'toc-h3': item.level === 3 }"
            @click.prevent="scrollToHeading(item.id)"
          >
            {{ item.text }}
          </a>
        </nav>
      </div>
      <SideBar />
    </aside>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getArticleById, deleteArticle } from '../api/article'
import { useAuthStore } from '../stores/auth'
import SideBar from '../components/SideBar.vue'
import MarkdownIt from 'markdown-it'
import Prism from 'prismjs'
import 'prismjs/components/prism-javascript'
import 'prismjs/components/prism-python'
import 'prismjs/components/prism-css'
import 'prismjs/components/prism-bash'
import 'prismjs/components/prism-json'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const article = ref(null)
const loading = ref(true)
const error = ref(null)
const toc = ref([])
const contentRef = ref(null)

// 搜索相关
const searchKeyword = ref('')
const searchResults = ref([])
const currentResultIndex = ref(0)
const showDropdown = ref(false)
const searching = ref(false)
let searchTimeout = null

// 初始化 markdown-it，添加标题 ID
const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  highlight: function (str, lang) {
    if (lang && Prism.languages[lang]) {
      try {
        return '<pre class="language-' + lang + '"><code>' +
          Prism.highlight(str, Prism.languages[lang], lang) +
          '</code></pre>'
      } catch (e) {
        console.error('Prism highlight error:', e)
      }
    }
    return '<pre><code>' + MarkdownIt().utils.escapeHtml(str) + '</code></pre>'
  }
})

// 添加标题 ID 插件
const defaultHeadingRender = md.renderer.rules.heading_open || function(tokens, idx, options, env, self) {
  return self.renderToken(tokens, idx, options)
}

md.renderer.rules.heading_open = function(tokens, idx, options, env, self) {
  const token = tokens[idx]
  const nextToken = tokens[idx + 1]
  if (nextToken && nextToken.content) {
    const id = nextToken.content
      .toLowerCase()
      .replace(/[^\u4e00-\u9fa5a-z0-9]+/g, '-')
      .replace(/^-|-$/g, '')
    token.attrSet('id', id)
  }
  return defaultHeadingRender(tokens, idx, options, env, self)
}

// 动态加载 emoji 插件
import('markdown-it-emoji').then(emoji => {
  md.use(emoji.default || emoji)
}).catch(e => {
  console.warn('Failed to load emoji plugin:', e)
})

// 解析目录
const parseToc = (content) => {
  if (!content) return []
  const tocItems = []
  const headingRegex = /^(#{2,3})\s+(.+)$/gm
  let match
  while ((match = headingRegex.exec(content)) !== null) {
    const level = match[1].length
    const text = match[2].trim()
    const id = text
      .toLowerCase()
      .replace(/[^\u4e00-\u9fa5a-z0-9]+/g, '-')
      .replace(/^-|-$/g, '')
    tocItems.push({ level, text, id })
  }
  return tocItems
}

const renderedContent = computed(() => {
  if (!article.value?.content) return ''
  try {
    toc.value = parseToc(article.value.content)
    return md.render(article.value.content)
  } catch (e) {
    console.error('Markdown render error:', e)
    return article.value.content
  }
})

// 高亮搜索关键词
const highlightedContent = computed(() => {
  const content = renderedContent.value
  if (!searchKeyword.value || !content) return content
  
  const keyword = searchKeyword.value
  const regex = new RegExp(keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi')
  
  // 标记所有匹配项
  return content.replace(regex, match => `<mark class="search-highlight">${match}</mark>`)
})

// 执行搜索，收集匹配位置
const performSearch = () => {
  // 清除之前的定时器
  if (searchTimeout) clearTimeout(searchTimeout)
  
  if (!searchKeyword.value || !contentRef.value) {
    searchResults.value = []
    showDropdown.value = false
    return
  }
  
  // 等待输入完成（300ms）
  searching.value = true
  searchTimeout = setTimeout(() => {
    const content = contentRef.value
    const keyword = searchKeyword.value
    const regex = new RegExp(keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi')
    
    // 在原始 HTML 中查找所有匹配
    const matches = []
    let match
    const html = content.innerHTML
    const tempRegex = new RegExp(regex.source, 'gi')
    
    while ((match = tempRegex.exec(html)) !== null) {
      matches.push({
        index: match.index,
        text: match[0],
        // 获取上下文（周围 30 个字符）
        context: getContextAround(html, match.index, keyword.length, 60)
      })
    }
    
    searchResults.value = matches
    currentResultIndex.value = 0
    showDropdown.value = matches.length > 0
    searching.value = false
  }, 300)
}

// 获取上下文文本
const getContextAround = (html, matchIndex, matchLen, contextLen) => {
  const start = Math.max(0, matchIndex - contextLen)
  const end = Math.min(html.length, matchIndex + matchLen + contextLen)
  let context = html.substring(start, end)
  
  // 清理 HTML 标签，只保留纯文本
  context = context.replace(/<[^>]+>/g, '')
  // 替换多余空白
  context = context.replace(/\s+/g, ' ').trim()
  
  // 如果不是从开头截取，添加省略号
  if (start > 0) context = '...' + context
  if (end < html.length) context = context + '...'
  
  return context
}

// 获取显示用的上下文（带高亮）
const getResultContext = (result) => {
  if (!result.context) return ''
  const keyword = searchKeyword.value
  const regex = new RegExp(keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi')
  return result.context.replace(regex, match => `<mark>${match}</mark>`)
}

// 跳转到指定结果
const jumpToResult = (index) => {
  currentResultIndex.value = index
  showDropdown.value = false
  
  if (!contentRef.value) return
  
  const highlights = contentRef.value.querySelectorAll('.search-highlight')
  if (!highlights.length) return
  
  // 找到第 index 个高亮（因为每次高亮后 index 会变化，需要重新计算）
  const keyword = searchKeyword.value
  const allHighlights = contentRef.value.querySelectorAll('.search-highlight')
  let targetIndex = 0
  let found = null
  
  for (let i = 0; i < allHighlights.length; i++) {
    if (allHighlights[i].textContent.toLowerCase() === keyword.toLowerCase()) {
      if (targetIndex === index) {
        found = allHighlights[i]
        break
      }
      targetIndex++
    }
  }
  
  if (found) {
    const navbarHeight = 56
    const elementPosition = found.getBoundingClientRect().top
    const offsetPosition = elementPosition + window.pageYOffset - navbarHeight - 100
    
    window.scrollTo({
      top: offsetPosition,
      behavior: 'smooth'
    })
  }
}

// 清除搜索
const clearSearch = () => {
  searchKeyword.value = ''
  searchResults.value = []
  currentResultIndex.value = 0
  showDropdown.value = false
}

const scrollToHeading = (id) => {
  const element = document.getElementById(id)
  if (element) {
    const navbarHeight = 56 // 导航栏高度
    const elementPosition = element.getBoundingClientRect().top
    const offsetPosition = elementPosition + window.pageYOffset - navbarHeight
    
    window.scrollTo({
      top: offsetPosition,
      behavior: 'smooth'
    })
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

// 解析标签：支持多种格式
const getTags = (tagsStr) => {
  if (!tagsStr) return []
  
  // 如果是数组格式字符串 "[Vue, JavaScript, CSS]"
  if (tagsStr.startsWith('[') && tagsStr.endsWith(']')) {
    tagsStr = tagsStr.slice(1, -1)
  }
  
  return tagsStr.split(',').map(t => t.trim()).filter(t => t)
}

const handleDelete = async () => {
  if (!article.value) return
  if (!confirm('确定要删除这篇文章吗？')) return
  try {
    await deleteArticle(article.value.id)
    router.push('/')
  } catch (e) {
    alert(e.message || '删除失败')
  }
}

onMounted(async () => {
  try {
    console.log('Fetching article with id:', route.params.id)
    const res = await getArticleById(route.params.id)
    console.log('Article response:', res)
    article.value = res.data
  } catch (e) {
    console.error('获取文章详情失败', e)
    error.value = e.message || '获取文章失败'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.article-detail {
  padding: 2rem;
}

.article-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.article-header-content {
  flex: 1;
}

.article-title {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 1rem;
  color: var(--color-starbucks);
  letter-spacing: -0.02em;
}

.article-actions {
  display: flex;
  gap: 0.5rem;
  flex-shrink: 0;
}

.btn-sm {
  padding: 4px 12px;
  font-size: 0.75rem;
}

.in-content-search {
  position: relative;
  margin-bottom: 1.5rem;
}

.search-input {
  width: 100%;
  padding: 0.625rem 0.875rem;
  font-size: 0.875rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  background: var(--color-card-bg);
  transition: var(--transition);
}

.search-input:focus {
  outline: none;
  border-color: var(--color-green-accent);
  box-shadow: 0 0 0 3px rgba(0, 117, 74, 0.1);
}

.search-count {
  font-size: 0.875rem;
  color: var(--color-text-black-soft);
  min-width: 50px;
  text-align: center;
}

.search-results-dropdown {
  position: absolute;
  top: calc(100% + 0.5rem);
  left: 0;
  right: 0;
  max-height: 320px;
  overflow-y: auto;
  background: var(--color-card-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  box-shadow: var(--shadow-card);
  z-index: 10;
}

.search-results-dropdown.empty {
  padding: 1rem;
  text-align: center;
  color: var(--color-text-black-soft);
  font-size: 0.875rem;
}

.search-result-item {
  padding: 0.75rem 1rem;
  cursor: pointer;
  border-bottom: 1px solid var(--color-border);
  transition: var(--transition);
}

.search-result-item:last-child {
  border-bottom: none;
}

.search-result-item:hover,
.search-result-item.active {
  background: var(--color-neutral-cool);
}

.result-context {
  font-size: 0.875rem;
  color: var(--color-text-black);
  line-height: 1.5;
  word-break: break-all;
}

.result-context :deep(mark) {
  background: #fef08a;
  color: #000;
  padding: 0 2px;
  border-radius: 2px;
}

:deep(.search-highlight) {
  background: #fef08a;
  color: #000;
  padding: 0 2px;
  border-radius: 2px;
}

@media (max-width: 576px) {
  .article-header {
    flex-direction: column;
  }
  
  .article-actions {
    width: 100%;
  }
}

.article-content {
  line-height: 1.8;
  font-size: 1rem;
}

.article-content :deep(h1),
.article-content :deep(h2),
.article-content :deep(h3),
.article-content :deep(h4),
.article-content :deep(h5),
.article-content :deep(h6) {
  margin: 2rem 0 1rem;
  font-weight: 600;
  color: var(--color-starbucks);
  letter-spacing: -0.01em;
}

.article-content :deep(h1) { font-size: 1.75rem; }
.article-content :deep(h2) { font-size: 1.5rem; }
.article-content :deep(h3) { font-size: 1.25rem; }
.article-content :deep(h4) { font-size: 1.125rem; }

.article-content :deep(p) {
  margin: 1rem 0;
  line-height: 1.8;
}

.article-content :deep(ul),
.article-content :deep(ol) {
  margin: 1rem 0;
  padding-left: 1.5rem;
}

.article-content :deep(li) {
  margin: 0.5rem 0;
  line-height: 1.6;
}

.article-content :deep(blockquote) {
  margin: 1.5rem 0;
  padding: 1rem 1.5rem;
  border-left: 4px solid var(--color-green-accent);
  background: rgba(0, 117, 74, 0.05);
  border-radius: 0 var(--radius) var(--radius) 0;
  color: var(--color-text-black-soft);
}

.article-content :deep(blockquote p) {
  margin: 0;
}

.article-content :deep(code) {
  background: var(--color-neutral-cool);
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-size: 0.9em;
  font-family: Consolas, Monaco, 'Courier New', monospace;
}

.article-content :deep(pre) {
  background: var(--color-house-green);
  color: var(--color-text-white);
  padding: 1.25rem;
  border-radius: var(--radius);
  overflow-x: auto;
  margin: 1.5rem 0;
}

.article-content :deep(pre code) {
  background: none;
  padding: 0;
  font-size: 0.875rem;
  color: inherit;
}

.article-content :deep(a) {
  color: var(--color-green-accent);
  text-decoration: none;
  border-bottom: 1px solid transparent;
  transition: var(--transition);
}

.article-content :deep(a:hover) {
  border-bottom-color: var(--color-green-accent);
}

.article-content :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: var(--radius);
  margin: 1.5rem 0;
  box-shadow: var(--shadow-card);
}

.article-content :deep(hr) {
  border: none;
  border-top: 2px solid rgba(0, 0, 0, 0.06);
  margin: 2rem 0;
}

.article-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 1.5rem 0;
}

.article-content :deep(th),
.article-content :deep(td) {
  padding: 0.75rem 1rem;
  text-align: left;
  border: 1px solid rgba(0, 0, 0, 0.1);
}

.article-content :deep(th) {
  background: var(--color-neutral-warm);
  font-weight: 600;
}

.article-content :deep(tr:nth-child(even)) {
  background: rgba(0, 0, 0, 0.02);
}

.article-content :deep(.task-list-item) {
  list-style: none;
  margin-left: -1.5rem;
}

.article-content :deep(.task-list-item input) {
  margin-right: 0.5rem;
}

.article-content :deep(.footnotes) {
  margin-top: 3rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  font-size: 0.875rem;
  color: var(--color-text-black-soft);
}

.article-content :deep(mark) {
  background: rgba(203, 162, 88, 0.3);
  padding: 0.1rem 0.25rem;
  border-radius: 2px;
}

/* 文章目录样式 */
.toc-card {
  padding: 1rem;
  margin-bottom: 1rem;
}

.toc-title {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
  color: var(--color-starbucks);
}

.toc-nav {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.toc-link {
  font-size: 0.875rem;
  color: var(--color-text-black);
  text-decoration: none;
  padding: 0.25rem 0;
  padding-left: 0.5rem;
  border-left: 2px solid transparent;
  transition: var(--transition);
  line-height: 1.4;
}

.toc-link:hover {
  color: var(--color-green-accent);
  border-left-color: var(--color-green-accent);
}

.toc-h2 {
  font-weight: 500;
}

.toc-h3 {
  padding-left: 1rem;
  font-size: 0.8125rem;
  color: var(--color-text-black-soft);
}

.toc-h3:hover {
  color: var(--color-green-accent);
}
</style>
