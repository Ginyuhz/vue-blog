<template>
  <div class="page-wrapper">
    <main class="page-main">
      <div class="search-header">
        <h1>搜索结果: {{ keyword }}</h1>
        <p class="search-count">共找到 {{ articles.length }} 篇文章</p>
      </div>
      
      <div class="article-list" v-if="!loading && articles.length">
        <article v-for="article in articles" :key="article.id" class="article-item card">
          <div class="article-header">
            <router-link :to="`/article/${article.id}`" class="article-title">
              {{ article.title }}
            </router-link>
            <div class="article-actions" v-if="authStore.isLoggedIn">
              <router-link :to="`/admin/article/edit?id=${article.id}`" class="btn btn-outline btn-sm">
                编辑
              </router-link>
              <button class="btn btn-danger btn-sm" @click="handleDelete(article.id)">
                删除
              </button>
            </div>
          </div>
          <p class="article-excerpt">{{ article.excerpt }}</p>
          <div class="article-meta">
            <span class="article-meta-item">
              <span>📅</span>
              {{ formatDate(article.created_at) }}
            </span>
            <span class="article-meta-item">
              <span>📁</span>
              {{ article.category_name }}
            </span>
            <span class="article-meta-item tag-list" v-if="getTags(article.tags).length">
              <span v-for="tag in getTags(article.tags)" :key="tag" class="tag">
                {{ tag }}
              </span>
            </span>
          </div>
        </article>
      </div>
      <div v-if="loading" class="loading">
        <div class="loading-spinner"></div>
        <span>搜索中...</span>
      </div>
      <div v-if="!loading && !articles.length" class="empty-state">
        <div class="empty-state-icon">🔍</div>
        <p>未找到相关文章</p>
      </div>
    </main>
    <aside class="page-aside">
      <SideBar />
    </aside>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { getArticleList, deleteArticle } from '../api/article'
import { useAuthStore } from '../stores/auth'
import SideBar from '../components/SideBar.vue'

const route = useRoute()
const authStore = useAuthStore()
const articles = ref([])
const loading = ref(true)
const keyword = ref('')

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

// 解析标签
const getTags = (tagsStr) => {
  if (!tagsStr) return []
  if (tagsStr.startsWith('[') && tagsStr.endsWith(']')) {
    tagsStr = tagsStr.slice(1, -1)
  }
  return tagsStr.split(',').map(t => t.trim()).filter(t => t)
}

const searchArticles = async (kw) => {
  if (!kw) {
    articles.value = []
    loading.value = false
    return
  }
  
  loading.value = true
  try {
    const res = await getArticleList({ keyword: kw })
    articles.value = res.data || []
  } catch (e) {
    console.error('搜索失败', e)
    articles.value = []
  } finally {
    loading.value = false
  }
}

const handleDelete = async (id) => {
  if (!confirm('确定要删除这篇文章吗？')) return
  try {
    await deleteArticle(id)
    articles.value = articles.value.filter(a => a.id !== id)
  } catch (e) {
    alert(e.message || '删除失败')
  }
}

onMounted(() => {
  keyword.value = route.query.q || ''
  searchArticles(keyword.value)
})

watch(() => route.query.q, (newQ) => {
  keyword.value = newQ || ''
  searchArticles(keyword.value)
})
</script>

<style scoped>
.search-header {
  margin-bottom: 2rem;
}

.search-header h1 {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-starbucks);
  margin-bottom: 0.5rem;
}

.search-count {
  color: var(--color-text-black-soft);
  font-size: 0.875rem;
}

.article-item {
  margin-bottom: 1.25rem;
}

.article-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 0.75rem;
}

.article-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-starbucks);
  text-decoration: none;
  transition: var(--transition);
}

.article-title:hover {
  color: var(--color-green-accent);
}

.article-actions {
  display: flex;
  gap: 0.5rem;
  flex-shrink: 0;
}

.article-excerpt {
  color: var(--color-text-black);
  font-size: 0.9375rem;
  line-height: 1.6;
  margin-bottom: 1rem;
}

.article-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  font-size: 0.8125rem;
  color: var(--color-text-black-soft);
}

.article-meta-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.tag-list {
  display: flex;
  gap: 0.375rem;
}

.tag {
  padding: 0.125rem 0.5rem;
  background: rgba(0, 117, 74, 0.08);
  color: var(--color-green-accent);
  border-radius: var(--radius-pill);
  font-size: 0.75rem;
}

.empty-state {
  text-align: center;
  padding: 3rem 1rem;
}

.empty-state-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 3rem;
}

.loading-spinner {
  width: 2rem;
  height: 2rem;
  border: 2px solid var(--color-neutral-cool);
  border-top-color: var(--color-green-accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
