<template>
  <div class="page-wrapper">
    <main class="page-main">
      <div class="about-page card">
        <div class="about-header">
          <h1 class="page-title">关于我</h1>
          <router-link v-if="authStore.isLoggedIn" to="/admin/profile" class="btn btn-outline btn-sm">
            编辑
          </router-link>
        </div>
        <div class="divider"></div>
        <div class="about-content" v-if="profile">
          <p v-for="(line, index) in bioLines" :key="index">{{ line }}</p>
          <div class="divider"></div>
          <h2>技术栈</h2>
          <div class="skill-list">
            <span v-for="skill in skillList" :key="skill" class="tag">{{ skill }}</span>
          </div>
          <div class="divider"></div>
          <h2>联系方式</h2>
          <p v-if="profile.email">Email: {{ profile.email }}</p>
          <p v-if="profile.github">GitHub: <a :href="profile.github" target="_blank">{{ profile.github }}</a></p>
        </div>
        <div v-if="loading" class="loading">
          <div class="loading-spinner"></div>
          <span>加载中...</span>
        </div>
      </div>
    </main>
    <aside class="page-aside">
      <SideBar />
    </aside>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getProfile } from '../api/article'
import { useAuthStore } from '../stores/auth'
import SideBar from '../components/SideBar.vue'

const authStore = useAuthStore()
const profile = ref(null)
const loading = ref(true)

const bioLines = computed(() => {
  if (!profile.value?.bio) return []
  return profile.value.bio.split('\n').filter(line => line.trim())
})

const skillList = computed(() => {
  if (!profile.value?.skills) return []
  return profile.value.skills.split(',').map(s => s.trim()).filter(s => s)
})

onMounted(async () => {
  try {
    const res = await getProfile()
    profile.value = res.data
  } catch (e) {
    console.error('获取个人信息失败', e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.about-page {
  padding: 2rem;
}

.about-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  font-size: 1.75rem;
  font-weight: 700;
}

.btn-sm {
  padding: 4px 12px;
  font-size: 0.75rem;
}

.about-content {
  line-height: 1.8;
}

.about-content p {
  margin: 0.75rem 0;
}

.about-content h2 {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 1.5rem 0 0.75rem;
}

.skill-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}
</style>
