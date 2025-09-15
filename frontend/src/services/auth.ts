import api from './api'
import type { LoginRequest, RegisterRequest, TokenResponse, User } from '../types/auth'

// 登录
export const login = async (credentials: LoginRequest): Promise<TokenResponse> => {
  const response = await api.post<TokenResponse>('/auth/login', 
    new URLSearchParams({
      username: credentials.username,
      password: credentials.password
    }), 
    {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    }
  )
  return response.data
}

// 注册
export const register = async (userData: RegisterRequest): Promise<void> => {
  await api.post('/users', userData)
}

// 获取用户信息
export const getUserInfo = async (token?: string): Promise<User> => {
  // 如果提供了token，使用它设置Authorization头
  const config = token ? { 
    headers: { 
      'Authorization': `Bearer ${token}` 
    } 
  } : {};
  
  // 使用带拦截器的api实例，确保正确的头部设置
  // 注意：去掉URL末尾的斜杠以避免307重定向
  const response = await api.get<User>('/users/me', config)
  return response.data
}

// 更新用户信息
export const updateUserInfo = async (userData: Partial<User>): Promise<User> => {
  const response = await api.put<User>('/users/me', userData)
  return response.data
}

// 更新密码
export const updatePassword = async (passwordData: {
  current_password: string
  new_password: string
}): Promise<void> => {
  await api.put('/users/me/password', passwordData)
}