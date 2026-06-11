<template>
  <nav class="navbar">
    <div class="container navbar-content">
      <router-link to="/" class="navbar-brand">技术博客</router-link>
      <div class="navbar-menu">
        <router-link to="/" class="nav-link">首页</router-link>
        <router-link to="/category" class="nav-link">分类</router-link>
        <router-link to="/tag" class="nav-link">标签</router-link>
        <router-link to="/about" class="nav-link">关于</router-link>
      </div>
      <div class="navbar-actions">
        <button class="theme-toggle" @click="toggleTheme" :title="isDark ? '切换浅色' : '切换暗黑'">
          {{ isDark ? '☀️' : '🌙' }}
        </button>
        <template v-if="authStore.isLoggedIn">
          <router-link to="/admin/article" class="nav-link">管理</router-link>
          <button class="btn-logout" @click="handleLogout">退出</button>
        </template>
        <router-link v-else to="/admin/login" class="nav-link">登录</router-link>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useThemeStore } from '../stores/theme'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const themeStore = useThemeStore()
const authStore = useAuthStore()
const isDark = computed(() => themeStore.isDark)

const toggleTheme = () => {
  themeStore.toggleTheme()
}

const handleLogout = () => {
  authStore.logout()
  router.push('/')
}
</script>

<style scoped>
.navbar {
  background: var(--color-nav-bg);
  box-shadow: var(--shadow-nav);
  position: sticky;
  top: 0;
  z-index: 100;
}

.navbar-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 3.5rem;
}

.navbar-brand {
  font-size: 1.375rem;
  font-weight: 700;
  color: var(--color-starbucks);
  letter-spacing: -0.16px;
}

.navbar-menu {
  display: flex;
  gap: 2rem;
}

.nav-link {
  color: var(--color-text-black);
  font-size: 0.9375rem;
  font-weight: 500;
  letter-spacing: -0.01em;
  transition: var(--transition);
}

.nav-link:hover,
.nav-link.router-link-active {
  color: var(--color-green-accent);
}

.navbar-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.theme-toggle {
  font-size: 1.25rem;
  padding: 0.5rem;
  border-radius: 50%;
  transition: var(--transition);
  cursor: pointer;
  border: none;
  background: transparent;
}

.theme-toggle:hover {
  background: var(--color-neutral-cool);
}

.btn-logout {
  padding: 0.375rem 0.875rem;
  background: transparent;
  color: var(--color-text-black-soft);
  border: 1px solid rgba(0, 0, 0, 0.15);
  border-radius: var(--radius-pill);
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
}

.btn-logout:hover {
  background: var(--color-neutral-cool);
  color: var(--color-text-black);
}

@media (max-width: 768px) {
  .navbar-menu {
    display: none;
  }
}
</style>
