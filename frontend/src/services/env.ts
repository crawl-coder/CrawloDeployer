// /Users/oscar/projects/CrawlPro/frontend/src/services/env.ts

import request from '../utils/request'
import {
  EnvVariable,
  EnvVariableCreate,
  EnvVariableUpdate,
  EnvListResponse
} from '../types/env'

export class EnvService {
  // 获取环境变量列表
  static async getList(params: {
    page: number
    size: number
    projectName?: string
    envName?: string
  }) {
    return request<{
      data: EnvListResponse
      message: string
      success: boolean
    }>({
      url: '/env-variables',
      method: 'GET',
      params
    })
  }

  // 创建环境变量
  static async create(data: EnvVariableCreate) {
    return request<{
      data: EnvVariable
      message: string
      success: boolean
    }>({
      url: '/env-variables',
      method: 'POST',
      data
    })
  }

  // 更新环境变量
  static async update(id: number, data: EnvVariableUpdate) {
    return request<{
      data: EnvVariable
      message: string
      success: boolean
    }>({
      url: `/env-variables/${id}`,
      method: 'PUT',
      data
    })
  }

  // 删除环境变量
  static async delete(id: number) {
    return request<{
      message: string
      success: boolean
    }>({
      url: `/env-variables/${id}`,
      method: 'DELETE'
    })
  }
}