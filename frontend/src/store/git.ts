import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  getGitCredentials,
  createGitCredential,
  updateGitCredential,
  deleteGitCredential
} from '../services/git'
import type { GitCredential, GitCredentialCreate, GitCredentialUpdate } from '../types/project'

export const useGitStore = defineStore('git', () => {
  // 状态
  const credentials = ref<GitCredential[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  
  // 获取Git凭证列表
  const fetchCredentials = async () => {
    loading.value = true
    error.value = null
    try {
      const data = await getGitCredentials()
      credentials.value = data
      return { success: true, data }
    } catch (err: any) {
      error.value = err.message || '获取Git凭证列表失败'
      return { success: false, message: error.value }
    } finally {
      loading.value = false
    }
  }
  
  // 创建Git凭证
  const createCredential = async (credentialData: GitCredentialCreate) => {
    loading.value = true
    error.value = null
    try {
      const data = await createGitCredential(credentialData)
      credentials.value.push(data)
      return { success: true, data }
    } catch (err: any) {
      error.value = err.message || '创建Git凭证失败'
      return { success: false, message: error.value }
    } finally {
      loading.value = false
    }
  }
  
  // 更新Git凭证
  const updateCredential = async (id: number, credentialData: GitCredentialUpdate) => {
    loading.value = true
    error.value = null
    try {
      const data = await updateGitCredential(id, credentialData)
      const index = credentials.value.findIndex(c => c.id === id)
      if (index !== -1) {
        credentials.value[index] = data
      }
      return { success: true, data }
    } catch (err: any) {
      error.value = err.message || '更新Git凭证失败'
      return { success: false, message: error.value }
    } finally {
      loading.value = false
    }
  }
  
  // 删除Git凭证
  const deleteCredential = async (id: number) => {
    loading.value = true
    error.value = null
    try {
      await deleteGitCredential(id)
      credentials.value = credentials.value.filter(c => c.id !== id)
      return { success: true }
    } catch (err: any) {
      error.value = err.message || '删除Git凭证失败'
      return { success: false, message: error.value }
    } finally {
      loading.value = false
    }
  }
  
  // 重置状态
  const reset = () => {
    credentials.value = []
    loading.value = false
    error.value = null
  }
  
  return {
    // 状态
    credentials,
    loading,
    error,
    
    // 方法
    fetchCredentials,
    createCredential,
    updateCredential,
    deleteCredential,
    reset
  }
})