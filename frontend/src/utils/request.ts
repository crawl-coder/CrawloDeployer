import axios, { AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios'

// 创建axios实例
const service = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
service.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
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
service.interceptors.response.use(
  (response: AxiosResponse) => {
    return response.data
  },
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // token过期或无效，清除本地存储并跳转到登录页
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// 封装请求方法
const request = async <T = any>(config: AxiosRequestConfig): Promise<T> => {
  try {
    const response: AxiosResponse<T> = await service(config)
    return response.data
  } catch (error) {
    throw error
  }
}

export default request