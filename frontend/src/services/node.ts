import api from './api'
import type { Node } from '@/types/node'
import type { ApiResponse } from '@/types/api'

// 获取节点列表
export const getNodes = async (params?: {
  skip?: number
  limit?: number
}): Promise<ApiResponse<Node[]>> => {
  const response = await api.get<ApiResponse<Node[]>>('/nodes/', { params })
  return response.data
}

// 获取节点详情
export const getNodeById = async (id: number): Promise<ApiResponse<Node>> => {
  const response = await api.get<ApiResponse<Node>>(`/nodes/${id}/`)
  return response.data
}

// 节点心跳上报
export const nodeHeartbeat = async (data: {
  hostname: string
  ip: string
  os?: string
}): Promise<ApiResponse<Node>> => {
  const formData = new FormData()
  formData.append('hostname', data.hostname)
  formData.append('ip', data.ip)
  if (data.os) {
    formData.append('os', data.os)
  }
  
  const response = await api.post<ApiResponse<Node>>('/nodes/heartbeat/', formData)
  return response.data
}

// 标记节点离线
export const markNodeOffline = async (id: number): Promise<ApiResponse<any>> => {
  const response = await api.post<ApiResponse<any>>(`/nodes/${id}/offline/`)
  return response.data
}