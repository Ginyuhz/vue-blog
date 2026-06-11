<template>
  <div class="page-wrapper">
    <main class="page-main">
      <!-- 显示分类下的文章列表 -->
      <div v-if="categoryId">
        <div class="page-header">
          <h1 class="page-title">{{ categoryName }}</h1>
          <p class="text-secondary">该分类下的文章</p>
        </div>
        <div class="article-list" v-if="!loading && articles.length">
          <article v-for="article in articles" :key="article.id" class="article-item card">
            <router-link :to="`/article/${article.id}`" class="article-title">
              {{ article.title }}
            </router-link>
            <p class="article-excerpt">{{ article.excerpt }}</p>
            <div class="article-meta">
              <span class="article-meta-item">
                <span>📅</span>
                {{ formatDate(article.created_at) }}
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
          <p>该分类下暂无文章</p>
          <router-link to="/category" class="btn btn-outline mt-2">查看全部分类</router-link>
        </div>
      </div>
      
      <!-- 显示所有分类 -->
      <div v-else>
        <div class="page-header">
          <h1 class="page-title">分类</h1>
          <p class="text-secondary">按分类浏览文章</p>
        </div>
        <div class="category-grid" v-if="categories.length">
          <router-link
            v-for="cat in categories"
            :key="cat.id"
            :to="`/category?id=${cat.id}`"
            class="category-card card"
          >
            <h3 class="category-name">{{ cat.name }}</h3>
            <p class="category-count text-secondary">{{ cat.count }} 篇文章</p>
          </router-link>
        </div>
        <div v-if="loading" class="loading">
          <div class="loading-spinner"></div>
          <span>加载中...</span>
        </div>
        <div v-if="!loading && !categories.length" class="empty-state">
          <div class="empty-state-icon">📁</div>
          <p>暂无分类</p>
        </div>
      </div>
    </main>
    <aside class="page-aside">
      <SideBar />
    </aside>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useRoute } from 'vue-router'
import { getCategoryList, getArticleList } from '../api/article'
import SideBar from '../components/SideBar.vue'

const route = useRoute()
const categories = ref([])
const articles = ref([])
const loading = ref(true)

const categoryId = computed(() => route.query.id ? parseInt(route.query.id) : null)
const categoryName = computed(() => {
  if (!categoryId.value) return ''
  const cat = categories.value.find(c => c.id === categoryId.value)
  return cat ? cat.name : ''
})

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

const loadCategories = async () => {
  try {
    const res = await getCategoryList()
    console.log('Categories response:', res)
    categories.value = res.data || []
  } catch (e) {
    console.error('获取分类列表失败', e)
    categories.value = []
  }
}

const loadArticles = async (id) => {
  loading.value = true
  try {
    const res = await getArticleList({ category_id: id })
    articles.value = res.data || []
  } catch (e) {
    console.error('获取文章列表失败', e)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  loading.value = true
  try {
    await loadCategories()
    if (categoryId.value) {
      await loadArticles(categoryId.value)
    }
  } catch (e) {
    console.error('加载数据失败', e)
  } finally {
    loading.value = false
  }
})

// 监听路由参数变化
watch(() => route.query.id, async (newId) => {
  if (newId) {
    await loadArticles(parseInt(newId))
  } else {
    articles.value = []
    loading.value = false
  }
})
</script>

<style scoped>
.page-header {
  margin-bottom: 1.5rem;
}

.page-title {
  font-size: 1.75rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  color: var(--color-starbucks);
  letter-spacing: -0.02em;
}

.category-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1.25rem;
}

.category-card {
  padding: 1.5rem;
  text-align: center;
  transition: var(--transition);
}

.category-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-card-hover);
}

.category-name {
  font-size: 1.125rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: var(--color-text-black);
}

.category-count {
  font-size: 0.875rem;
}

.article-item {
  cursor: pointer;
  margin-bottom: 1rem;
}

.article-title {
  display: block;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-starbucks);
  margin-bottom: 0.5rem;
  transition: var(--transition);
}

.article-title:hover {
  color: var(--color-green-accent);
}

.article-excerpt {
  color: var(--color-text-black-soft);
  font-size: 0.875rem;
  line-height: 1.6;
  margin-bottom: 0.75rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.article-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.75rem;
  color: var(--color-text-black-soft);
}

.article-meta-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}
</style>
