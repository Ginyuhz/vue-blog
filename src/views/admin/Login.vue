<template>
  <div class="login-page">
    <div class="login-card card">
      <h1 class="login-title">管理员登录</h1>
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label class="form-label">用户名</label>
          <input
            type="text"
            class="form-input"
            v-model="form.username"
            placeholder="请输入用户名"
            required
          />
        </div>
        <div class="form-group">
          <label class="form-label">密码</label>
          <input
            type="password"
            class="form-input"
            v-model="form.password"
            placeholder="请输入密码"
            required
          />
        </div>
        <div v-if="errorMsg" class="message message-error">{{ errorMsg }}</div>
        <button type="submit" class="btn btn-primary btn-block" :disabled="loading">
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login } from '../../api/article'
import { useAuthStore } from '../../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
  username: '',
  password: ''
})
const loading = ref(false)
const errorMsg = ref('')

const handleLogin = async () => {
  errorMsg.value = ''
  loading.value = true
  try {
    const res = await login(form.value)
    authStore.setToken(res.data.token)
    router.push('/admin/article')
  } catch (e) {
    errorMsg.value = e.message || '登录失败'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 70vh;
  padding: 2rem;
}

.login-card {
  width: 100%;
  max-width: 420px;
  padding: 2.5rem;
}

.login-title {
  font-size: 1.75rem;
  font-weight: 700;
  text-align: center;
  margin-bottom: 2rem;
  color: var(--color-starbucks);
  letter-spacing: -0.16px;
}

.login-form {
  margin-top: 1.5rem;
}

.btn-block {
  width: 100%;
  padding: 12px 16px;
  font-size: 16px;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-input {
  padding: 14px 16px;
  font-size: 1rem;
}
</style>
