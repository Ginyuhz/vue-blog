<template>
  <aside class="sidebar">
    <!-- 搜索 -->
    <div class="card sidebar-section search-section">
      <h3 class="sidebar-title">搜索</h3>
      <div class="search-box">
        <input 
          type="text" 
          class="form-input" 
          placeholder="搜索文章..." 
          v-model="keyword" 
          @input="handleInput"
          @keydown.enter="handleSearch"
          @focus="showDropdown = true"
          @blur="hideDropdown"
        />
        <div class="search-dropdown" v-if="showDropdown && searchResults.length">
          <router-link 
            v-for="article in searchResults" 
            :key="article.id"
            :to="`/article/${article.id}`"
            class="search-result-item"
            @click="clearSearch"
          >
            <div class="result-content">
              <span class="result-title" v-html="highlightKeyword(article.title)"></span>
              <span class="result-excerpt" v-html="highlightKeyword(getExcerpt(article))"></span>
            </div>
            <span class="result-category">{{ article.category_name }}</span>
          </router-link>
        </div>
        <div class="search-dropdown empty" v-if="showDropdown && keyword && !searchResults.length && !searching">
          未找到相关文章
        </div>
      </div>
    </div>

    <!-- 分类 -->
    <div class="card sidebar-section">
      <h3 class="sidebar-title">分类</h3>
      <div class="category-list" v-if="categories.length">
        <router-link
          v-for="cat in categories"
          :key="cat.id"
          :to="`/category?id=${cat.id}`"
          class="category-item"
          :class="{ active: currentCategoryId === cat.id }"
        >
          <span class="category-name">{{ cat.name }}</span>
          <span class="category-count">{{ cat.count }}</span>
        </router-link>
      </div>
      <div v-else class="empty-state">暂无分类</div>
    </div>

    <!-- 标签 -->
    <div class="card sidebar-section">
      <h3 class="sidebar-title">标签</h3>
      <div class="tag-list" v-if="tags.length">
        <router-link
          v-for="tag in tags"
          :key="tag.id"
          :to="`/tag?name=${encodeURIComponent(tag.name)}`"
          class="tag"
          :class="{ active: currentTagName === tag.name }"
        >
          {{ tag.name }}
        </router-link>
      </div>
      <div v-else class="empty-state">暂无标签</div>
    </div>
  </aside>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getCategoryList, getTagList, getArticleList } from '../api/article'

const route = useRoute()
const router = useRouter()
const keyword = ref('')
const categories = ref([])
const tags = ref([])
const searchResults = ref([])
const showDropdown = ref(false)
const searching = ref(false)
let searchTimeout = null

const currentCategoryId = computed(() => {
  return route.path === '/category' ? parseInt(route.query.id) : null
})

const currentTagName = computed(() => {
  return route.path === '/tag' ? route.query.name : null
})

const handleInput = () => {
  // 清除之前的定时器
  if (searchTimeout) clearTimeout(searchTimeout)
  
  if (!keyword.value.trim()) {
    searchResults.value = []
    showDropdown.value = false
    return
  }
  
  // 延迟搜索
  searching.value = true
  searchTimeout = setTimeout(async () => {
    try {
      const res = await getArticleList({ keyword: keyword.value.trim() })
      searchResults.value = (res.data || []).slice(0, 5) // 最多显示5条
      showDropdown.value = true
    } catch (e) {
      console.error('搜索失败', e)
      searchResults.value = []
    } finally {
      searching.value = false
    }
  }, 300)
}

const handleSearch = () => {
  if (keyword.value.trim()) {
    showDropdown.value = false
    router.push(`/search?q=${encodeURIComponent(keyword.value.trim())}`)
  }
}

const hideDropdown = () => {
  // 延迟关闭，等待点击事件
  setTimeout(() => {
    showDropdown.value = false
  }, 200)
}

// 高亮搜索词
const highlightKeyword = (text) => {
  if (!text || !keyword.value) return text
  const regex = new RegExp(keyword.value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi')
  return text.replace(regex, match => `<mark>${match}</mark>`)
}

// 获取包含搜索词的摘要
const getExcerpt = (article) => {
  if (!article) return ''
  
  // 优先搜索 content，如果没有就用 excerpt
  const text = article.content || article.excerpt || ''
  const keywordLower = keyword.value.toLowerCase()
  const index = text.toLowerCase().indexOf(keywordLower)
  
  if (index === -1) {
    // 如果没有找到，返回 excerpt 的前50字符
    return (article.excerpt || '').substring(0, 50) + '...'
  }
  
  // 显示包含搜索词的上下文
  const start = Math.max(0, index - 30)
  const end = Math.min(text.length, index + keyword.value.length + 50)
  let result = text.substring(start, end)
  
  // 清理 HTML 标签
  result = result.replace(/<[^>]+>/g, '')
  // 替换多余空白
  result = result.replace(/\s+/g, ' ').trim()
  
  if (start > 0) result = '...' + result
  if (end < text.length) result = result + '...'
  
  return result
}

const clearSearch = () => {
  keyword.value = ''
  searchResults.value = []
  showDropdown.value = false
}

onMounted(async () => {
  try {
    const [catRes, tagRes] = await Promise.all([
      getCategoryList(),
      getTagList()
    ])
    categories.value = catRes.data || []
    tags.value = tagRes.data || []
  } catch (e) {
    console.error('获取侧边栏数据失败', e)
  }
})
</script>

<style scoped>
.sidebar {
  display: flex;
  flex-direction: column;
  gap: 1.6rem;
}

.sidebar-section {
  padding: 1.25rem;
}

.sidebar-title {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  color: var(--color-starbucks);
  letter-spacing: -0.01em;
}

.search-box input {
  font-size: 0.875rem;
}

.search-section {
  position: relative;
}

.search-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  max-height: 320px;
  overflow-y: auto;
  background: var(--color-card-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  box-shadow: var(--shadow-card);
  z-index: 10;
  margin-top: 0.5rem;
}

.search-dropdown.empty {
  padding: 1rem;
  text-align: center;
  color: var(--color-text-black-soft);
  font-size: 0.875rem;
}

.search-result-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--color-border);
  transition: var(--transition);
  color: var(--color-text-black);
  text-decoration: none;
}

.search-result-item:last-child {
  border-bottom: none;
}

.search-result-item:hover {
  background: var(--color-neutral-cool);
}

.result-content {
  flex: 1;
  min-width: 0;
}

.result-title {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-bottom: 0.25rem;
}

.result-excerpt {
  display: block;
  font-size: 0.75rem;
  color: var(--color-text-black-soft);
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.result-category {
  font-size: 0.75rem;
  color: var(--color-text-black-soft);
  margin-left: 0.75rem;
  flex-shrink: 0;
  padding-top: 0.125rem;
}

.result-content :deep(mark),
.result-category :deep(mark) {
  background: #fef08a;
  color: #000;
  padding: 0 2px;
  border-radius: 2px;
}

.category-list {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
  max-height: 240px;
  overflow-y: auto;
}

.category-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0.75rem;
  border-radius: var(--radius);
  transition: var(--transition);
  color: var(--color-text-black);
}

.category-item:hover {
  background: rgba(0, 117, 74, 0.05);
}

.category-item.active {
  background: var(--color-green-accent);
  color: white;
}

.category-item.active .category-count {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.category-name {
  font-size: 0.875rem;
}

.category-count {
  font-size: 0.75rem;
  color: var(--color-green-accent);
  background: rgba(0, 117, 74, 0.1);
  padding: 0.125rem 0.5rem;
  border-radius: var(--radius-pill);
}

/* 标签样式 */
.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  max-height: 160px;
  overflow-y: auto;
}

.tag {
  display: inline-block;
  padding: 0.375rem 0.875rem;
  background: rgba(0, 117, 74, 0.08);
  color: var(--color-green-accent);
  border-radius: var(--radius-pill);
  font-size: 0.8125rem;
  transition: var(--transition);
}

.tag:hover {
  background: rgba(0, 117, 74, 0.15);
}

.tag.active {
  background: var(--color-green-accent);
  color: white;
}
</style>
