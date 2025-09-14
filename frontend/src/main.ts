import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './styles/index.css'

const app = createApp(App)
const pinia = createPinia()

// 初始化认证状态
const initApp = async () => {
  // 这里可以添加全局的初始化逻辑
  app.use(pinia)
  app.use(router)
  app.use(ElementPlus)
  
  app.mount('#app')
}

initApp()