export interface Node {
  id: number
  hostname: string
  ip_address: string | null
  status: 'ONLINE' | 'OFFLINE'
  last_heartbeat: string | null
  registered_at: string
  os: 'WINDOWS' | 'LINUX' | 'MACOS' | 'UNKNOWN'
  os_version: string | null
  cpu_cores: number | null
  cpu_usage: number | null
  memory_gb: number | null
  memory_usage: number | null
  disk_gb: number | null
  disk_usage: number | null
  version: string | null
  python_version: string | null
  tags: string | null
  capabilities: string | null
  max_concurrency: number
  current_concurrency: number
  public_ip: string | null
  agent_port: number | null
  physical_host_id: string | null
  physical_host_name: string | null
  container_id: string | null
  instance_name: string | null
}

export interface NodeCreate {
  hostname: string
  ip_address?: string
  os?: 'WINDOWS' | 'LINUX' | 'MACOS' | 'UNKNOWN'
  physical_host_id?: string
  physical_host_name?: string
  container_id?: string
  instance_name?: string
}

export interface NodeUpdate {
  ip_address?: string
  os?: 'WINDOWS' | 'LINUX' | 'MACOS' | 'UNKNOWN'
  os_version?: string
  cpu_cores?: number
  cpu_usage?: number
  memory_gb?: number
  memory_usage?: number
  disk_gb?: number
  disk_usage?: number
  version?: string
  python_version?: string
  tags?: string
  capabilities?: string
  max_concurrency?: number
  public_ip?: string
  agent_port?: number
  physical_host_id?: string
  physical_host_name?: string
  container_id?: string
  instance_name?: string
}