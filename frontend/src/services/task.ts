import api from './api'
import type { Task, TaskCreate, TaskUpdate, TaskRun } from '@/types/task'

// 获取任务列表
export const getTasks = async (params?: {
  skip?: number
  limit?: number
}): Promise<Task[]> => {
  const response = await api.get<Task[]>('/tasks/', { params })
  return response.data
}

// 获取任务详情
export const getTask = async (id: number): Promise<Task> => {
  const response = await api.get<Task>(`/tasks/${id}/`)
  return response.data
}

// 创建任务
export const createTask = async (taskData: TaskCreate): Promise<Task> => {
  const response = await api.post<Task>('/tasks/', taskData)
  return response.data
}

// 更新任务
export const updateTask = async (id: number, taskData: TaskUpdate): Promise<Task> => {
  const response = await api.put<Task>(`/tasks/${id}/`, taskData)
  return response.data
}

// 删除任务
export const deleteTask = async (id: number): Promise<Task> => {
  const response = await api.delete<Task>(`/tasks/${id}/`)
  return response.data
}

// 启用/禁用任务
export const toggleTask = async (id: number, enable: boolean): Promise<Task> => {
  const response = await api.post<Task>(`/tasks/${id}/toggle/`, { enable })
  return response.data
}

// 立即执行任务
export const runTask = async (id: number): Promise<TaskRun> => {
  const response = await api.post<TaskRun>(`/tasks/${id}/run/`)
  return response.data
}

// 获取任务统计
export const getTaskStats = async (id: number): Promise<any> => {
  const response = await api.get<any>(`/tasks/${id}/stats/`)
  return response.data
}

// 获取任务概览统计
export const getTasksOverviewStats = async (): Promise<any> => {
  const response = await api.get<any>('/tasks/stats/overview/')
  return response.data
}

// 添加任务依赖
export const addTaskDependencies = async (id: number, dependencyIds: number[]): Promise<Task> => {
  const response = await api.post<Task>(`/tasks/${id}/dependencies/`, dependencyIds)
  return response.data
}

// 获取任务依赖
export const getTaskDependencies = async (id: number): Promise<Task[]> => {
  const response = await api.get<Task[]>(`/tasks/${id}/dependencies/`)
  return response.data
}

// 清除任务依赖
export const clearTaskDependencies = async (id: number): Promise<Task> => {
  const response = await api.delete<Task>(`/tasks/${id}/dependencies/`)
  return response.data
}