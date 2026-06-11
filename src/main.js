import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import './assets/css/reset.css'
import './assets/css/global.css'
import './assets/css/common.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
