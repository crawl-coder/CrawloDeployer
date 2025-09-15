<template>
  <div class="physical-host-list">
    <el-card class="summary-card">
      <el-row :gutter="20">
        <el-col :span="8">
          <div class="summary-item">
            <div class="summary-icon primary">
              <el-icon><Monitor /></el-icon>
            </div>
            <div class="summary-info">
              <div class="summary-value">{{ physicalHosts.length }}</div>
              <div class="summary-label">物理主机数</div>
            </div>
          </div>
        </el-col>
        
        <el-col :span="8">
          <div class="summary-item">
            <div class="summary-icon success">
              <el-icon><Cpu /></el-icon>
            </div>
            <div class="summary-info">
              <div class="summary-value">{{ totalCpuCores }}</div>
              <div class="summary-label">总CPU核心数</div>
            </div>
          </div>
        </el-col>
        
        <el-col :span="8">
          <div class="summary-item">
            <div class="summary-icon warning">
              <el-icon><Box /></el-icon>
            </div>
            <div class="summary-info">
              <div class="summary-value">{{ totalMemory }} GB</div>
              <div class="summary-label">总内存</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </el-card>
    
    <el-card class="hosts-card">
      <template #header>
        <div class="card-header">
          <span>物理主机列表</span>
          <div class="header-actions">
            <el-button type="primary" @click="handleAddPhysicalHost">
              <el-icon><Plus /></el-icon>
              添加物理主机
            </el-button>
            <el-button link @click="handleRefresh">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>
      
      <el-table
        :data="physicalHosts"
        v-loading="loading"
        style="width: 100%"
        row-key="physical_host_name"
      >
        <el-table-column prop="physical_host_name" label="物理主机名" min-width="150" />
        <el-table-column prop="total_nodes" label="总节点数" width="100" />
        <el-table-column prop="logical_nodes" label="逻辑节点数" width="120" />
        <el-table-column prop="online_nodes" label="在线节点" width="100">
          <template #default="{ row }">
            <el-tag type="success">{{ row.online_nodes }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="offline_nodes" label="离线节点" width="100">
          <template #default="{ row }">
            <el-tag type="danger">{{ row.offline_nodes }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="cpu_cores" label="CPU核心" width="100">
          <template #default="{ row }">
            {{ row.cpu_cores || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="memory_gb" label="内存(GB)" width="120">
          <template #default="{ row }">
            {{ row.memory_gb ? row.memory_gb.toFixed(2) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="disk_gb" label="磁盘(GB)" width="120">
          <template #default="{ row }">
            {{ row.disk_gb ? row.disk_gb.toFixed(2) : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="资源使用率" width="150">
          <template #default="{ row }">
            <el-popover trigger="hover" placement="top">
              <template #default>
                <div>逻辑节点数: {{ row.logical_nodes }}</div>
                <div>CPU核心数: {{ row.cpu_cores || '-' }}</div>
                <div>内存: {{ row.memory_gb ? row.memory_gb.toFixed(2) : '-' }} GB</div>
                <div>磁盘: {{ row.disk_gb ? row.disk_gb.toFixed(2) : '-' }} GB</div>
              </template>
              <template #reference>
                <el-button link>查看详情</el-button>
              </template>
            </el-popover>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button link @click="handleViewDetails(row)">详情</el-button>
            <el-button link @click="handleCheckResources(row)">检查资源</el-button>
            <el-button link type="primary" @click="handleAddLogicalNode(row)">添加逻辑节点</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 物理主机详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="物理主机详情"
      width="800px"
    >
      <el-descriptions v-if="currentHost" :column="2" border>
        <el-descriptions-item label="物理主机名">
          {{ currentHost.physical_host_name }}
        </el-descriptions-item>
        <el-descriptions-item label="总节点数">
          {{ currentHost.total_nodes }}
        </el-descriptions-item>
        <el-descriptions-item label="逻辑节点数">
          {{ currentHost.logical_nodes }}
        </el-descriptions-item>
        <el-descriptions-item label="在线节点">
          <el-tag type="success">{{ currentHost.online_nodes }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="离线节点">
          <el-tag type="danger">{{ currentHost.offline_nodes }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="CPU核心数">
          {{ currentHost.cpu_cores || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="总内存">
          {{ currentHost.memory_gb ? currentHost.memory_gb.toFixed(2) + ' GB' : '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="总磁盘">
          {{ currentHost.disk_gb ? currentHost.disk_gb.toFixed(2) + ' GB' : '-' }}
        </el-descriptions-item>
      </el-descriptions>
      
      <el-divider>逻辑节点列表</el-divider>
      
      <el-table
        :data="logicalNodes"
        style="width: 100%"
      >
        <el-table-column prop="hostname" label="主机名" min-width="150" />
        <el-table-column prop="ip_address" label="IP地址" width="150" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="os" label="操作系统" width="120">
          <template #default="{ row }">
            {{ getOsText(row.os) }}
          </template>
        </el-table-column>
        <el-table-column prop="instance_name" label="实例名称" width="150">
          <template #default="{ row }">
            {{ row.instance_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="cpu_cores" label="CPU核心" width="100">
          <template #default="{ row }">
            {{ row.cpu_cores || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="memory_gb" label="内存(GB)" width="120">
          <template #default="{ row }">
            {{ row.memory_gb ? row.memory_gb.toFixed(2) : '-' }}
          </template>
        </el-table-column>
      </el-table>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="detailDialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 资源检查对话框 -->
    <el-dialog
      v-model="resourceCheckDialogVisible"
      title="资源检查"
      width="600px"
    >
      <el-form
        :model="resourceCheckForm"
        label-width="120px"
      >
        <el-form-item label="所需CPU核心">
          <el-input-number
            v-model="resourceCheckForm.required_cpu_cores"
            :min="1"
            :max="currentHost?.cpu_cores || 32"
            controls-position="right"
          />
        </el-form-item>
        <el-form-item label="所需内存(GB)">
          <el-input-number
            v-model="resourceCheckForm.required_memory_gb"
            :min="0.1"
            :max="currentHost?.memory_gb || 128"
            :step="0.1"
            controls-position="right"
          />
        </el-form-item>
        <el-form-item label="所需磁盘(GB)">
          <el-input-number
            v-model="resourceCheckForm.required_disk_gb"
            :min="0.1"
            :max="currentHost?.disk_gb || 1000"
            :step="0.1"
            controls-position="right"
          />
        </el-form-item>
      </el-form>
      
      <div v-if="resourceCheckResult" class="resource-result">
        <el-alert
          :type="resourceCheckResult.available ? 'success' : 'error'"
          :title="resourceCheckResult.reason"
          show-icon
        />
        
        <el-descriptions :column="2" size="small" style="margin-top: 20px;">
          <el-descriptions-item label="所需CPU">
            {{ resourceCheckResult.details.required_cpu }} 核心
          </el-descriptions-item>
          <el-descriptions-item label="可用CPU">
            {{ resourceCheckResult.details.available_cpu }} 核心
          </el-descriptions-item>
          <el-descriptions-item label="所需内存">
            {{ resourceCheckResult.details.required_memory }} GB
          </el-descriptions-item>
          <el-descriptions-item label="可用内存">
            {{ resourceCheckResult.details.available_memory.toFixed(2) }} GB
          </el-descriptions-item>
          <el-descriptions-item label="所需磁盘">
            {{ resourceCheckResult.details.required_disk }} GB
          </el-descriptions-item>
          <el-descriptions-item label="可用磁盘">
            {{ resourceCheckResult.details.available_disk.toFixed(2) }} GB
          </el-descriptions-item>
        </el-descriptions>
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="resourceCheckDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handlePerformResourceCheck">检查</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 添加逻辑节点对话框 -->
    <el-dialog
      v-model="addLogicalNodeDialogVisible"
      title="添加逻辑节点"
      width="600px"
    >
      <el-form
        :model="logicalNodeForm"
        :rules="logicalNodeRules"
        ref="logicalNodeFormRef"
        label-width="120px"
      >
        <el-form-item label="主机名" prop="hostname">
          <el-input v-model="logicalNodeForm.hostname" placeholder="请输入节点主机名" />
        </el-form-item>
        <el-form-item label="IP地址" prop="ip_address">
          <el-input v-model="logicalNodeForm.ip_address" placeholder="请输入节点IP地址" />
        </el-form-item>
        <el-form-item label="操作系统" prop="os">
          <el-select v-model="logicalNodeForm.os" placeholder="请选择操作系统">
            <el-option label="Windows" value="WINDOWS" />
            <el-option label="Linux" value="LINUX" />
            <el-option label="macOS" value="MACOS" />
            <el-option label="未知" value="UNKNOWN" />
          </el-select>
        </el-form-item>
        <el-form-item label="实例名称" prop="instance_name">
          <el-input v-model="logicalNodeForm.instance_name" placeholder="请输入实例名称（可选）" />
        </el-form-item>
        <el-form-item label="所需CPU核心">
          <el-input-number
            v-model="logicalNodeForm.cpu_cores"
            :min="1"
            controls-position="right"
          />
        </el-form-item>
        <el-form-item label="所需内存(GB)">
          <el-input-number
            v-model="logicalNodeForm.memory_gb"
            :min="0.1"
            :step="0.1"
            controls-position="right"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="addLogicalNodeDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleCreateLogicalNode">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useNodeStore } from '@/store/node'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance } from 'element-plus'
import type { Node, NodeCreate } from '@/types/node'
import {
  Monitor,
  Cpu,
  Box,
  Plus,
  Refresh
} from '@element-plus/icons-vue'

const nodeStore = useNodeStore()

// 数据相关
const physicalHosts = ref<any[]>([])
const currentHost = ref<any>(null)
const logicalNodes = ref<Node[]>([])
const loading = ref(false)

// 对话框相关
const detailDialogVisible = ref(false)
const resourceCheckDialogVisible = ref(false)
const addLogicalNodeDialogVisible = ref(false)

// 表单相关
const logicalNodeFormRef = ref<FormInstance>()
const resourceCheckForm = reactive({
  required_cpu_cores: 1,
  required_memory_gb: 1.0,
  required_disk_gb: 1.0
})

const logicalNodeForm = reactive({
  hostname: '',
  ip_address: '',
  os: 'UNKNOWN',
  instance_name: '',
  cpu_cores: 1,
  memory_gb: 1.0
})

const logicalNodeRules = {
  hostname: [
    { required: true, message: '请输入主机名', trigger: 'blur' }
  ],
  ip_address: [
    { required: true, message: '请输入IP地址', trigger: 'blur' }
  ],
  os: [
    { required: true, message: '请选择操作系统', trigger: 'change' }
  ]
}

const resourceCheckResult = ref<any>(null)

// 计算属性
const totalCpuCores = computed(() => {
  return physicalHosts.value.reduce((sum, host) => sum + (host.cpu_cores || 0), 0)
})

const totalMemory = computed(() => {
  return physicalHosts.value.reduce((sum, host) => sum + (host.memory_gb || 0), 0).toFixed(2)
})

// 生命周期钩子
onMounted(() => {
  fetchPhysicalHosts()
})

// 方法定义
const fetchPhysicalHosts = async () => {
  loading.value = true
  try {
    const result = await nodeStore.fetchPhysicalHosts()
    if (result.success) {
      physicalHosts.value = result.data || []
    }
  } finally {
    loading.value = false
  }
}

const handleRefresh = () => {
  fetchPhysicalHosts()
}

const handleAddPhysicalHost = () => {
  ElMessage.info('请在物理主机上启动Worker以自动添加')
}

const handleViewDetails = async (host: any) => {
  currentHost.value = host
  // 获取该物理主机上的所有逻辑节点
  await nodeStore.fetchNodes()
  logicalNodes.value = nodeStore.nodes.filter(
    node => node.physical_host_name === host.physical_host_name
  )
  detailDialogVisible.value = true
}

const handleCheckResources = (host: any) => {
  currentHost.value = host
  resourceCheckForm.required_cpu_cores = 1
  resourceCheckForm.required_memory_gb = 1.0
  resourceCheckForm.required_disk_gb = 1.0
  resourceCheckResult.value = null
  resourceCheckDialogVisible.value = true
}

const handlePerformResourceCheck = async () => {
  if (!currentHost.value) return
  
  const result = await nodeStore.checkNodeResources({
    physical_host_name: currentHost.value.physical_host_name,
    required_cpu_cores: resourceCheckForm.required_cpu_cores,
    required_memory_gb: resourceCheckForm.required_memory_gb,
    required_disk_gb: resourceCheckForm.required_disk_gb
  })
  
  if (result.success) {
    resourceCheckResult.value = result.data
  }
}

const handleAddLogicalNode = (host: any) => {
  currentHost.value = host
  // 重置表单
  logicalNodeForm.hostname = ''
  logicalNodeForm.ip_address = ''
  logicalNodeForm.os = 'UNKNOWN'
  logicalNodeForm.instance_name = ''
  logicalNodeForm.cpu_cores = 1
  logicalNodeForm.memory_gb = 1.0
  addLogicalNodeDialogVisible.value = true
}

const handleCreateLogicalNode = async () => {
  if (!logicalNodeFormRef.value) return
  
  await logicalNodeFormRef.value.validate(async (valid) => {
    if (valid && currentHost.value) {
      // 先检查资源是否足够
      const checkResult = await nodeStore.checkNodeResources({
        physical_host_name: currentHost.value.physical_host_name,
        required_cpu_cores: logicalNodeForm.cpu_cores,
        required_memory_gb: logicalNodeForm.memory_gb,
        required_disk_gb: 1.0 // 磁盘检查暂时设为1GB
      })
      
      if (checkResult.success && checkResult.data.available) {
        // 资源足够，创建节点
        // 构造符合NodeCreate接口的对象
        const nodeData: NodeCreate = {
          hostname: logicalNodeForm.hostname,
          ip_address: logicalNodeForm.ip_address,
          os: logicalNodeForm.os as "WINDOWS" | "LINUX" | "MACOS" | "UNKNOWN" | undefined,
          physical_host_name: currentHost.value.physical_host_name,
          instance_name: logicalNodeForm.instance_name || undefined
          // 注意：cpu_cores 和 memory_gb 不在 NodeCreate 接口中
        }
        
        const result = await nodeStore.createNewNode(nodeData)
        if (result.success) {
          ElMessage.success('逻辑节点创建成功')
          addLogicalNodeDialogVisible.value = false
          fetchPhysicalHosts() // 刷新物理主机列表
        }
      } else {
        ElMessage.error('资源不足，无法创建逻辑节点')
      }
    }
  })
}

// 工具方法
const getStatusTagType = (status: string) => {
  switch (status) {
    case 'ONLINE':
      return 'success'
    case 'OFFLINE':
      return 'danger'
    default:
      return 'info'
  }
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'ONLINE':
      return '在线'
    case 'OFFLINE':
      return '离线'
    default:
      return status
  }
}

const getOsText = (os: string) => {
  switch (os) {
    case 'WINDOWS':
      return 'Windows'
    case 'LINUX':
      return 'Linux'
    case 'MACOS':
      return 'macOS'
    default:
      return '未知'
  }
}
</script>

<style scoped>
.physical-host-list {
  padding: 20px;
}

.summary-card {
  margin-bottom: 20px;
}

.summary-item {
  display: flex;
  align-items: center;
}

.summary-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  font-size: 24px;
}

.summary-icon.primary {
  background-color: #ecf5ff;
  color: #409eff;
}

.summary-icon.success {
  background-color: #f0f9ff;
  color: #67c23a;
}

.summary-icon.warning {
  background-color: #fdf6ec;
  color: #e6a23c;
}

.summary-icon.danger {
  background-color: #fef0f0;
  color: #f56c6c;
}

.summary-info {
  flex: 1;
}

.summary-value {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 5px;
}

.summary-label {
  font-size: 14px;
  color: #909399;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.resource-result {
  margin-top: 20px;
}
</style>