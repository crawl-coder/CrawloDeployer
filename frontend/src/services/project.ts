import api from './api'
import type { Project, ProjectUpdate } from '../types/project'
import type { ApiResponse } from '../types/api'

// 获取项目列表
export const getProjects = async (params?: {
  skip?: number
  limit?: number
}): Promise<ApiResponse<Project[]>> => {
  const response = await api.get<ApiResponse<Project[]>>('/projects/', { params })
  return response.data
}

// 获取项目详情
export const getProjectById = async (id: number): Promise<ApiResponse<Project>> => {
  // 修复API路径，移除末尾的斜杠
  const response = await api.get<ApiResponse<Project>>(`/projects/${id}`)
  return response.data
}

// 创建项目
export const createProject = async (formData: FormData): Promise<ApiResponse<Project>> => {
  const response = await api.post<ApiResponse<Project>>('/projects/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
      }
  })
  return response.data
}

// 更新项目
export const updateProject = async (id: number, project: ProjectUpdate): Promise<ApiResponse<Project>> => {
  // 修复API路径，移除末尾的斜杠
  const response = await api.put<ApiResponse<Project>>(`/projects/${id}`, project)
  return response.data
}

// 删除项目
export const deleteProject = async (id: number): Promise<ApiResponse<Project>> => {
  // 修复API路径，移除末尾的斜杠
  const response = await api.delete<ApiResponse<Project>>(`/projects/${id}`)
  return response.data
}

// 同步项目到节点
export const syncProjectToNodes = async (id: number, nodeHostnames: string[]): Promise<ApiResponse<any>> => {
  // 修复API路径，移除末尾的斜杠
  const response = await api.post<ApiResponse<any>>(`/projects/${id}/sync`, { node_hostnames: nodeHostnames })
  return response.data
}

// 获取项目文件列表
export const getProjectFiles = async (id: number): Promise<ApiResponse<string[]>> => {
  // 修复API路径，移除末尾的斜杠
  const response = await api.get<ApiResponse<string[]>>(`/projects/${id}/files`)
  return response.data
}

// 获取项目统计信息
export const getProjectStats = async (id: number): Promise<ApiResponse<any>> => {
  // 修复API路径，移除末尾的斜杠
  const response = await api.get<ApiResponse<any>>(`/projects/${id}/stats`)
  return response.data
}