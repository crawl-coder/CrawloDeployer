import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  getTasks,
  getTask,
  createTask,
  updateTask,
  deleteTask,
  toggleTask,
  runTask,
  getTaskStats,
  getTasksOverviewStats,
  addTaskDependencies,
  getTaskDependencies,
  clearTaskDependencies
} from '../services/task'
import type { Task, TaskCreate, TaskUpdate } from '../types/task'

export const useTaskStore = defineStore('task', () => {
  // 状态
  const tasks = ref<Task[]>([])
  const currentTask = ref<Task | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  
  // 计算属性
  const taskCount = computed(() => tasks.value.length)
  
  // 获取任务列表
  const fetchTasks = async (params?: { skip?: number; limit?: number }) => {
    loading.value = true
    error.value = null
    try {
      const response = await getTasks(params)
      if (response.success) {
        tasks.value = response.data || []
      } else {
        error.value = response.message || '获取任务列表失败'
      }
    } catch (err: any) {
      error.value = err.message || '获取任务列表失败'
    } finally {
      loading.value = false
    }
  }
  
  // 获取任务详情
  const fetchTask = async (id: number) => {
    loading.value = true
    error.value = null
    try {
      const response = await getTask(id)
      if (response.success) {
        currentTask.value = response.data || null
        return response.data
      } else {
        error.value = response.message || '获取任务详情失败'
        return null
      }
    } catch (err: any) {
      error.value = err.message || '获取任务详情失败'
      return null
    } finally {
      loading.value = false
    }
  }
  
  // 创建任务
  const createNewTask = async (taskData: TaskCreate) => {
    loading.value = true
    error.value = null
    try {
      const response = await createTask(taskData)
      if (response.success && response.data) {
        tasks.value.push(response.data)
        return { success: true, data: response.data }
      } else {
        error.value = response.message || '创建任务失败'
        return { success: false, message: error.value }
      }
    } catch (err: any) {
      error.value = err.message || '创建任务失败'
      return { success: false, message: error.value }
    } finally {
      loading.value = false
    }
  }
  
  // 更新任务
  const updateExistingTask = async (id: number, taskData: TaskUpdate) => {
    loading.value = true
    error.value = null
    try {
      const response = await updateTask(id, taskData)
      if (response.success && response.data) {
        const index = tasks.value.findIndex(t => t.id === id)
        if (index !== -1) {
          tasks.value[index] = response.data
        }
        if (currentTask.value && currentTask.value.id === id) {
          currentTask.value = response.data
        }
        return { success: true, data: response.data }
      } else {
        error.value = response.message || '更新任务失败'
        return { success: false, message: error.value }
      }
    } catch (err: any) {
      error.value = err.message || '更新任务失败'
      return { success: false, message: error.value }
    } finally {
      loading.value = false
    }
  }
  
  // 删除任务
  const deleteExistingTask = async (id: number) => {
    loading.value = true
    error.value = null
    try {
      const response = await deleteTask(id)
      if (response.success) {
        tasks.value = tasks.value.filter(t => t.id !== id)
        if (currentTask.value && currentTask.value.id === id) {
          currentTask.value = null
        }
        return { success: true }
      } else {
        error.value = response.message || '删除任务失败'
        return { success: false, message: error.value }
      }
    } catch (err: any) {
      error.value = err.message || '删除任务失败'
      return { success: false, message: error.value }
    } finally {
      loading.value = false
    }
  }
  
  // 启用/禁用任务
  const toggleTaskStatus = async (id: number, enable: boolean) => {
    loading.value = true
    error.value = null
    try {
      const response = await toggleTask(id, enable)
      if (response.success && response.data) {
        const index = tasks.value.findIndex(t => t.id === id)
        if (index !== -1) {
          tasks.value[index] = response.data
        }
        if (currentTask.value && currentTask.value.id === id) {
          currentTask.value = response.data
        }
        return { success: true, data: response.data }
      } else {
        error.value = response.message || '切换任务状态失败'
        return { success: false, message: error.value }
      }
    } catch (err: any) {
      error.value = err.message || '切换任务状态失败'
      return { success: false, message: error.value }
    } finally {
      loading.value = false
    }
  }
  
  // 立即执行任务
  const runTaskNow = async (id: number) => {
    loading.value = true
    error.value = null
    try {
      const response = await runTask(id)
      if (response.success) {
        return { success: true, data: response.data }
      } else {
        error.value = response.message || '执行任务失败'
        return { success: false, message: error.value }
      }
    } catch (err: any) {
      error.value = err.message || '执行任务失败'
      return { success: false, message: error.value }
    } finally {
      loading.value = false
    }
  }
  
  // 获取任务统计
  const fetchTaskStats = async (id: number) => {
    loading.value = true
    error.value = null
    try {
      const response = await getTaskStats(id)
      if (response.success) {
        return { success: true, data: response.data }
      } else {
        error.value = response.message || '获取任务统计失败'
        return { success: false, message: error.value }
      }
    } catch (err: any) {
      error.value = err.message || '获取任务统计失败'
      return { success: false, message: error.value }
    } finally {
      loading.value = false
    }
  }
  
  // 获取任务概览统计
  const fetchTasksOverviewStats = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await getTasksOverviewStats()
      if (response.success) {
        return { success: true, data: response.data }
      } else {
        error.value = response.message || '获取任务概览统计失败'
        return { success: false, message: error.value }
      }
    } catch (err: any) {
      error.value = err.message || '获取任务概览统计失败'
      return { success: false, message: error.value }
    } finally {
      loading.value = false
    }
  }
  
  // 添加任务依赖
  const addDependencies = async (id: number, dependencyIds: number[]) => {
    loading.value = true
    error.value = null
    try {
      const response = await addTaskDependencies(id, dependencyIds)
      if (response.success && response.data) {
        const index = tasks.value.findIndex(t => t.id === id)
        if (index !== -1) {
          tasks.value[index] = response.data
        }
        if (currentTask.value && currentTask.value.id === id) {
          currentTask.value = response.data
        }
        return { success: true, data: response.data }
      } else {
        error.value = response.message || '添加任务依赖失败'
        return { success: false, message: error.value }
      }
    } catch (err: any) {
      error.value = err.message || '添加任务依赖失败'
      return { success: false, message: error.value }
    } finally {
      loading.value = false
    }
  }
  
  // 获取任务依赖
  const fetchDependencies = async (id: number) => {
    loading.value = true
    error.value = null
    try {
      const response = await getTaskDependencies(id)
      if (response.success) {
        return { success: true, data: response.data }
      } else {
        error.value = response.message || '获取任务依赖失败'
        return { success: false, message: error.value }
      }
    } catch (err: any) {
      error.value = err.message || '获取任务依赖失败'
      return { success: false, message: error.value }
    } finally {
      loading.value = false
    }
  }
  
  // 清除任务依赖
  const clearDependencies = async (id: number) => {
    loading.value = true
    error.value = null
    try {
      const response = await clearTaskDependencies(id)
      if (response.success && response.data) {
        const index = tasks.value.findIndex(t => t.id === id)
        if (index !== -1) {
          tasks.value[index] = response.data
        }
        if (currentTask.value && currentTask.value.id === id) {
          currentTask.value = response.data
        }
        return { success: true, data: response.data }
      } else {
        error.value = response.message || '清除任务依赖失败'
        return { success: false, message: error.value }
      }
    } catch (err: any) {
      error.value = err.message || '清除任务依赖失败'
      return { success: false, message: error.value }
    } finally {
      loading.value = false
    }
  }
  
  // 重置状态
  const reset = () => {
    tasks.value = []
    currentTask.value = null
    loading.value = false
    error.value = null
  }
  
  return {
    // 状态
    tasks,
    currentTask,
    loading,
    error,
    
    // 计算属性
    taskCount,
    
    // 方法
    fetchTasks,
    fetchTask,
    createNewTask,
    updateExistingTask,
    deleteExistingTask,
    toggleTaskStatus,
    runTaskNow,
    fetchTaskStats,
    fetchTasksOverviewStats,
    addDependencies,
    fetchDependencies,
    clearDependencies,
    reset
  }
})