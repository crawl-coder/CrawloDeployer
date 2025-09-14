import api from './api'
import type { Project, ProjectCreate, ProjectUpdate } from '@/types/project'

// 获取项目列表
export const getProjects = async (params?: {
  skip?: number
  limit?: number
}): Promise<Project[]> => {
  const response = await api.get<Project[]>('/projects/', { params })  // 添加斜杠
  return response.data
}

// 获取项目详情
export const getProject = async (id: number): Promise<Project> => {
  const response = await api.get<Project>(`/projects/${id}/`)  // 添加斜杠
  return response.data
}

// 创建项目
export const createProject = async (projectData: ProjectCreate): Promise<Project> => {
  const formData = new FormData()
  
  formData.append('name', projectData.name)
  formData.append('description', projectData.description)
  
  if (projectData.file) {
    formData.append('file', projectData.file)
  }
  
  if (projectData.files && projectData.files.length > 0) {
    projectData.files.forEach(file => {
      formData.append('files', file)
    })
  }
  
  if (projectData.git_repo_url) {
    formData.append('git_repo_url', projectData.git_repo_url)
  }
  
  if (projectData.git_branch) {
    formData.append('git_branch', projectData.git_branch)
  }
  
  const response = await api.post<Project>('/projects/', formData, {  // 添加斜杠
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
  return response.data
}

// 更新项目
export const updateProject = async (id: number, projectData: ProjectUpdate): Promise<Project> => {
  const response = await api.put<Project>(`/projects/${id}/`, projectData)  // 添加斜杠
  return response.data
}

// 删除项目
export const deleteProject = async (id: number): Promise<Project> => {
  const response = await api.delete<Project>(`/projects/${id}/`)  // 添加斜杠
  return response.data
}

// 获取项目环境变量
export const getProjectEnvVars = async (id: number): Promise<Record<string, string>> => {
  const response = await api.get<Record<string, string>>(`/projects/${id}/env-vars/`)  // 添加斜杠
  return response.data
}

// 更新项目环境变量
export const updateProjectEnvVars = async (id: number, envVars: Record<string, string>): Promise<Project> => {
  const response = await api.put<Project>(`/projects/${id}/env-vars/`, envVars)  // 添加斜杠
  return response.data
}