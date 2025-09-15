import api from './api'
import type { User, UserStats, UserUpdate, PasswordUpdate } from '../types/auth'

// 获取用户资料
export const getProfile = async (): Promise<User> => {
  const response = await api.get<User>('/users/me/')
  return response.data
}

// 更新用户资料
export const updateProfile = async (userData: UserUpdate): Promise<User> => {
  const response = await api.put<User>('/users/me/', userData)
  return response.data
}

// 更新密码
export const updatePassword = async (passwordData: PasswordUpdate): Promise<any> => {
  const response = await api.put('/users/me/password/', passwordData)
  return response.data
}

// 获取用户统计
export const getStats = async (): Promise<UserStats> => {
  const response = await api.get<UserStats>('/users/me/stats/')
  return response.data
}

// 更新通知设置
export const updateNotifications = async (notificationData: any): Promise<any> => {
  const response = await api.put('/users/me/notifications/', notificationData)
  return response.data
}

// 退出所有设备
export const logoutAll = async (): Promise<any> => {
  const response = await api.post('/users/me/logout-all/')
  return response.data
}

// 注销账户
export const deleteAccount = async (): Promise<any> => {
  const response = await api.delete('/users/me/')
  return response.data
}