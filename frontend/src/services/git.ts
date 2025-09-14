import api from './api'

// Git凭证相关类型
export interface GitCredentialCreate {
  provider: string
  username: string
  token: string
}

export interface GitCredentialUpdate {
  provider?: string
  username?: string
  token?: string
}

export interface GitCredentialOut {
  id: number
  provider: string
  username: string
  created_at: string
}

// 获取Git凭证列表
export const getGitCredentials = async (): Promise<GitCredentialOut[]> => {
  const response = await api.get<GitCredentialOut[]>('/git-credentials/')
  return response.data
}

// 创建Git凭证
export const createGitCredential = async (credentialData: GitCredentialCreate): Promise<GitCredentialOut> => {
  const response = await api.post<GitCredentialOut>('/git-credentials/', credentialData)
  return response.data
}

// 更新Git凭证
export const updateGitCredential = async (id: number, credentialData: GitCredentialUpdate): Promise<GitCredentialOut> => {
  const response = await api.put<GitCredentialOut>(`/git-credentials/${id}/`, credentialData)
  return response.data
}

// 删除Git凭证
export const deleteGitCredential = async (id: number): Promise<void> => {
  await api.delete(`/git-credentials/${id}/`)
}