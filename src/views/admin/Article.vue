<template>
  <div class="admin-page">
    <div class="admin-nav">
      <router-link to="/admin/article" class="nav-item active">文章管理</router-link>
      <router-link to="/admin/category" class="nav-item">分类管理</router-link>
      <router-link to="/admin/tag" class="nav-item">标签管理</router-link>
      <router-link to="/admin/profile" class="nav-item">个人信息</router-link>
    </div>
    <div class="admin-header">
      <h1 class="page-title">文章管理</h1>
      <div class="header-actions">
        <button
          v-if="selectedIds.length > 0"
          class="btn btn-danger"
          @click="handleBatchDelete"
        >
          批量删除 ({{ selectedIds.length }})
        </button>
        <router-link to="/admin/article/edit" class="btn btn-primary">新增文章</router-link>
      </div>
    </div>
    <div class="card">
      <table class="article-table" v-if="articles.length">
        <thead>
          <tr>
            <th class="col-checkbox">
              <input
                type="checkbox"
                :checked="isAllSelected"
                :indeterminate="selectedIds.length > 0 && !isAllSelected"
                @change="toggleSelectAll"
              />
            </th>
            <th>标题</th>
            <th>分类</th>
            <th>标签</th>
            <th>时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="article in articles" :key="article.id" :class="{ selected: selectedIds.includes(article.id) }">
            <td class="col-checkbox">
              <input
                type="checkbox"
                :checked="selectedIds.includes(article.id)"
                @change="toggleSelect(article.id)"
              />
            </td>
            <td>{{ article.title }}</td>
            <td>{{ article.category_name }}</td>
            <td>
              <span v-for="tag in getTags(article.tags)" :key="tag" class="tag-item">
                {{ tag }}
              </span>
            </td>
            <td>{{ formatDate(article.created_at) }}</td>
            <td>
              <div class="action-btns">
                <router-link :to="`/admin/article/edit?id=${article.id}`" class="btn btn-outline btn-sm">
                  编辑
                </router-link>
                <button class="btn btn-danger btn-sm" @click="handleDelete(article.id)">
                  删除
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="loading" class="loading">
        <div class="loading-spinner"></div>
        <span>加载中...</span>
      </div>
      <div v-if="!loading && !articles.length" class="empty-state">
        <div class="empty-state-icon">📝</div>
        <p>暂无文章</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getArticleList, deleteArticle, batchDeleteArticle } from '../../api/article'

const articles = ref([])
const loading = ref(true)
const selectedIds = ref([])

const isAllSelected = computed(() => {
  return articles.value.length > 0 && selectedIds.value.length === articles.value.length
})

const toggleSelect = (id) => {
  const idx = selectedIds.value.indexOf(id)
  if (idx === -1) {
    selectedIds.value.push(id)
  } else {
    selectedIds.value.splice(idx, 1)
  }
}

const toggleSelectAll = () => {
  if (isAllSelected.value) {
    selectedIds.value = []
  } else {
    selectedIds.value = articles.value.map(a => a.id)
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

// 解析标签：支持多种格式
const getTags = (tagsStr) => {
  if (!tagsStr) return []
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
    selectedIds.value = selectedIds.value.filter(sid => sid !== id)
  } catch (e) {
    alert(e.message || '删除失败')
  }
}

const handleBatchDelete = async () => {
  if (!confirm(`确定要删除选中的 ${selectedIds.value.length} 篇文章吗？`)) return
  try {
    const res = await batchDeleteArticle(selectedIds.value)
    const { success, fail } = res.data || {}
    
    // 移除成功删除的文章
    const successIds = Array.isArray(success) ? success.map(s => s.id) : []
    articles.value = articles.value.filter(a => !successIds.includes(a.id))
    selectedIds.value = []
    
    // 显示结果
    if (Array.isArray(fail) && fail.length > 0) {
      const failNames = fail.map(f => f.title || `ID: ${f.id}`).join('、')
      alert(`${res.msg}\n失败的文章：${failNames}`)
    } else {
      alert(res.msg)
    }
  } catch (e) {
    alert(e.message || '批量删除失败')
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
.admin-page {
  max-width: 1000px;
  margin: 0 auto;
  padding: 1.6rem;
}

.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.page-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--color-starbucks);
  letter-spacing: -0.16px;
}

.article-table {
  width: 100%;
  border-collapse: collapse;
}

.article-table th,
.article-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.article-table th {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-black-soft);
  letter-spacing: -0.01em;
}

.article-table td {
  font-size: 0.875rem;
  color: var(--color-text-black);
}

.btn-sm {
  padding: 4px 12px;
  font-size: 0.75rem;
}

.ml-1 {
  margin-left: 0.5rem;
}

.admin-nav {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.nav-item {
  padding: 0.5rem 1.25rem;
  border-radius: var(--radius-pill);
  font-size: 0.875rem;
  font-weight: 500;
  letter-spacing: -0.01em;
  transition: var(--transition);
  color: var(--color-text-black);
}

.nav-item:hover {
  background: rgba(0, 117, 74, 0.05);
}

.nav-item.active {
  background: var(--color-green-accent);
  color: white;
}

.tag-item {
  display: inline-block;
  padding: 2px 8px;
  margin: 2px;
  background: rgba(0, 117, 74, 0.1);
  color: var(--color-green-accent);
  border-radius: var(--radius-pill);
  font-size: 0.75rem;
}

.action-btns {
  display: flex;
  gap: 0.5rem;
}

.col-checkbox {
  width: 40px;
  text-align: center;
}

.col-checkbox input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: var(--color-green-accent);
}

tr.selected {
  background: rgba(0, 117, 74, 0.05);
}

.header-actions {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}
</style>
