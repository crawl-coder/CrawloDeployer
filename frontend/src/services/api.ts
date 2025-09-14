import axios from 'axios'

// 创建带拦截器的axios实例
const api = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 创建不带拦截器的axios实例，用于认证相关请求
const unauthenticatedApi = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 首先尝试从localStorage获取token
    let token = localStorage.getItem('token')
    
    // 如果localStorage中没有token，尝试从内存中获取
    if (!token) {
      // 这里我们无法直接访问store，所以需要依赖localStorage
      // 但在登录过程中，token可能还未写入localStorage
    }
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response?.status === 401) {
      // token过期或无效，清除本地存储
      localStorage.removeItem('token')
      // 如果当前不在登录页，重定向到登录页
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default api
export { unauthenticatedApi }