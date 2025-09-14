<template>
  <div class="execution-detail">
    <el-card class="breadcrumb-card">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/executions' }">任务执行记录</el-breadcrumb-item>
        <el-breadcrumb-item>执行详情</el-breadcrumb-item>
      </el-breadcrumb>
    </el-card>

    <el-card class="info-card">
      <template #header>
        <div class="card-header">
          <span>执行基本信息</span>
        </div>
      </template>
      
      <el-descriptions :column="3" border>
        <el-descriptions-item label="执行ID">{{ executionInfo.id }}</el-descriptions-item>
        <el-descriptions-item label="任务名称">{{ executionInfo.taskName }}</el-descriptions-item>
        <el-descriptions-item label="所属项目">{{ executionInfo.projectName }}</el-descriptions-item>
        <el-descriptions-item label="执行节点">{{ executionInfo.nodeName }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(executionInfo.status)">
            {{ getStatusText(executionInfo.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="开始时间">{{ executionInfo.startTime }}</el-descriptions-item>
        <el-descriptions-item label="结束时间">{{ executionInfo.endTime }}</el-descriptions-item>
        <el-descriptions-item label="执行时长">{{ executionInfo.duration }}</el-descriptions-item>
        <el-descriptions-item label="结果数据">{{ executionInfo.resultCount }} 条</el-descriptions-item>
        <el-descriptions-item label="创建人">{{ executionInfo.creator }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ executionInfo.createdAt }}</el-descriptions-item>
      </el-descriptions>
      
      <div class="error-section" v-if="executionInfo.errorMessage">
        <h4>错误信息</h4>
        <el-alert
          :title="executionInfo.errorMessage"
          type="error"
          :closable="false"
        />
      </div>
    </el-card>

    <el-card class="tabs-card">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="执行日志" name="logs">
          <div class="log-container">
            <div class="log-actions">
              <el-button type="primary" @click="downloadLogs">下载日志</el-button>
              <el-button @click="refreshLogs">刷新</el-button>
            </div>
            <pre class="log-content">{{ logContent }}</pre>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="执行结果" name="results">
          <div class="results-container">
            <div class="results-actions">
              <el-input
                v-model="resultFilter"
                placeholder="搜索结果..."
                style="width: 300px; margin-right: 10px;"
              />
              <el-button type="primary" @click="exportResults">导出结果</el-button>
            </div>
            
            <el-table
              :data="resultList"
              v-loading="resultsLoading"
              stripe
              style="width: 100%"
            >
              <el-table-column prop="id" label="ID" width="80" />
              <el-table-column prop="title" label="标题" min-width="200" />
              <el-table-column prop="url" label="URL" min-width="300" />
              <el-table-column prop="createdAt" label="抓取时间" width="180" />
              <el-table-column label="操作" width="100">
                <template #default="{ row }">
                  <el-button link type="primary" @click="viewResultDetail(row)">详情</el-button>
                </template>
              </el-table-column>
            </el-table>
            
            <div class="pagination-container">
              <el-pagination
                v-model:current-page="resultsPagination.currentPage"
                v-model:page-size="resultsPagination.pageSize"
                :page-sizes="[10, 20, 50, 100]"
                :total="resultsPagination.total"
                layout="total, sizes, prev, pager, next, jumper"
                @size-change="handleResultsSizeChange"
                @current-change="handleResultsCurrentChange"
              />
            </div>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="性能统计" name="metrics">
          <div class="metrics-container">
            <el-row :gutter="20">
              <el-col :span="6">
                <el-card class="metric-card">
                  <div class="metric-value">{{ metrics.requests }}</div>
                  <div class="metric-label">请求次数</div>
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card class="metric-card">
                  <div class="metric-value">{{ metrics.successRate }}%</div>
                  <div class="metric-label">成功率</div>
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card class="metric-card">
                  <div class="metric-value">{{ metrics.avgResponseTime }}ms</div>
                  <div class="metric-label">平均响应时间</div>
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card class="metric-card">
                  <div class="metric-value">{{ metrics.dataSize }}</div>
                  <div class="metric-label">数据大小</div>
                </el-card>
              </el-col>
            </el-row>
            
            <el-card class="chart-card">
              <template #header>
                <div class="card-header">
                  <span>执行时间线</span>
                </div>
              </template>
              <div ref="timelineChartRef" class="chart-container"></div>
            </el-card>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 结果详情对话框 -->
    <el-dialog
      v-model="resultDetailDialogVisible"
      title="结果详情"
      width="60%"
      :before-close="handleResultDetailDialogClose"
    >
      <el-descriptions :column="1" border>
        <el-descriptions-item label="ID">{{ currentResult.id }}</el-descriptions-item>
        <el-descriptions-item label="标题">{{ currentResult.title }}</el-descriptions-item>
        <el-descriptions-item label="URL">{{ currentResult.url }}</el-descriptions-item>
        <el-descriptions-item label="内容摘要">{{ currentResult.summary }}</el-descriptions-item>
        <el-descriptions-item label="抓取时间">{{ currentResult.createdAt }}</el-descriptions-item>
      </el-descriptions>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="resultDetailDialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { ExecutionService } from '@/services/execution'
import { ExecutionDetail, ExecutionResult, ExecutionMetrics } from '@/types/execution'

// 路由
const route = useRoute()

// 数据状态
const executionInfo = ref<ExecutionDetail>({} as ExecutionDetail)
const activeTab = ref('logs')
const logContent = ref('')
const resultList = ref<ExecutionResult[]>([])
const resultsLoading = ref(false)
const resultFilter = ref('')
const currentResult = ref<ExecutionResult>({} as ExecutionResult)
const resultDetailDialogVisible = ref(false)
const timelineChartRef = ref<HTMLDivElement | null>(null)
let timelineChart: echarts.ECharts | null = null

// 分页
const resultsPagination = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 0
})

// 性能统计
const metrics = ref<ExecutionMetrics>({
  requests: 0,
  successRate: 0,
  avgResponseTime: 0,
  dataSize: '0 KB'
})

// 获取执行详情
const fetchExecutionDetail = async () => {
  try {
    const response = await ExecutionService.getDetail(route.params.id as string)
    executionInfo.value = response.data
    logContent.value = response.data.logs || ''
  } catch (error) {
    ElMessage.error('获取执行详情失败')
    console.error(error)
  }
}

// 获取执行结果
const fetchExecutionResults = async () => {
  resultsLoading.value = true
  try {
    const params = {
      page: resultsPagination.currentPage,
      size: resultsPagination.pageSize,
      keyword: resultFilter.value || undefined
    }
    
    const response = await ExecutionService.getResults(route.params.id as string, params)
    resultList.value = response.data.items
    resultsPagination.total = response.data.total
  } catch (error) {
    ElMessage.error('获取执行结果失败')
    console.error(error)
  } finally {
    resultsLoading.value = false
  }
}

// 获取性能统计
const fetchMetrics = async () => {
  try {
    const response = await ExecutionService.getMetrics(route.params.id as string)
    metrics.value = response.data
    if (response.data.timeline) {
      renderTimelineChart(response.data.timeline)
    }
  } catch (error) {
    ElMessage.error('获取性能统计失败')
    console.error(error)
  }
}

// 渲染时间线图表
const renderTimelineChart = (data: any[] | undefined) => {
  if (!timelineChartRef.value || !data) return
  
  if (!timelineChart) {
    timelineChart = echarts.init(timelineChartRef.value)
  }
  
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: data.map(item => item.time)
    },
    yAxis: {
      type: 'value',
      name: '响应时间(ms)'
    },
    series: [{
      data: data.map(item => item.responseTime),
      type: 'line',
      smooth: true
    }]
  }
  
  timelineChart.setOption(option)
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
const downloadLogs = () => {
  ElMessage.info('下载日志功能待实现')
}

const refreshLogs = async () => {
  try {
    const response = await ExecutionService.getLogs(route.params.id as string)
    logContent.value = response.data.logs
    ElMessage.success('日志刷新成功')
  } catch (error) {
    ElMessage.error('刷新日志失败')
    console.error(error)
  }
}

const exportResults = () => {
  ElMessage.info('导出结果功能待实现')
}

const viewResultDetail = (row: ExecutionResult) => {
  currentResult.value = row
  resultDetailDialogVisible.value = true
}

const handleResultDetailDialogClose = () => {
  resultDetailDialogVisible.value = false
}

const handleResultsSizeChange = (val: number) => {
  resultsPagination.pageSize = val
  resultsPagination.currentPage = 1
  fetchExecutionResults()
}

const handleResultsCurrentChange = (val: number) => {
  resultsPagination.currentPage = val
  fetchExecutionResults()
}

// 监听结果过滤变化
watch(resultFilter, () => {
  resultsPagination.currentPage = 1
  fetchExecutionResults()
})

// 监听标签页变化
watch(activeTab, (newTab) => {
  if (newTab === 'results') {
    fetchExecutionResults()
  } else if (newTab === 'metrics') {
    fetchMetrics()
  }
})

// 初始化
onMounted(() => {
  fetchExecutionDetail()
})
</script>

<style scoped>
.execution-detail {
  padding: 20px;
}

.breadcrumb-card {
  margin-bottom: 20px;
}

.info-card {
  margin-bottom: 20px;
}

.error-section {
  margin-top: 20px;
}

.tabs-card {
  margin-bottom: 20px;
}

.log-container {
  padding: 20px;
}

.log-actions {
  margin-bottom: 20px;
  text-align: right;
}

.log-content {
  background-color: #f5f5f5;
  padding: 15px;
  border-radius: 4px;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.5;
  max-height: 500px;
  overflow-y: auto;
}

.results-container {
  padding: 20px 0;
}

.results-actions {
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.metrics-container {
  padding: 20px 0;
}

.metric-card {
  text-align: center;
}

.metric-value {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
}

.metric-label {
  font-size: 14px;
  color: #606266;
  margin-top: 10px;
}

.chart-card {
  margin-top: 20px;
}

.chart-container {
  width: 100%;
  height: 400px;
}
</style>