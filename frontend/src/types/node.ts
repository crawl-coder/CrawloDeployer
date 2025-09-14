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
}