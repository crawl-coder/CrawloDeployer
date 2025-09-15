// /Users/oscar/projects/CrawloDeployer/frontend/src/services/execution.ts

import request from '../utils/request'
import {
  ExecutionDetail,
  ExecutionResult,
  ExecutionMetrics,
  ExecutionListResponse
} from '../types/execution'

export class ExecutionService {
  // 获取执行记录列表
  static async getList(params: {
    page: number
    size: number
    taskName?: string
    status?: string
    startDate?: string
    endDate?: string
    sortBy?: string
    sortOrder?: string
  }) {
    // 转换参数以匹配后端API
    const backendParams: any = {
      skip: (params.page - 1) * params.size,
      limit: params.size
    };
    
    // 添加其他过滤参数
    if (params.taskName) backendParams.task_name = params.taskName;
    if (params.status) backendParams.status = params.status;
    if (params.startDate) backendParams.start_date = params.startDate;
    if (params.endDate) backendParams.end_date = params.endDate;
    
    return request<{
      data: ExecutionListResponse
      message: string
      success: boolean
    }>({
      url: '/task-runs',
      method: 'GET',
      params: backendParams
    })
  }

  // 获取执行记录详情
  static async getDetail(id: number | string) {
    return request<{
      data: ExecutionDetail
      message: string
      success: boolean
    }>({
      url: `/task-runs/${id}`,
      method: 'GET'
    })
  }

  // 获取执行日志
  static async getLogs(id: number | string) {
    return request<{
      data: { logs: string }
      message: string
      success: boolean
    }>({
      url: `/task-runs/${id}/log`,
      method: 'GET'
    })
  }

  // 获取执行结果
  static async getResults(
    executionId: number | string,
    params: {
      page: number
      size: number
      keyword?: string
    }
  ) {
    // 注意：后端可能没有直接对应的结果获取API，这里暂时保持原样
    return request<{
      data: {
        items: ExecutionResult[]
        total: number
        page: number
        size: number
      }
      message: string
      success: boolean
    }>({
      url: `/task-runs/${executionId}/results`,
      method: 'GET',
      params
    })
  }

  // 获取执行性能统计
  static async getMetrics(executionId: number | string) {
    // 注意：后端可能没有直接对应的性能统计API，这里暂时保持原样
    return request<{
      data: ExecutionMetrics
      message: string
      success: boolean
    }>({
      url: `/task-runs/${executionId}/metrics`,
      method: 'GET'
      // 后端可能没有这个端点，需要根据实际情况调整
    })
  }

  // 导出执行结果
  static async exportResults(executionId: number | string) {
    return request<{
      data: { url: string }
      message: string
      success: boolean
    }>({
      url: `/task-runs/${executionId}/export`,
      method: 'GET'
    })
  }
}