import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  getNodes,
  getNode,
  nodeHeartbeat,
  markNodeOffline
} from '@/services/node'
import type { Node } from '@/types/node'

export const useNodeStore = defineStore('node', () => {
  // 状态
  const nodes = ref<Node[]>([])
  const currentNode = ref<Node | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  
  // 计算属性
  const nodeCount = computed(() => nodes.value.length)
  const onlineNodes = computed(() => nodes.value.filter(node => node.status === 'ONLINE'))
  const offlineNodes = computed(() => nodes.value.filter(node => node.status === 'OFFLINE'))
  
  // 获取节点列表
  const fetchNodes = async (params?: { skip?: number; limit?: number }) => {
    loading.value = true
    error.value = null
    try {
      const data = await getNodes(params)
      nodes.value = data
    } catch (err: any) {
      error.value = err.message || '获取节点列表失败'
    } finally {
      loading.value = false
    }
  }
  
  // 获取节点详情
  const fetchNode = async (id: number) => {
    loading.value = true
    error.value = null
    try {
      const data = await getNode(id)
      currentNode.value = data
      return data
    } catch (err: any) {
      error.value = err.message || '获取节点详情失败'
      return null
    } finally {
      loading.value = false
    }
  }
  
  // 节点心跳上报
  const sendHeartbeat = async (data: { hostname: string; ip: string; os?: string }) => {
    loading.value = true
    error.value = null
    try {
      const nodeData = await nodeHeartbeat(data)
      // 更新节点列表中的节点信息
      const index = nodes.value.findIndex(n => n.id === nodeData.id)
      if (index !== -1) {
        nodes.value[index] = nodeData
      }
      return { success: true, data: nodeData }
    } catch (err: any) {
      error.value = err.message || '心跳上报失败'
      return { success: false, message: error.value }
    } finally {
      loading.value = false
    }
  }
  
  // 标记节点离线
  const markOffline = async (id: number) => {
    loading.value = true
    error.value = null
    try {
      await markNodeOffline(id)
      // 更新节点状态
      const node = nodes.value.find(n => n.id === id)
      if (node) {
        node.status = 'OFFLINE'
      }
      if (currentNode.value && currentNode.value.id === id) {
        currentNode.value.status = 'OFFLINE'
      }
      return { success: true }
    } catch (err: any) {
      error.value = err.message || '标记节点离线失败'
      return { success: false, message: error.value }
    } finally {
      loading.value = false
    }
  }
  
  // 重置状态
  const reset = () => {
    nodes.value = []
    currentNode.value = null
    loading.value = false
    error.value = null
  }
  
  return {
    // 状态
    nodes,
    currentNode,
    loading,
    error,
    
    // 计算属性
    nodeCount,
    onlineNodes,
    offlineNodes,
    
    // 方法
    fetchNodes,
    fetchNode,
    sendHeartbeat,
    markOffline,
    reset
  }
})