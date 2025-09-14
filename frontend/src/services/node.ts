import api from './api'
import type { Node } from '@/types/node'

// 获取节点列表
export const getNodes = async (params?: {
  skip?: number
  limit?: number
}): Promise<Node[]> => {
  const response = await api.get<Node[]>('/nodes/', { params })
  return response.data
}

// 获取节点详情
export const getNode = async (id: number): Promise<Node> => {
  const response = await api.get<Node>(`/nodes/${id}/`)
  return response.data
}

// 节点心跳上报
export const nodeHeartbeat = async (data: {
  hostname: string
  ip: string
  os?: string
}): Promise<Node> => {
  const formData = new FormData()
  formData.append('hostname', data.hostname)
  formData.append('ip', data.ip)
  if (data.os) {
    formData.append('os', data.os)
  }
  
  const response = await api.post<Node>('/nodes/heartbeat/', formData)
  return response.data
}

// 标记节点离线
export const markNodeOffline = async (id: number): Promise<any> => {
  const response = await api.post<any>(`/nodes/${id}/offline/`)
  return response.data
}