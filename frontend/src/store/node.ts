import { defineStore } from 'pinia'
import { nodeService } from '@/services/node'
import type { Node } from '@/types/node'
import { ElMessage } from 'element-plus'

interface NodeState {
  nodes: Node[]
  loading: boolean
  error: string | null
}

export const useNodeStore = defineStore('node', {
  state: (): NodeState => ({
    nodes: [],
    loading: false,
    error: null
  }),

  getters: {
    onlineNodes: (state) => state.nodes.filter(node => node.status === 'ONLINE'),
    offlineNodes: (state) => state.nodes.filter(node => node.status === 'OFFLINE')
  },

  actions: {
    async fetchNodes() {
      this.loading = true
      this.error = null
      try {
        const response = await nodeService.getNodes()
        if (response.success) {
          this.nodes = response.data || []
        } else {
          this.error = response.message || '获取节点列表失败'
          ElMessage.error(this.error)
        }
      } catch (error) {
        this.error = '网络错误'
        ElMessage.error('获取节点列表失败')
      } finally {
        this.loading = false
      }
    },

    async fetchNodeById(id: number) {
      this.loading = true
      this.error = null
      try {
        const response = await nodeService.getNodeById(id)
        if (response.success) {
          const index = this.nodes.findIndex(node => node.id === id)
          if (index !== -1) {
            this.nodes[index] = response.data
          } else {
            this.nodes.push(response.data)
          }
          return response.data
        } else {
          this.error = response.message || '获取节点信息失败'
          ElMessage.error(this.error)
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

    async refreshNodeStatus(id: number) {
      this.loading = true
      this.error = null
      try {
        const response = await nodeService.markNodeOffline(id)
        if (response.success) {
          const index = this.nodes.findIndex(node => node.id === id)
          if (index !== -1) {
            this.nodes[index].status = 'OFFLINE'
          }
          ElMessage.success('节点状态已刷新')
        } else {
          this.error = response.message || '刷新节点状态失败'
          ElMessage.error(this.error)
        }
      } catch (error) {
        this.error = '网络错误'
        ElMessage.error('刷新节点状态失败')
      } finally {
        this.loading = false
      }
    }
  }
})