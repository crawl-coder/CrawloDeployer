import { defineStore } from 'pinia'
import {
  getProjects,
  getProjectById,
  createProject,
  updateProject,
  deleteProject,
  syncProjectToNodes,
  getProjectFiles,
  getProjectStats
} from '@/services/project'
import type { Project, ProjectCreate, ProjectUpdate } from '@/types/project'
import { ElMessage } from 'element-plus'

interface ProjectState {
  projects: Project[]
  projectCount: number
  loading: boolean
  error: string | null
}

export const useProjectStore = defineStore('project', {
  state: (): ProjectState => ({
    projects: [],
    projectCount: 0,
    loading: false,
    error: null
  }),

  getters: {
    projectList: (state) => state.projects
  },

  actions: {
    async fetchProjects(params?: { skip?: number; limit?: number }) {
      this.loading = true
      this.error = null
      try {
        const response = await getProjects(params)
        if (response.success) {
          this.projects = response.data || []
          this.projectCount = response.total || this.projects.length
        } else {
          this.error = response.message || '获取项目列表失败'
          ElMessage.error(this.error)
        }
      } catch (error) {
        this.error = '网络错误'
        ElMessage.error('获取项目列表失败')
      } finally {
        this.loading = false
      }
    },

    async fetchProjectById(id: number) {
      this.loading = true
      this.error = null
      try {
        const response = await getProjectById(id)
        if (response.success) {
          const index = this.projects.findIndex(project => project.id === id)
          if (index !== -1) {
            this.projects[index] = response.data
          } else {
            this.projects.push(response.data)
          }
          return response
        } else {
          this.error = response.message || '获取项目详情失败'
          ElMessage.error(this.error)
          return response
        }
      } catch (error) {
        this.error = '网络错误'
        ElMessage.error('获取项目详情失败')
        return { success: false, message: '网络错误' }
      } finally {
        this.loading = false
      }
    },

    async createNewProject(projectData: ProjectCreate) {
      this.loading = true
      this.error = null
      try {
        // 创建FormData对象
        const formData = new FormData()
        
        // 添加基本字段
        formData.append('name', projectData.name)
        formData.append('description', projectData.description || '')
        
        // 根据部署方式添加相应字段
        if (projectData.git_repo_url) {
          // Git部署方式
          formData.append('deploy_method', 'git')
          formData.append('git_url', projectData.git_repo_url)
          formData.append('git_branch', projectData.git_branch || 'main')
          
          if (projectData.ssh_key) {
            // SSH密钥认证
            formData.append('ssh_key', projectData.ssh_key)
            if (projectData.ssh_key_fingerprint) {
              formData.append('ssh_key_fingerprint', projectData.ssh_key_fingerprint)
            }
          }
        } else if (projectData.files && projectData.files.length > 0) {
          // 文件上传方式
          formData.append('deploy_method', 'upload')
          
          // 添加所有文件
          projectData.files.forEach((file, index) => {
            formData.append('files', file)
          })
        } else {
          // 默认ZIP方式
          formData.append('deploy_method', 'zip')
          if (projectData.file) {
            formData.append('files', projectData.file)
          }
        }
        
        const response = await createProject(formData)
        if (response.success) {
          this.projects.push(response.data)
          this.projectCount++
          ElMessage.success('创建成功')
        } else {
          this.error = response.message || '创建失败'
          ElMessage.error(this.error)
        }
        return response
      } catch (error) {
        this.error = '网络错误'
        ElMessage.error('创建失败')
        return { success: false, message: '网络错误' }
      } finally {
        this.loading = false
      }
    },

    async updateExistingProject(id: number, project: ProjectUpdate) {
      this.loading = true
      this.error = null
      try {
        const response = await updateProject(id, project)
        if (response.success) {
          const index = this.projects.findIndex(p => p.id === id)
          if (index !== -1) {
            this.projects[index] = response.data
          }
          ElMessage.success('更新成功')
        } else {
          this.error = response.message || '更新失败'
          ElMessage.error(this.error)
        }
        return response
      } catch (error) {
        this.error = '网络错误'
        ElMessage.error('更新失败')
        return { success: false, message: '网络错误' }
      } finally {
        this.loading = false
      }
    },

    async deleteExistingProject(id: number) {
      this.loading = true
      this.error = null
      try {
        const response = await deleteProject(id)
        if (response.success) {
          this.projects = this.projects.filter(project => project.id !== id)
          this.projectCount--
          ElMessage.success('删除成功')
        } else {
          this.error = response.message || '删除失败'
          ElMessage.error(this.error)
        }
        return response
      } catch (error) {
        this.error = '网络错误'
        ElMessage.error('删除失败')
        return { success: false, message: '网络错误' }
      } finally {
        this.loading = false
      }
    },

    async syncProjectToNodes(id: number, nodeHostnames: string[]) {
      this.loading = true
      this.error = null
      try {
        const response = await syncProjectToNodes(id, nodeHostnames)
        if (response.success) {
          ElMessage.success('项目同步成功')
        } else {
          this.error = response.message || '项目同步失败'
          ElMessage.error(this.error)
        }
        return response
      } catch (error) {
        this.error = '网络错误'
        ElMessage.error('项目同步失败')
        return { success: false, message: '网络错误' }
      } finally {
        this.loading = false
      }
    },

    async getProjectFiles(id: number) {
      this.loading = true
      this.error = null
      try {
        const response = await getProjectFiles(id)
        if (!response.success) {
          this.error = response.message || '获取项目文件失败'
          ElMessage.error(this.error)
        }
        return response
      } catch (error) {
        this.error = '网络错误'
        ElMessage.error('获取项目文件失败')
        return { success: false, message: '网络错误' }
      } finally {
        this.loading = false
      }
    },

    async getProjectStats(id: number) {
      this.loading = true
      this.error = null
      try {
        const response = await getProjectStats(id)
        if (!response.success) {
          this.error = response.message || '获取项目统计失败'
          ElMessage.error(this.error)
        }
        return response
      } catch (error) {
        this.error = '网络错误'
        ElMessage.error('获取项目统计失败')
        return { success: false, message: '网络错误' }
      } finally {
        this.loading = false
      }
    }
  }
})