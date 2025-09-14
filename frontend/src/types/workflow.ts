// /Users/oscar/projects/CrawlPro/frontend/src/types/workflow.ts

export interface Workflow {
  id: number
  name: string
  projectId: number
  projectName: string
  description: string
  status: 'enabled' | 'disabled'
  concurrent: boolean
  failureStrategy: 'stop' | 'continue'
  taskCount: number
  createdAt: string
  updatedAt: string
}

export interface WorkflowCreate {
  name: string
  projectId: number
  description?: string
  concurrent?: boolean
  failureStrategy?: 'stop' | 'continue'
}

export interface WorkflowUpdate {
  name?: string
  description?: string
  status?: 'enabled' | 'disabled'
  concurrent?: boolean
  failureStrategy?: 'stop' | 'continue'
}

export interface TaskNode {
  id: number
  name: string
  type: string
  config: any
}

export interface TaskDependency {
  id: number
  sourceId: number
  targetId: number
  condition?: string
}

export interface WorkflowDesign {
  tasks: TaskNode[]
  dependencies: TaskDependency[]
}

export interface WorkflowListResponse {
  items: Workflow[]
  total: number
  page: number
  size: number
}