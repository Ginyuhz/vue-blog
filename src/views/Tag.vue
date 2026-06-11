<template>
  <div class="page-wrapper">
    <main class="page-main">
      <!-- 显示标签下的文章列表 -->
      <div v-if="tagId">
        <div class="page-header">
          <h1 class="page-title">#{{ tagName }}</h1>
          <p class="text-secondary">该标签下的文章</p>
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
          <p>该标签下暂无文章</p>
          <router-link to="/tag" class="btn btn-outline mt-2">查看全部标签</router-link>
        </div>
      </div>
      
      <!-- 显示所有标签 -->
      <div v-else>
        <div class="page-header">
          <h1 class="page-title">标签</h1>
          <p class="text-secondary">按标签筛选文章</p>
        </div>
        <div class="tag-cloud" v-if="tags.length">
          <router-link
            v-for="tag in tags"
            :key="tag.id"
            :to="`/tag?id=${tag.id}`"
            class="tag-cloud-item"
          >
            <span class="tag-name">{{ tag.name }}</span>
            <span class="tag-count">{{ tag.count }}</span>
          </router-link>
        </div>
        <div v-if="loading" class="loading">
          <div class="loading-spinner"></div>
          <span>加载中...</span>
        </div>
        <div v-if="!loading && !tags.length" class="empty-state">
          <div class="empty-state-icon">🏷️</div>
          <p>暂无标签</p>
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
import { getTagList, getArticleList } from '../api/article'
import SideBar from '../components/SideBar.vue'

const route = useRoute()
const tags = ref([])
const articles = ref([])
const loading = ref(true)

const tagId = computed(() => {
  const id = route.query.id
  return id ? parseInt(id) : null
})

const tagNameFromQuery = computed(() => route.query.name || '')
const tagName = computed(() => {
  if (tagNameFromQuery.value) return tagNameFromQuery.value
  if (!tagId.value) return ''
  const tag = tags.value.find(t => t.id === tagId.value)
  return tag ? tag.name : ''
})

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

const loadTags = async () => {
  try {
    const res = await getTagList()
    console.log('Tags response:', res)
    tags.value = res.data || []
  } catch (e) {
    console.error('获取标签列表失败', e)
    tags.value = []
  }
}

const loadArticles = async (idOrName) => {
  loading.value = true
  try {
    let tagName = idOrName
    // 如果是数字 id，从列表中查找对应的标签名
    if (typeof idOrName === 'number' || !isNaN(parseInt(idOrName))) {
      const id = parseInt(idOrName)
      const tag = tags.value.find(t => t.id === id)
      tagName = tag?.name
    }
    if (!tagName) {
      articles.value = []
      return
    }
    const res = await getArticleList({ tag: tagName })
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
    await loadTags()
    if (tagNameFromQuery.value) {
      await loadArticles(tagNameFromQuery.value)
    } else if (tagId.value) {
      await loadArticles(tagId.value)
    }
  } catch (e) {
    console.error('加载数据失败', e)
  } finally {
    loading.value = false
  }
})

// 监听路由参数变化
watch(() => route.query, async (newQuery) => {
  const newId = newQuery.id
  const newName = newQuery.name
  if (newName) {
    await loadArticles(newName)
  } else if (newId) {
    await loadArticles(parseInt(newId))
  } else {
    articles.value = []
    loading.value = false
  }
}, { deep: true })
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

.tag-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.tag-cloud-item {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: var(--color-card-bg);
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: var(--radius-pill);
  transition: var(--transition);
  color: var(--color-text-black);
}

.tag-cloud-item:hover {
  border-color: var(--color-green-accent);
  background: var(--color-green-accent);
  color: #fff;
}

.tag-name {
  font-size: 0.875rem;
}

.tag-count {
  font-size: 0.75rem;
  opacity: 0.7;
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
