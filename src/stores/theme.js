import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const isDark = ref(false)

  // 监听 isDark 变化，更新 html 元素的 class
  watch(isDark, (dark) => {
    if (dark) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, { immediate: true })

  const toggleTheme = () => {
    isDark.value = !isDark.value
  }

  return {
    isDark,
    toggleTheme
  }
})
