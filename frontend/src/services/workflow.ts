// /Users/oscar/projects/CrawlPro/frontend/src/services/workflow.ts

import request from '../utils/request'
import {
  Workflow,
  WorkflowCreate,
  WorkflowUpdate,
  WorkflowDesign,
  WorkflowListResponse
} from '../types/workflow'
import { Task } from '../types/task'

export class WorkflowService {
  // 获取工作流列表
  static async getList(params: {
    page: number
    size: number
    projectName?: string
    workflowName?: string
    status?: string
  }) {
    return request<{
      data: WorkflowListResponse
      message: string
      success: boolean
    }>({
      url: '/workflows',
      method: 'GET',
      params
    })
  }

  // 创建工作流
  static async create(data: WorkflowCreate) {
    return request<{
      data: Workflow
      message: string
      success: boolean
    }>({
      url: '/workflows',
      method: 'POST',
      data
    })
  }

  // 更新工作流
  static async update(id: number, data: WorkflowUpdate) {
    return request<{
      data: Workflow
      message: string
      success: boolean
    }>({
      url: `/workflows/${id}`,
      method: 'PUT',
      data
    })
  }

  // 删除工作流
  static async delete(id: number) {
    return request<{
      message: string
      success: boolean
    }>({
      url: `/workflows/${id}`,
      method: 'DELETE'
    })
  }

  // 获取工作流任务列表
  static async getTasks(workflowId: number) {
    return request<{
      data: Task[]
      message: string
      success: boolean
    }>({
      url: `/workflows/${workflowId}/tasks`,
      method: 'GET'
    })
  }

  // 获取工作流设计
  static async getDesign(workflowId: number) {
    return request<{
      data: WorkflowDesign
      message: string
      success: boolean
    }>({
      url: `/workflows/${workflowId}/design`,
      method: 'GET'
    })
  }

  // 保存工作流设计
  static async saveDesign(workflowId: number, data: WorkflowDesign) {
    return request<{
      message: string
      success: boolean
    }>({
      url: `/workflows/${workflowId}/design`,
      method: 'POST',
      data
    })
  }
}