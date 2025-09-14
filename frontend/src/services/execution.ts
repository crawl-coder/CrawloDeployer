// /Users/oscar/projects/CrawlPro/frontend/src/services/execution.ts

import request from '@/utils/request'
import {
  ExecutionDetail,
  ExecutionResult,
  ExecutionMetrics,
  ExecutionListResponse
} from '@/types/execution'

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
    return request<{
      data: ExecutionListResponse
      message: string
      success: boolean
    }>({
      url: '/executions',
      method: 'GET',
      params
    })
  }

  // 获取执行记录详情
  static async getDetail(id: number | string) {
    return request<{
      data: ExecutionDetail
      message: string
      success: boolean
    }>({
      url: `/executions/${id}`,
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
      url: `/executions/${id}/logs`,
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
      url: `/executions/${executionId}/results`,
      method: 'GET',
      params
    })
  }

  // 获取执行性能统计
  static async getMetrics(executionId: number | string) {
    return request<{
      data: ExecutionMetrics
      message: string
      success: boolean
    }>({
      url: `/executions/${executionId}/metrics`,
      method: 'GET'
    })
  }

  // 导出执行结果
  static async exportResults(executionId: number | string) {
    return request<{
      data: { url: string }
      message: string
      success: boolean
    }>({
      url: `/executions/${executionId}/export`,
      method: 'POST'
    })
  }
}