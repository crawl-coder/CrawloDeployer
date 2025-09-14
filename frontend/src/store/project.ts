import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  getProjects,
  getProject,
  createProject,
  updateProject,
  deleteProject,
  getProjectEnvVars,
  updateProjectEnvVars
} from '@/services/project'
import type { Project, ProjectCreate, ProjectUpdate } from '@/types/project'

export const useProjectStore = defineStore('project', () => {
  // 状态
  const projects = ref<Project[]>([])
  const currentProject = ref<Project | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  
  // 计算属性
  const projectCount = computed(() => projects.value.length)
  
  // 获取项目列表
  const fetchProjects = async (params?: { skip?: number; limit?: number }) => {
    loading.value = true
    error.value = null
    try {
      const data = await getProjects(params)
      projects.value = data
    } catch (err: any) {
      error.value = err.message || '获取项目列表失败'
    } finally {
      loading.value = false
    }
  }
  
  // 获取项目详情
  const fetchProject = async (id: number) => {
    loading.value = true
    error.value = null
    try {
      const data = await getProject(id)
      currentProject.value = data
      return data
    } catch (err: any) {
      error.value = err.message || '获取项目详情失败'
      return null
    } finally {
      loading.value = false
    }
  }
  
  // 创建项目
  const createNewProject = async (projectData: ProjectCreate) => {
    loading.value = true
    error.value = null
    try {
      const data = await createProject(projectData)
      projects.value.push(data)
      return { success: true, data }
    } catch (err: any) {
      error.value = err.message || '创建项目失败'
      return { success: false, message: error.value }
    } finally {
      loading.value = false
    }
  }
  
  // 更新项目
  const updateExistingProject = async (id: number, projectData: ProjectUpdate) => {
    loading.value = true
    error.value = null
    try {
      const data = await updateProject(id, projectData)
      const index = projects.value.findIndex(p => p.id === id)
      if (index !== -1) {
        projects.value[index] = data
      }
      if (currentProject.value && currentProject.value.id === id) {
        currentProject.value = data
      }
      return { success: true, data }
    } catch (err: any) {
      error.value = err.message || '更新项目失败'
      return { success: false, message: error.value }
    } finally {
      loading.value = false
    }
  }
  
  // 删除项目
  const deleteExistingProject = async (id: number) => {
    loading.value = true
    error.value = null
    try {
      await deleteProject(id)
      projects.value = projects.value.filter(p => p.id !== id)
      if (currentProject.value && currentProject.value.id === id) {
        currentProject.value = null
      }
      return { success: true }
    } catch (err: any) {
      error.value = err.message || '删除项目失败'
      return { success: false, message: error.value }
    } finally {
      loading.value = false
    }
  }
  
  // 获取项目环境变量
  const fetchProjectEnvVars = async (id: number) => {
    loading.value = true
    error.value = null
    try {
      const data = await getProjectEnvVars(id)
      return { success: true, data }
    } catch (err: any) {
      error.value = err.message || '获取环境变量失败'
      return { success: false, message: error.value }
    } finally {
      loading.value = false
    }
  }
  
  // 更新项目环境变量
  const updateProjectEnvVarsAction = async (id: number, envVars: Record<string, string>) => {
    loading.value = true
    error.value = null
    try {
      const data = await updateProjectEnvVars(id, envVars)
      const index = projects.value.findIndex(p => p.id === id)
      if (index !== -1) {
        projects.value[index] = data
      }
      if (currentProject.value && currentProject.value.id === id) {
        currentProject.value = data
      }
      return { success: true, data }
    } catch (err: any) {
      error.value = err.message || '更新环境变量失败'
      return { success: false, message: error.value }
    } finally {
      loading.value = false
    }
  }
  
  // 重置状态
  const reset = () => {
    projects.value = []
    currentProject.value = null
    loading.value = false
    error.value = null
  }
  
  return {
    // 状态
    projects,
    currentProject,
    loading,
    error,
    
    // 计算属性
    projectCount,
    
    // 方法
    fetchProjects,
    fetchProject,
    createNewProject,
    updateExistingProject,
    deleteExistingProject,
    fetchProjectEnvVars,
    updateProjectEnvVarsAction,
    reset
  }
})