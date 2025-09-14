// /Users/oscar/projects/CrawlPro/frontend/src/services/statistics.ts

import request from '@/utils/request'

export class StatisticsService {
  // 获取任务统计汇总
  static async getSummary() {
    return request({
      url: '/statistics/summary',
      method: 'GET'
    })
  }

  // 获取任务执行趋势
  static async getTrend(params: {
    startDate: string
    endDate: string
  }) {
    return request({
      url: '/statistics/trend',
      method: 'GET',
      params
    })
  }

  // 获取任务状态分布
  static async getStatusDistribution() {
    return request({
      url: '/statistics/status-distribution',
      method: 'GET'
    })
  }

  // 获取项目任务分布
  static async getProjectDistribution() {
    return request({
      url: '/statistics/project-distribution',
      method: 'GET'
    })
  }

  // 获取最近执行记录
  static async getRecentExecutions(params: {
    limit: number
  }) {
    return request({
      url: '/statistics/recent-executions',
      method: 'GET',
      params
    })
  }
}