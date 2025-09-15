import api from './api'
import type { Node, NodeCreate, NodeUpdate } from '../types/node'
import type { ApiResponse } from '../types/api'

// 获取节点列表
export const getNodes = async (params?: {
  skip?: number
  limit?: number
}): Promise<ApiResponse<Node[]>> => {
  const response = await api.get<ApiResponse<Node[]>>('/nodes', { params })
  return response.data
}

// 获取节点详情
export const getNodeById = async (id: number): Promise<ApiResponse<Node>> => {
  const response = await api.get<ApiResponse<Node>>(`/nodes/${id}`)
  return response.data
}

// 创建节点
export const createNode = async (nodeData: NodeCreate): Promise<ApiResponse<Node>> => {
  const response = await api.post<ApiResponse<Node>>('/nodes', nodeData)
  return response.data
}

// 更新节点
export const updateNode = async (id: number, nodeData: NodeUpdate): Promise<ApiResponse<Node>> => {
  const response = await api.put<ApiResponse<Node>>(`/nodes/${id}`, nodeData)
  return response.data
}

// 删除节点
export const deleteNode = async (id: number): Promise<ApiResponse<any>> => {
  const response = await api.delete<ApiResponse<any>>(`/nodes/${id}`)
  return response.data
}

// 获取物理主机列表
export const getPhysicalHosts = async (): Promise<ApiResponse<any[]>> => {
  const response = await api.get<ApiResponse<any[]>>('/nodes/physical-hosts')
  return response.data
}

// 检查资源是否足够
export const checkResources = async (data: {
  physical_host_name: string
  required_cpu_cores?: number
  required_memory_gb?: number
  required_disk_gb?: number
}): Promise<ApiResponse<any>> => {
  const response = await api.post<ApiResponse<any>>('/nodes/check-resources', data)
  return response.data
}

// 节点心跳上报
export const nodeHeartbeat = async (data: {
  hostname: string
  ip: string
  os?: string
  physical_host_id?: string
  physical_host_name?: string
  container_id?: string
  instance_name?: string
}): Promise<ApiResponse<Node>> => {
  const formData = new FormData()
  formData.append('hostname', data.hostname)
  formData.append('ip', data.ip)
  if (data.os) {
    formData.append('os', data.os)
  }
  if (data.physical_host_id) {
    formData.append('physical_host_id', data.physical_host_id)
  }
  if (data.physical_host_name) {
    formData.append('physical_host_name', data.physical_host_name)
  }
  if (data.container_id) {
    formData.append('container_id', data.container_id)
  }
  if (data.instance_name) {
    formData.append('instance_name', data.instance_name)
  }
  
  // 修复API路径，移除末尾的斜杠
  const response = await api.post<ApiResponse<Node>>('/nodes/heartbeat', formData)
  return response.data
}

// 标记节点离线
export const markNodeOffline = async (id: number): Promise<ApiResponse<any>> => {
  // 修复API路径，移除末尾的斜杠
  const response = await api.post<ApiResponse<any>>(`/nodes/${id}/offline`)
  return response.data
}
