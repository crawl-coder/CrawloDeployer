export interface LoginRequest {
  username: string
  password: string
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

export interface User {
  id: number
  username: string
  email: string
  is_active: boolean
  is_superuser: boolean
  created_at: string
  full_name?: string
  phone?: string
  bio?: string
  avatar?: string
  updated_at?: string
}

export interface UserStats {
  projects: number
  tasks: number
  executions: number
}

export interface UserUpdate {
  email?: string
  full_name?: string
  phone?: string
  bio?: string
}

export interface PasswordUpdate {
  current_password: string
  new_password: string
}