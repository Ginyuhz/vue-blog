<template>
  <div id="app" :class="{ dark: isDark }">
    <NavBar />
    <main class="main-content">
      <router-view />
    </main>
    <FooterBar />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useThemeStore } from './stores/theme'
import NavBar from './components/NavBar.vue'
import FooterBar from './components/FooterBar.vue'

const themeStore = useThemeStore()
const isDark = computed(() => themeStore.isDark)
</script>

<style scoped>
#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 5.5rem 1rem 2rem;
}
</style>
