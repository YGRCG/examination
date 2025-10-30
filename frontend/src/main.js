import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import Vant from 'vant'
import 'element-plus/dist/index.css'
import 'vant/lib/index.css'
import App from './App.vue'
import router from './router'
import axios from 'axios'

// 创建应用实例
const app = createApp(App)
const pinia = createPinia()

// 配置axios全局默认值
axios.defaults.baseURL = '/api'
axios.defaults.timeout = 10000

// 请求拦截器 - 添加token
axios.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器 - 处理统一响应格式
axios.interceptors.response.use(
  response => {
    const res = response.data
    if (res.status === 'error') {
      // 处理错误情况
      console.error(res.message)
      // 可以在这里统一处理错误提示
    }
    return res
  },
  error => {
    console.error('网络错误:', error)
    return Promise.reject(error)
  }
)

// 全局注册axios
app.config.globalProperties.$axios = axios

// 使用插件
app.use(pinia)
app.use(router)
app.use(ElementPlus)
app.use(Vant)

// 挂载应用
app.mount('#app')