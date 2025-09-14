// /Users/oscar/projects/CrawlPro/frontend/src/types/execution.ts

export interface Execution {
  id: number
  taskId: number
  taskName: string
  projectId: number
  projectName: string
  nodeId: number
  nodeName: string
  status: 'running' | 'success' | 'failed'
  startTime: string
  endTime: string
  duration: string
  resultCount: number
  errorMessage?: string
  creator: string
  createdAt: string
}

export interface ExecutionDetail extends Execution {
  logs?: string
  resultData?: any[]
}

export interface ExecutionResult {
  id: number
  executionId: number
  title: string
  url: string
  summary: string
  createdAt: string
}

export interface ExecutionMetrics {
  requests: number
  successRate: number
  avgResponseTime: number
  dataSize: string
  timeline?: Array<{
    time: string
    responseTime: number
  }>
}

export interface ExecutionListResponse {
  items: Execution[]
  total: number
  page: number
  size: number
}