<template>
  <div class="admin-page">
    <div class="admin-nav">
      <router-link to="/admin/article" class="nav-item">文章管理</router-link>
      <router-link to="/admin/category" class="nav-item">分类管理</router-link>
      <router-link to="/admin/tag" class="nav-item active">标签管理</router-link>
      <router-link to="/admin/profile" class="nav-item">个人信息</router-link>
    </div>
    <div class="admin-header">
      <h1 class="page-title">标签管理</h1>
      <div class="header-actions">
        <button class="btn btn-primary" @click="showAddModal = true">新增标签</button>
      </div>
    </div>
    <div class="card">
      <table class="tag-table" v-if="tags.length">
        <thead>
          <tr>
            <th>标签名称</th>
            <th>文章数量</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="tag in tags" :key="tag.id">
            <td>{{ tag.name }}</td>
            <td>{{ tag.count }}</td>
            <td>
              <div class="action-btns">
                <button class="btn btn-outline btn-sm" @click="handleEdit(tag)">编辑</button>
                <button class="btn btn-danger btn-sm" @click="handleDelete(tag.id)">删除</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="loading" class="loading">
        <div class="loading-spinner"></div>
        <span>加载中...</span>
      </div>
      <div v-if="!loading && !tags.length" class="empty-state">
        <div class="empty-state-icon">🏷️</div>
        <p>暂无标签</p>
      </div>
    </div>

    <!-- 新增/编辑标签模态框 -->
    <div class="modal-overlay" v-if="showAddModal" @click.self="closeModal">
      <div class="modal card">
        <h3 class="modal-title">{{ editingTag ? '编辑标签' : '新增标签' }}</h3>
        <div class="form-group">
          <label class="form-label">标签名称</label>
          <input
            type="text"
            class="form-input"
            v-model="form.name"
            placeholder="请输入标签名称"
          />
        </div>
        <div class="modal-actions">
          <button class="btn btn-outline" @click="closeModal">取消</button>
          <button class="btn btn-primary" @click="handleSubmit" :disabled="saving">
            {{ saving ? '保存中...' : '保存' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getTagList, createTag, updateTag, deleteTag } from '../../api/article'

const tags = ref([])
const loading = ref(true)
const showAddModal = ref(false)
const editingTag = ref(null)
const form = ref({ name: '' })
const saving = ref(false)

const loadTags = async () => {
  try {
    const res = await getTagList()
    tags.value = res.data || []
  } catch (e) {
    console.error('获取标签失败', e)
  } finally {
    loading.value = false
  }
}

const handleEdit = (tag) => {
  editingTag.value = tag
  form.value = { name: tag.name }
  showAddModal.value = true
}

const handleDelete = async (id) => {
  if (!confirm('确定要删除该标签吗？')) return
  try {
    await deleteTag(id)
    tags.value = tags.value.filter(tag => tag.id !== id)
  } catch (e) {
    alert(e.message || '删除失败')
  }
}

const closeModal = () => {
  showAddModal.value = false
  editingTag.value = null
  form.value = { name: '' }
}

const handleSubmit = async () => {
  if (!form.value.name.trim()) {
    return
  }
  
  saving.value = true
  try {
    if (editingTag.value) {
      await updateTag(editingTag.value.id, { name: form.value.name })
    } else {
      await createTag({ name: form.value.name })
    }
    closeModal()
    loadTags()
  } catch (e) {
    console.error('保存失败', e)
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadTags()
})
</script>

<style scoped>
.admin-page {
  max-width: 1000px;
  margin: 0 auto;
  padding: 1.6rem;
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

.action-btns {
  display: flex;
  gap: 0.5rem;
}

.btn-sm {
  padding: 4px 12px;
  font-size: 0.75rem;
}
</style>
