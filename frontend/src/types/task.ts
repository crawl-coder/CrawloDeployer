export interface Task {
  id: number
  name: string
  project_id: number
  spider_name: string
  cron_expression: string | null
  args: Record<string, any> | null
  is_enabled: boolean
  created_at: string
  priority: 'LOW' | 'MEDIUM' | 'HIGH'
  timeout_seconds: number | null
  max_retries: number
  notify_on_failure: boolean
  notify_on_success: boolean
  notification_emails: string[] | null
  last_run_status: 'PENDING' | 'RUNNING' | 'SUCCESS' | 'FAILURE' | null
  last_run_time: string | null
  dependency_task_ids: number[] | null
}

export interface TaskCreate {
  name: string
  project_id: number
  spider_name: string
  cron_expression?: string
  args?: Record<string, any>
  priority?: 'LOW' | 'MEDIUM' | 'HIGH'
  timeout_seconds?: number
  max_retries?: number
  notify_on_failure?: boolean
  notify_on_success?: boolean
  notification_emails?: string[]
}

export interface TaskUpdate {
  name?: string
  project_id?: number
  spider_name?: string
  cron_expression?: string | null
  args?: Record<string, any> | null
  is_enabled?: boolean
  priority?: 'LOW' | 'MEDIUM' | 'HIGH'
  timeout_seconds?: number | null
  max_retries?: number
  notify_on_failure?: boolean
  notify_on_success?: boolean
  notification_emails?: string[] | null
  dependency_task_ids?: number[] | null
}

export interface TaskRun {
  id: number
  task_id: number
  celery_task_id: string
  status: 'PENDING' | 'RUNNING' | 'SUCCESS' | 'FAILURE'
  start_time: string | null
  end_time: string | null
  log_output: string | null
  worker_node: string | null
  exit_code: number | null
  cpu_usage: number | null
  memory_usage_mb: number | null
  duration_seconds: number | null
  items_scraped: number | null
  requests_count: number | null
  result_size_mb: number | null
  manually_stopped: boolean
  node_id: number | null
}