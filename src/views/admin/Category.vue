<template>
  <div class="admin-page">
    <div class="admin-nav">
      <router-link to="/admin/article" class="nav-item">文章管理</router-link>
      <router-link to="/admin/category" class="nav-item active">分类管理</router-link>
      <router-link to="/admin/tag" class="nav-item">标签管理</router-link>
      <router-link to="/admin/profile" class="nav-item">个人信息</router-link>
    </div>
    <div class="admin-header">
      <h1 class="page-title">分类管理</h1>
      <div class="header-actions">
        <button class="btn btn-primary" @click="showAddModal = true">新增分类</button>
      </div>
    </div>
    <div class="card">
      <table class="category-table" v-if="categories.length">
        <thead>
          <tr>
            <th>分类名称</th>
            <th>文章数量</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="cat in categories" :key="cat.id">
            <td>{{ cat.name }}</td>
            <td>{{ cat.count }}</td>
            <td>
              <div class="action-btns">
                <button class="btn btn-outline btn-sm" @click="handleEdit(cat)">编辑</button>
                <button 
                  class="btn btn-danger btn-sm" 
                  @click="handleDelete(cat.id)"
                  :disabled="cat.count > 0"
                >
                  删除
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="!categories.length" class="empty-state">
        <div class="empty-state-icon">📁</div>
        <p>暂无分类</p>
      </div>
    </div>

    <!-- 新增/编辑分类弹窗 -->
    <div v-if="showAddModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ editingCategory ? '编辑分类' : '新增分类' }}</h3>
          <button class="modal-close" @click="closeModal">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label class="form-label">分类名称</label>
            <input
              type="text"
              class="form-input"
              v-model="form.name"
              placeholder="请输入分类名称"
            />
          </div>
          <div v-if="errorMsg" class="message message-error">{{ errorMsg }}</div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline" @click="closeModal">取消</button>
          <button class="btn btn-primary" @click="handleSubmit">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getCategoryList, createCategory, updateCategory, deleteCategory } from '../../api/article'

const categories = ref([])
const showAddModal = ref(false)
const editingCategory = ref(null)
const form = ref({ name: '' })
const errorMsg = ref('')

const loadCategories = async () => {
  try {
    const res = await getCategoryList()
    categories.value = res.data || []
  } catch (e) {
    console.error('获取分类失败', e)
  }
}

const handleEdit = (cat) => {
  editingCategory.value = cat
  form.value = { name: cat.name }
  showAddModal.value = true
}

const handleDelete = async (id) => {
  if (!confirm('确定要删除该分类吗？')) return
  try {
    await deleteCategory(id)
    categories.value = categories.value.filter(cat => cat.id !== id)
  } catch (e) {
    alert(e.message || '删除失败')
  }
}

const closeModal = () => {
  showAddModal.value = false
  editingCategory.value = null
  form.value = { name: '' }
  errorMsg.value = ''
}

const handleSubmit = async () => {
  if (!form.value.name.trim()) {
    errorMsg.value = '请输入分类名称'
    return
  }
  
  try {
    if (editingCategory.value) {
      await updateCategory(editingCategory.value.id, { name: form.value.name })
    } else {
      await createCategory({ name: form.value.name })
    }
    closeModal()
    loadCategories()
  } catch (e) {
    errorMsg.value = e.message || '保存失败'
  }
}

onMounted(() => {
  loadCategories()
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

.article-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  border-bottom: 1px solid var(--color-border);
}

.article-item:last-child {
  border-bottom: none;
}

.article-title {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-right: 1rem;
}

.form-select {
  padding: 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  background: var(--color-card-bg);
  min-width: 120px;
}

.empty-tip {
  text-align: center;
  color: var(--color-text-black-soft);
  padding: 2rem;
}

.modal-large {
  max-width: 600px;
}

.col-checkbox {
  width: 40px;
  text-align: center;
}

.action-btns {
  display: flex;
  gap: 0.5rem;
}

.btn-sm {
  padding: 4px 12px;
  font-size: 0.75rem;
}

.btn-outline:disabled,
.btn-danger:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
