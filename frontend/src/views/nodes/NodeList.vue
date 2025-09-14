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
        <el-descriptions-item label="公网IP">
          {{ nodeStore.currentNode.public_ip || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="代理端口">
          {{ nodeStore.currentNode.agent_port || '-' }}
        </el-descriptions-item>
      </el-descriptions>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="detailDialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Monitor,
  Check,
  Close,
  Refresh
} from '@element-plus/icons-vue'
import { useNodeStore } from '@/store/node'
import type { Node } from '@/types/node'

// Store
const nodeStore = useNodeStore()

// 响应式数据
const currentPage = ref(1)
const pageSize = ref(10)
const detailDialogVisible = ref(false)

// 方法
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
      return '未知'
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
    case 'UNKNOWN':
      return '未知'
    default:
      return os
  }
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

const handleRefresh = async () => {
  await nodeStore.fetchNodes({
    skip: (currentPage.value - 1) * pageSize.value,
    limit: pageSize.value
  })
}

const handleViewDetail = async (node: Node) => {
  const result = await nodeStore.fetchNode(node.id)
  if (result) {
    detailDialogVisible.value = true
  } else {
    ElMessage.error('获取节点详情失败')
  }
}

const handleMarkOffline = async (node: Node) => {
  try {
    const result = await nodeStore.markOffline(node.id)
    if (result.success) {
      ElMessage.success('节点已标记为离线')
      await handleRefresh()
    } else {
      ElMessage.error(result.message || '标记节点离线失败')
    }
  } catch (error) {
    ElMessage.error('标记节点离线失败')
  }
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  handleRefresh()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  handleRefresh()
}

// 生命周期
onMounted(async () => {
  await nodeStore.fetchNodes({
    skip: 0,
    limit: pageSize.value
  })
})

// 监听分页变化
watch([currentPage, pageSize], async () => {
  await nodeStore.fetchNodes({
    skip: (currentPage.value - 1) * pageSize.value,
    limit: pageSize.value
  })
})
</script>

<style scoped>
.node-list {
  padding: 20px;
}

.summary-card {
  margin-bottom: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.summary-item {
  display: flex;
  align-items: center;
  padding: 20px 0;
}

.summary-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  font-size: 20px;
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

.summary-value {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 5px;
}

.summary-label {
  color: #999;
  font-size: 14px;
}

.nodes-card {
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>