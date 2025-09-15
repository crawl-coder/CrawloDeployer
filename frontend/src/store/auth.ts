import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi, register as registerApi, getUserInfo } from '../services/auth'
import type { LoginRequest, RegisterRequest, User } from '../types/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)
  
  const isAuthenticated = computed(() => !!token.value)
  
  // 登录
  const login = async (credentials: LoginRequest) => {
    try {
      console.log('尝试登录:', credentials.username)
      const response = await loginApi(credentials)
      console.log('登录响应:', response)
      token.value = response.access_token
      console.log('设置token到store:', token.value)
      localStorage.setItem('token', response.access_token)
      console.log('设置token到localStorage:', response.access_token)
      
      // 获取用户信息 - 直接传递token以避免localStorage同步问题
      console.log('获取用户信息...')
      const userInfo = await getUserInfo(response.access_token)
      user.value = userInfo
      
      console.log('登录成功')
      return { success: true }
    } catch (error: any) {
      console.error('登录失败:', error)
      // 清除可能存储的无效token
      token.value = null
      localStorage.removeItem('token')
      return { success: false, message: error.message || '登录失败' }
    }
  }
  
  // 注册
  const register = async (userData: RegisterRequest) => {
    try {
      await registerApi(userData)
      return { success: true }
    } catch (error: any) {
      return { success: false, message: error.message }
    }
  }
  
  // 获取用户信息
  const fetchUserInfo = async (token?: string) => {
    try {
      const userInfo = await getUserInfo(token)
      user.value = userInfo
      return { success: true }
    } catch (error: any) {
      console.error('获取用户信息失败:', error)
      logout()
      return { success: false, message: error.message || '获取用户信息失败' }
    }
  }
  
  // 登出
  const logout = () => {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
  }
  
  // 初始化认证状态
  const initAuth = async () => {
    const savedToken = localStorage.getItem('token')
    console.log('初始化认证状态，本地token:', savedToken)
    if (savedToken) {
      token.value = savedToken
      console.log('设置store中的token:', savedToken)
      try {
        await fetchUserInfo(savedToken)
      } catch (error) {
        console.error('初始化用户信息失败:', error)
        // 如果获取用户信息失败，清除token
        token.value = null
        localStorage.removeItem('token')
      }
    }
  }
  
  return {
    user,
    token,
    isAuthenticated,
    login,
    register,
    fetchUserInfo,
    logout,
    initAuth
  }
})