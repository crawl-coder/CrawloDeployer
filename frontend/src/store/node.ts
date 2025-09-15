import { defineStore } from 'pinia'
import { 
  getNodes,
  getNodeById,
  createNode,
  updateNode,
  deleteNode,
  nodeHeartbeat,
  markNodeOffline,
  getPhysicalHosts,
  checkResources
} from '../services/node'
import type { Node, NodeCreate, NodeUpdate } from '../types/node'
import type { ApiResponse } from '../types/api'
import { ElMessage } from 'element-plus'

interface NodeState {
  nodes: Node[]
  currentNode: Node | null
  nodeCount: number
  loading: boolean
  error: string | null
}

export const useNodeStore = defineStore('node', {
  state: (): NodeState => ({
    nodes: [],
    currentNode: null,
    nodeCount: 0,
    loading: false,
    error: null
  }),

  getters: {
    onlineNodes: (state) => state.nodes.filter(node => node.status === 'ONLINE'),
    offlineNodes: (state) => state.nodes.filter(node => node.status === 'OFFLINE')
  },

  actions: {
    async fetchNodes(params?: { skip?: number; limit?: number }) {
      this.loading = true
      this.error = null
      try {
        const response = await getNodes(params)
        if (response.success) {
          this.nodes = response.data || []
          this.nodeCount = response.total || this.nodes.length
        } else {
          this.error = response.message || '获取节点列表失败'
          ElMessage.error(this.error || '获取节点列表失败')
        }
      } catch (error) {
        this.error = '网络错误'
        ElMessage.error('获取节点列表失败')
      } finally {
        this.loading = false
      }
    },

    async fetchNode(id: number) {
      this.loading = true
      this.error = null
      try {
        const response = await getNodeById(id)
        if (response.success && response.data) {
          this.currentNode = response.data
          const index = this.nodes.findIndex(node => node.id === id)
          if (index !== -1) {
            this.nodes[index] = response.data
          } else {
            this.nodes.push(response.data)
          }
          return response.data
        } else {
          this.error = response.message || '获取节点信息失败'
          ElMessage.error(this.error || '获取节点信息失败')
          return null
        }
      } catch (error) {
        this.error = '网络错误'
        ElMessage.error('获取节点信息失败')
        return null
      } finally {
        this.loading = false
      }
    },

    // 创建新节点
    async createNewNode(nodeData: NodeCreate) {
      try {
        const response = await createNode(nodeData)
        if (response.success) {
          // 添加成功后刷新节点列表
          await this.fetchNodes()
          ElMessage.success('节点创建成功')
        } else {
          ElMessage.error(response.message || '节点创建失败')
        }
        return response
      } catch (error: any) {
        console.error('创建节点失败:', error)
        ElMessage.error(error.message || '创建节点失败')
        return { success: false, message: error.message || '创建节点失败' } as ApiResponse<Node>
      }
    },

    async updateExistingNode(id: number, nodeData: NodeUpdate) {
      this.loading = true
      this.error = null
      try {
        const response = await updateNode(id, nodeData)
        if (response.success && response.data) {
          const index = this.nodes.findIndex(node => node.id === id)
          if (index !== -1) {
            this.nodes[index] = response.data
          }
          if (this.currentNode && this.currentNode.id === id) {
            this.currentNode = response.data
          }
          ElMessage.success('节点更新成功')
          return { success: true, data: response.data }
        } else {
          this.error = response.message || '更新节点失败'
          ElMessage.error(this.error || '更新节点失败')
          return { success: false, message: this.error }
        }
      } catch (error) {
        this.error = '网络错误'
        ElMessage.error('更新节点失败')
        return { success: false, message: '网络错误' }
      } finally {
        this.loading = false
      }
    },

    async deleteExistingNode(id: number) {
      this.loading = true
      this.error = null
      try {
        const response = await deleteNode(id)
        if (response.success) {
          this.nodes = this.nodes.filter(node => node.id !== id)
          this.nodeCount--
          if (this.currentNode && this.currentNode.id === id) {
            this.currentNode = null
          }
          ElMessage.success('节点删除成功')
          return { success: true }
        } else {
          this.error = response.message || '删除节点失败'
          ElMessage.error(this.error || '删除节点失败')
          return { success: false, message: this.error }
        }
      } catch (error) {
        this.error = '网络错误'
        ElMessage.error('删除节点失败')
        return { success: false, message: '网络错误' }
      } finally {
        this.loading = false
      }
    },

    async markOffline(id: number) {
      this.loading = true
      this.error = null
      try {
        const response = await markNodeOffline(id)
        if (response.success) {
          const index = this.nodes.findIndex(node => node.id === id)
          if (index !== -1) {
            this.nodes[index].status = 'OFFLINE'
          }
          ElMessage.success('节点状态已刷新')
          return response
        } else {
          this.error = response.message || '刷新节点状态失败'
          ElMessage.error(this.error || '刷新节点状态失败')
          return response
        }
      } catch (error) {
        this.error = '网络错误'
        ElMessage.error('刷新节点状态失败')
        return { success: false, message: '网络错误' }
      } finally {
        this.loading = false
      }
    },
    
    // 添加节点心跳功能
    async sendHeartbeat(data: { hostname: string; ip: string; os?: string, physical_host_id?: string, physical_host_name?: string, container_id?: string, instance_name?: string }) {
      this.loading = true
      this.error = null
      try {
        const response = await nodeHeartbeat(data)
        if (response.success && response.data) {
          // 更新或添加节点到列表
          const index = this.nodes.findIndex(node => node.id === response.data!.id)
          if (index !== -1) {
            this.nodes[index] = response.data!
          } else {
            this.nodes.push(response.data!)
          }
          ElMessage.success('心跳上报成功')
          return response
        } else {
          this.error = response.message || '心跳上报失败'
          ElMessage.error(this.error || '心跳上报失败')
          return response
        }
      } catch (error) {
        this.error = '网络错误'
        ElMessage.error('心跳上报失败')
        return { success: false, message: '网络错误' }
      } finally {
        this.loading = false
      }
    },
    
    async fetchPhysicalHosts() {
      this.loading = true
      this.error = null
      try {
        const response = await getPhysicalHosts()
        if (response.success) {
          return { success: true, data: response.data }
        } else {
          this.error = response.message || '获取物理主机列表失败'
          ElMessage.error(this.error || '获取物理主机列表失败')
          return { success: false, message: this.error }
        }
      } catch (error) {
        this.error = '网络错误'
        ElMessage.error('获取物理主机列表失败')
        return { success: false, message: '网络错误' }
      } finally {
        this.loading = false
      }
    },
    
    async checkNodeResources(data: {
      physical_host_name: string
      required_cpu_cores?: number
      required_memory_gb?: number
      required_disk_gb?: number
    }) {
      this.loading = true
      this.error = null
      try {
        const response = await checkResources(data)
        if (response.success) {
          return { success: true, data: response.data }
        } else {
          this.error = response.message || '资源检查失败'
          ElMessage.error(this.error || '资源检查失败')
          return { success: false, message: this.error }
        }
      } catch (error) {
        this.error = '网络错误'
        ElMessage.error('资源检查失败')
        return { success: false, message: '网络错误' }
      } finally {
        this.loading = false
      }
    },
    
  }
})