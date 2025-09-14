export interface Project {
  id: number
  name: string
  description: string
  package_path: string
  created_at: string
  owner_id: number
  status: 'DEVELOPING' | 'ONLINE' | 'OFFLINE'
  version: string
  entrypoint: string
  has_requirements: boolean
  env_template: Record<string, string> | null
}

export interface ProjectCreate {
  name: string
  description: string
  file?: File
  files?: File[]
  git_repo_url?: string
  git_branch?: string
}

export interface ProjectUpdate {
  name?: string
  description?: string
  status?: 'DEVELOPING' | 'ONLINE' | 'OFFLINE'
  version?: string
  entrypoint?: string
  env_template?: Record<string, string>
}

// Git 凭证相关类型
export interface GitCredential {
  id: number
  provider: string
  username: string
  created_at: string
}

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