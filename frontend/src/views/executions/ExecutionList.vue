<template>
  <div class="execution-list">
    <el-card class="filter-card">
      <el-form :model="filterForm" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-form-item label="任务名称">
              <el-input v-model="filterForm.taskName" placeholder="请输入任务名称" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="执行状态">
              <el-select v-model="filterForm.status" placeholder="请选择状态" clearable>
                <el-option label="成功" value="success" />
                <el-option label="失败" value="failed" />
                <el-option label="运行中" value="running" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="执行时间">
              <el-date-picker
                v-model="filterForm.dateRange"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item>
              <el-button type="primary" @click="handleSearch">查询</el-button>
              <el-button @click="handleReset">重置</el-button>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <el-card>
      <template #header>
        <div class="card-header">
          <span>任务执行记录</span>
          <el-button type="primary" @click="handleRefresh">刷新</el-button>
        </div>
      </template>

      <el-table
        :data="executionList"
        v-loading="loading"
        stripe
        style="width: 100%"
        @sort-change="handleSortChange"
      >
        <el-table-column prop="id" label="执行ID" width="100" sortable="custom" />
        <el-table-column prop="taskName" label="任务名称" min-width="150" />
        <el-table-column prop="projectName" label="所属项目" min-width="120" />
        <el-table-column prop="nodeName" label="执行节点" min-width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="startTime" label="开始时间" width="180" sortable="custom" />
        <el-table-column prop="endTime" label="结束时间" width="180" sortable="custom" />
        <el-table-column prop="duration" label="执行时长" width="120" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewDetail(row)">详情</el-button>
            <el-button link type="primary" @click="viewLogs(row)">日志</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.currentPage"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 执行详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="执行详情"
      width="60%"
      :before-close="handleDetailDialogClose"
    >
      <el-descriptions :column="2" border>
        <el-descriptions-item label="执行ID">{{ currentExecution.id }}</el-descriptions-item>
        <el-descriptions-item label="任务名称">{{ currentExecution.taskName }}</el-descriptions-item>
        <el-descriptions-item label="所属项目">{{ currentExecution.projectName }}</el-descriptions-item>
        <el-descriptions-item label="执行节点">{{ currentExecution.nodeName }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentExecution.status)">
            {{ getStatusText(currentExecution.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="开始时间">{{ currentExecution.startTime }}</el-descriptions-item>
        <el-descriptions-item label="结束时间">{{ currentExecution.endTime }}</el-descriptions-item>
        <el-descriptions-item label="执行时长">{{ currentExecution.duration }}</el-descriptions-item>
        <el-descriptions-item label="结果数据">{{ currentExecution.resultCount }} 条</el-descriptions-item>
        <el-descriptions-item label="错误信息" :span="2">
          <el-alert
            v-if="currentExecution.errorMessage"
            :title="currentExecution.errorMessage"
            type="error"
            :closable="false"
          />
          <span v-else>无</span>
        </el-descriptions-item>
      </el-descriptions>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="detailDialogVisible = false">关闭</el-button>
          <el-button type="primary" @click="exportResults">导出结果</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 日志查看对话框 -->
    <el-dialog
      v-model="logDialogVisible"
      title="执行日志"
      width="70%"
      :before-close="handleLogDialogClose"
    >
      <div class="log-container">
        <pre class="log-content">{{ logContent }}</pre>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="logDialogVisible = false">关闭</el-button>
          <el-button type="primary" @click="downloadLogs">下载日志</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { ExecutionService } from '@/services/execution'
import { Execution } from '@/types/execution'

// 数据状态
const loading = ref(false)
const executionList = ref<Execution[]>([])
const detailDialogVisible = ref(false)
const logDialogVisible = ref(false)
const logContent = ref('')
const currentExecution = ref<Execution>({} as Execution)

// 过滤表单
const filterForm = reactive({
  taskName: '',
  status: '',
  dateRange: []
})

// 分页
const pagination = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 0
})

// 排序
const sortParams = reactive({
  field: '',
  order: ''
})

// 获取执行记录列表
const fetchExecutionList = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.currentPage,
      size: pagination.pageSize,
      taskName: filterForm.taskName || undefined,
      status: filterForm.status || undefined,
      startDate: filterForm.dateRange?.[0],
      endDate: filterForm.dateRange?.[1],
      sortBy: sortParams.field || undefined,
      sortOrder: sortParams.order || undefined
    }
    
    const response = await ExecutionService.getList(params)
    executionList.value = response.data.items
    pagination.total = response.data.total
  } catch (error) {
    ElMessage.error('获取执行记录失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 状态显示
const getStatusType = (status: string) => {
  switch (status) {
    case 'success': return 'success'
    case 'failed': return 'danger'
    case 'running': return 'warning'
    default: return 'info'
  }
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'success': return '成功'
    case 'failed': return '失败'
    case 'running': return '运行中'
    default: return status
  }
}

// 操作处理
const handleSearch = () => {
  pagination.currentPage = 1
  fetchExecutionList()
}

const handleReset = () => {
  filterForm.taskName = ''
  filterForm.status = ''
  filterForm.dateRange = []
  pagination.currentPage = 1
  fetchExecutionList()
}

const handleRefresh = () => {
  fetchExecutionList()
}

const handleSortChange = ({ prop, order }: any) => {
  sortParams.field = prop
  sortParams.order = order === 'ascending' ? 'asc' : order === 'descending' ? 'desc' : ''
  fetchExecutionList()
}

const handleSizeChange = (val: number) => {
  pagination.pageSize = val
  pagination.currentPage = 1
  fetchExecutionList()
}

const handleCurrentChange = (val: number) => {
  pagination.currentPage = val
  fetchExecutionList()
}

const viewDetail = (row: Execution) => {
  currentExecution.value = row
  detailDialogVisible.value = true
}

const viewLogs = async (row: Execution) => {
  try {
    const response = await ExecutionService.getLogs(row.id)
    logContent.value = response.data.logs
    logDialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取日志失败')
    console.error(error)
  }
}

const exportResults = () => {
  ElMessage.info('导出功能待实现')
}

const downloadLogs = () => {
  ElMessage.info('下载日志功能待实现')
}

const handleDetailDialogClose = () => {
  detailDialogVisible.value = false
}

const handleLogDialogClose = () => {
  logDialogVisible.value = false
}

// 初始化
onMounted(() => {
  fetchExecutionList()
})
</script>

<style scoped>
.execution-list {
  padding: 20px;
}

.filter-card {
  margin-bottom: 20px;
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

.log-container {
  max-height: 400px;
  overflow-y: auto;
  background-color: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
}

.log-content {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.5;
}
</style>