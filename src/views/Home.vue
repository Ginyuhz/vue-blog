<template>
  <div class="page-wrapper">
    <main class="page-main">
      <!-- 星巴克风格特色区域 -->
      <div class="feature-band">
        <h2>欢迎来到我的技术博客</h2>
        <p>分享技术心得，记录学习历程。这里是一个温暖的技术社区，就像一杯香浓的咖啡，让你在忙碌的一天中找到片刻宁静。</p>
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
            <router-link :to="`/category?id=${article.category_id}`" class="article-meta-item category-link">
              <span>📁</span>
              {{ article.category_name }}
            </router-link>
            <span class="article-meta-item tag-list" v-if="getTags(article.tags).length">
              <router-link 
                v-for="tag in getTags(article.tags)" 
                :key="tag" 
                :to="`/tag?name=${encodeURIComponent(tag)}`" 
                class="tag"
              >
                {{ tag }}
              </router-link>
            </span>
          </div>
        </article>
      </div>
      <div v-if="loading" class="loading">
        <div class="loading-spinner"></div>
        <span>加载中...</span>
      </div>
      <div v-if="!loading && !articles.length" class="empty-state">
        <div class="empty-state-icon">📝</div>
        <p>暂无文章</p>
      </div>
    </main>
    <aside class="page-aside">
      <SideBar />
    </aside>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getArticleList, deleteArticle } from '../api/article'
import { useAuthStore } from '../stores/auth'
import SideBar from '../components/SideBar.vue'

const authStore = useAuthStore()
const articles = ref([])
const loading = ref(true)

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

const handleDelete = async (id) => {
  if (!confirm('确定要删除这篇文章吗？')) return
  try {
    await deleteArticle(id)
    articles.value = articles.value.filter(a => a.id !== id)
  } catch (e) {
    alert(e.message || '删除失败')
  }
}

onMounted(async () => {
  try {
    const res = await getArticleList()
    articles.value = res.data || []
  } catch (e) {
    console.error('获取文章列表失败', e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.article-item {
  cursor: pointer;
}

.article-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.article-title {
  display: block;
  flex: 1;
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

.tag-list {
  display: flex;
  gap: 0.375rem;
}

.tag {
  color: var(--color-green-accent);
  text-decoration: none;
  transition: var(--transition);
}

.tag:hover {
  color: var(--color-starbucks);
}

.category-link {
  color: var(--color-text-black-soft);
  text-decoration: none;
  transition: var(--transition);
}

.category-link:hover {
  color: var(--color-starbucks);
}

@media (max-width: 576px) {
  .article-header {
    flex-direction: column;
  }
  
  .article-actions {
    width: 100%;
  }
}
</style>
