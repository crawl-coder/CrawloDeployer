<template>
  <div class="node-list">
    <el-card class="summary-card">
      <el-row :gutter="20">
        <el-col :span="8">
          <div class="summary-item">
            <div class="summary-icon primary">
              <el-icon><Monitor /></el-icon>
            </div>
            <div class="summary-info">
              <div class="summary-value">{{ nodeStore.nodeCount }}</div>
              <div class="summary-label">总节点数</div>
            </div>
          </div>
        </el-col>
        
        <el-col :span="8">
          <div class="summary-item">
            <div class="summary-icon success">
              <el-icon><Check /></el-icon>
            </div>
            <div class="summary-info">
              <div class="summary-value">{{ nodeStore.onlineNodes.length }}</div>
              <div class="summary-label">在线节点</div>
            </div>
          </div>
        </el-col>
        
        <el-col :span="8">
          <div class="summary-item">
            <div class="summary-icon danger">
              <el-icon><Close /></el-icon>
            </div>
            <div class="summary-info">
              <div class="summary-value">{{ nodeStore.offlineNodes.length }}</div>
              <div class="summary-label">离线节点</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </el-card>
    
    <el-card class="nodes-card">
      <template #header>
        <div class="card-header">
          <span>节点列表</span>
          <div class="header-actions">
            <el-button type="primary" @click="handleAddNode">
              <el-icon><Plus /></el-icon>
              添加节点
            </el-button>
            <el-button @click="handleViewPhysicalHosts">
              <el-icon><Monitor /></el-icon>
              物理主机管理
            </el-button>
            <el-button link @click="handleRefresh">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>
      
      <el-table
        :data="nodeStore.nodes"
        v-loading="nodeStore.loading"
        style="width: 100%"
        row-key="id"
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
        <el-table-column prop="physical_host_name" label="物理主机" width="150">
          <template #default="{ row }">
            {{ row.physical_host_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="instance_name" label="实例名称" width="150">
          <template #default="{ row }">
            {{ row.instance_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="cpu_usage" label="CPU使用率" width="120">
          <template #default="{ row }">
            <el-progress
              v-if="row.cpu_usage !== null"
              :percentage="row.cpu_usage"
              :status="row.cpu_usage > 80 ? 'exception' : ''"
            />
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="memory_usage" label="内存使用" width="150">
          <template #default="{ row }">
            <div v-if="row.memory_gb && row.memory_usage">
              <div>{{ row.memory_usage.toFixed(2) }} / {{ row.memory_gb.toFixed(2) }} GB</div>
              <el-progress
                :percentage="row.memory_gb ? (row.memory_usage / row.memory_gb * 100) : 0"
                :status="(row.memory_usage / row.memory_gb * 100) > 80 ? 'exception' : ''"
              />
            </div>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="last_heartbeat" label="最后心跳" width="180">
          <template #default="{ row }">
            {{ row.last_heartbeat ? formatDate(row.last_heartbeat) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="version" label="版本" width="100" />
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button link @click="handleViewDetail(row)">详情</el-button>
            <el-button
              v-if="row.status === 'ONLINE'"
              link
              type="danger"
              @click="handleMarkOffline(row)"
            >
              离线
            </el-button>
            <el-button
              link
              type="danger"
              @click="handleDeleteNode(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="nodeStore.nodeCount"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
    
    <!-- 节点详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="节点详情"
      width="800px"
    >
      <el-descriptions v-if="nodeStore.currentNode" :column="2" border>
        <el-descriptions-item label="主机名">
          {{ nodeStore.currentNode.hostname }}
        </el-descriptions-item>
        <el-descriptions-item label="IP地址">
          {{ nodeStore.currentNode.ip_address || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusTagType(nodeStore.currentNode.status)">
            {{ getStatusText(nodeStore.currentNode.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="操作系统">
          {{ getOsText(nodeStore.currentNode.os) }}
        </el-descriptions-item>
        <el-descriptions-item label="操作系统版本">
          {{ nodeStore.currentNode.os_version || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="注册时间">
          {{ formatDate(nodeStore.currentNode.registered_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="最后心跳">
          {{ nodeStore.currentNode.last_heartbeat ? formatDate(nodeStore.currentNode.last_heartbeat) : '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="Worker版本">
          {{ nodeStore.currentNode.version || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="Python版本">
          {{ nodeStore.currentNode.python_version || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="CPU核心数">
          {{ nodeStore.currentNode.cpu_cores || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="CPU使用率">
          <el-progress
            v-if="nodeStore.currentNode.cpu_usage !== null"
            :percentage="nodeStore.currentNode.cpu_usage"
            :status="nodeStore.currentNode.cpu_usage > 80 ? 'exception' : ''"
          />
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="内存">
          <div v-if="nodeStore.currentNode.memory_gb && nodeStore.currentNode.memory_usage">
            <div>{{ nodeStore.currentNode.memory_usage.toFixed(2) }} / {{ nodeStore.currentNode.memory_gb.toFixed(2) }} GB</div>
            <el-progress
              :percentage="nodeStore.currentNode.memory_gb ? (nodeStore.currentNode.memory_usage / nodeStore.currentNode.memory_gb * 100) : 0"
              :status="(nodeStore.currentNode.memory_usage / nodeStore.currentNode.memory_gb * 100) > 80 ? 'exception' : ''"
            />
          </div>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="磁盘">
          <div v-if="nodeStore.currentNode.disk_gb && nodeStore.currentNode.disk_usage">
            <div>{{ nodeStore.currentNode.disk_usage.toFixed(2) }} / {{ nodeStore.currentNode.disk_gb.toFixed(2) }} GB</div>
            <el-progress
              :percentage="nodeStore.currentNode.disk_gb ? (nodeStore.currentNode.disk_usage / nodeStore.currentNode.disk_gb * 100) : 0"
              :status="(nodeStore.currentNode.disk_usage / nodeStore.currentNode.disk_gb * 100) > 80 ? 'exception' : ''"
            />
          </div>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="最大并发数">
          {{ nodeStore.currentNode.max_concurrency }}
        </el-descriptions-item>
        <el-descriptions-item label="当前并发数">
          {{ nodeStore.currentNode.current_concurrency }}
        </el-descriptions-item>
        <el-descriptions-item label="标签">
          {{ nodeStore.currentNode.tags || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="能力">
          {{ nodeStore.currentNode.capabilities || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="公网IP">
          {{ nodeStore.currentNode.public_ip || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="通信端口">
          {{ nodeStore.currentNode.agent_port || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="物理主机ID">
          {{ nodeStore.currentNode.physical_host_id || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="物理主机名">
          {{ nodeStore.currentNode.physical_host_name || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="容器ID">
          {{ nodeStore.currentNode.container_id || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="实例名称">
          {{ nodeStore.currentNode.instance_name || '-' }}
        </el-descriptions-item>
      </el-descriptions>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="detailDialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 添加节点对话框 -->
    <el-dialog
      v-model="addNodeDialogVisible"
      title="添加节点"
      width="600px"
    >
      <el-form
        :model="newNodeForm"
        :rules="addNodeRules"
        ref="addNodeFormRef"
        label-width="120px"
      >
        <el-form-item label="主机名" prop="hostname">
          <el-input v-model="newNodeForm.hostname" placeholder="请输入节点主机名" />
        </el-form-item>
        <el-form-item label="IP地址" prop="ip_address">
          <el-input v-model="newNodeForm.ip_address" placeholder="请输入节点IP地址" />
        </el-form-item>
        <el-form-item label="操作系统" prop="os">
          <el-select v-model="newNodeForm.os" placeholder="请选择操作系统">
            <el-option label="Windows" value="WINDOWS" />
            <el-option label="Linux" value="LINUX" />
            <el-option label="macOS" value="MACOS" />
            <el-option label="未知" value="UNKNOWN" />
          </el-select>
        </el-form-item>
        <el-form-item label="物理主机名" prop="physical_host_name">
          <el-input v-model="newNodeForm.physical_host_name" placeholder="请输入物理主机名（可选）" />
        </el-form-item>
        <el-form-item label="实例名称" prop="instance_name">
          <el-input v-model="newNodeForm.instance_name" placeholder="请输入实例名称（可选）" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="addNodeDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleCreateNode">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useNodeStore } from '@/store/node'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance } from 'element-plus'
import type { Node, NodeCreate } from '@/types/node'

const nodeStore = useNodeStore()
const router = useRouter()

// 分页相关
const currentPage = ref(1)
const pageSize = ref(10)

// 对话框相关
const detailDialogVisible = ref(false)
const addNodeDialogVisible = ref(false)

// 表单相关
const addNodeFormRef = ref<FormInstance>()
const newNodeForm = reactive({
  hostname: '',
  ip_address: '',
  os: 'UNKNOWN',
  physical_host_name: '',
  instance_name: ''
})

const addNodeRules = {
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

// 生命周期钩子
onMounted(() => {
  nodeStore.fetchNodes()
})

// 方法定义
const handleRefresh = () => {
  nodeStore.fetchNodes()
}

const handleViewPhysicalHosts = () => {
  router.push('/physical-hosts')
}

const handleViewDetail = async (node: Node) => {
  await nodeStore.fetchNode(node.id)
  detailDialogVisible.value = true
}

const handleMarkOffline = (node: Node) => {
  ElMessageBox.confirm(
    `确定要将节点 ${node.hostname} 标记为离线吗？`,
    '确认操作',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    const result = await nodeStore.markOffline(node.id)
    if (result.success) {
      ElMessage.success('节点已标记为离线')
      nodeStore.fetchNodes()
    } else {
      ElMessage.error(result.message || '操作失败')
    }
  }).catch(() => {
    // 用户取消操作
  })
}

const handleAddNode = () => {
  // 重置表单
  newNodeForm.hostname = ''
  newNodeForm.ip_address = ''
  newNodeForm.os = 'UNKNOWN'
  newNodeForm.physical_host_name = ''
  newNodeForm.instance_name = ''
  addNodeDialogVisible.value = true
}

const handleCreateNode = async () => {
  if (!addNodeFormRef.value) return
  
  await addNodeFormRef.value.validate(async (valid) => {
    if (valid) {
      // 调用API创建节点
      // 确保os字段是正确的枚举类型
      let osValue: "WINDOWS" | "LINUX" | "MACOS" | "UNKNOWN" | undefined;
      if (newNodeForm.os && 
          (newNodeForm.os === "WINDOWS" || 
           newNodeForm.os === "LINUX" || 
           newNodeForm.os === "MACOS" || 
           newNodeForm.os === "UNKNOWN")) {
        osValue = newNodeForm.os;
      }
      
      const nodeData: NodeCreate = {
        hostname: newNodeForm.hostname,
        ip_address: newNodeForm.ip_address,
        os: osValue,
        physical_host_name: newNodeForm.physical_host_name || undefined,
        instance_name: newNodeForm.instance_name || undefined
      }
      
      const result = await nodeStore.createNewNode(nodeData)
      if (result.success) {
        addNodeDialogVisible.value = false
        nodeStore.fetchNodes()
      }
    }
  })
}

const handleDeleteNode = (node: Node) => {
  ElMessageBox.confirm(
    `确定要删除节点 ${node.hostname} 吗？此操作不可恢复。`,
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    // 调用API删除节点
    const result = await nodeStore.deleteExistingNode(node.id)
    if (result.success) {
      nodeStore.fetchNodes()
    }
  }).catch(() => {
    // 用户取消操作
  })
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  nodeStore.fetchNodes()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  nodeStore.fetchNodes({ skip: (val - 1) * pageSize.value, limit: pageSize.value })
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

const formatDate = (dateString: string) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}
</script>

<style scoped>
.node-list {
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

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>