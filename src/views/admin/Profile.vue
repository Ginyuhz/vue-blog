<template>
  <div class="admin-page">
    <div class="admin-nav">
      <router-link to="/admin/article" class="nav-item">文章管理</router-link>
      <router-link to="/admin/category" class="nav-item">分类管理</router-link>
      <router-link to="/admin/tag" class="nav-item">标签管理</router-link>
      <router-link to="/admin/profile" class="nav-item active">个人信息</router-link>
    </div>
    <div class="admin-header">
      <h1 class="page-title">个人信息</h1>
    </div>
    <div class="card edit-card">
      <div class="form-group">
        <label class="form-label">名称</label>
        <input
          type="text"
          class="form-input"
          v-model="form.name"
          placeholder="请输入名称"
        />
      </div>
      <div class="form-group">
        <label class="form-label">简介</label>
        <textarea
          class="form-input form-textarea"
          v-model="form.bio"
          placeholder="请输入个人简介"
          rows="4"
        ></textarea>
      </div>
      <div class="form-group">
        <label class="form-label">技能（逗号分隔）</label>
        <input
          type="text"
          class="form-input"
          v-model="form.skills"
          placeholder="Vue3, JavaScript, Python"
        />
      </div>
      <div class="form-group">
        <label class="form-label">Email</label>
        <input
          type="email"
          class="form-input"
          v-model="form.email"
          placeholder="example@email.com"
        />
      </div>
      <div class="form-group">
        <label class="form-label">GitHub</label>
        <input
          type="text"
          class="form-input"
          v-model="form.github"
          placeholder="https://github.com/username"
        />
      </div>
      <div class="form-actions">
        <button class="btn btn-primary" @click="handleSave" :disabled="saving">
          {{ saving ? '保存中...' : '保存' }}
        </button>
      </div>
      <div v-if="errorMsg" class="message message-error">{{ errorMsg }}</div>
      <div v-if="successMsg" class="message message-success">{{ successMsg }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getProfile, updateProfile } from '../../api/article'

const form = ref({
  name: '',
  bio: '',
  skills: '',
  email: '',
  github: ''
})

const saving = ref(false)
const errorMsg = ref('')
const successMsg = ref('')

const loadProfile = async () => {
  try {
    const res = await getProfile()
    if (res.data) {
      form.value = {
        name: res.data.name || '',
        bio: res.data.bio || '',
        skills: res.data.skills || '',
        email: res.data.email || '',
        github: res.data.github || ''
      }
    }
  } catch (e) {
    console.error('获取个人信息失败', e)
  }
}

const handleSave = async () => {
  errorMsg.value = ''
  successMsg.value = ''
  saving.value = true
  try {
    await updateProfile(form.value)
    successMsg.value = '保存成功'
    setTimeout(() => {
      successMsg.value = ''
    }, 2000)
  } catch (e) {
    errorMsg.value = e.message || '保存失败'
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadProfile()
})
</script>

<style scoped>
.admin-page {
  max-width: 800px;
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

.edit-card {
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-textarea {
  resize: vertical;
  min-height: 100px;
}

.form-actions {
  margin-top: 1.5rem;
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

.message-success {
  color: var(--color-success);
  background: rgba(34, 197, 94, 0.1);
  padding: 0.75rem;
  border-radius: var(--radius);
  margin-top: 1rem;
}
</style>
