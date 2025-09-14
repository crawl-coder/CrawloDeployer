// /Users/oscar/projects/CrawlPro/frontend/src/types/env.ts

export interface EnvVariable {
  id: number
  projectId: number
  projectName: string
  name: string
  value: string
  isSecret: boolean
  description: string
  createdAt: string
  updatedAt: string
}

export interface EnvVariableCreate {
  projectId: number
  name: string
  value: string
  isSecret: boolean
  description?: string
}

export interface EnvVariableUpdate {
  projectId?: number
  name?: string
  value?: string
  isSecret?: boolean
  description?: string
}

export interface EnvListResponse {
  items: EnvVariable[]
  total: number
  page: number
  size: number
}