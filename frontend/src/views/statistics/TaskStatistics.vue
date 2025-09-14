<template>
  <div class="task-statistics">
    <el-row :gutter="20" class="summary-cards">
      <el-col :span="6">
        <el-card class="summary-card">
          <div class="summary-content">
            <div class="summary-icon" :style="{ backgroundColor: '#409eff' }">
              <el-icon><Collection /></el-icon>
            </div>
            <div class="summary-info">
              <div class="summary-value">{{ summary.totalTasks }}</div>
              <div class="summary-label">总任务数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="summary-card">
          <div class="summary-content">
            <div class="summary-icon" :style="{ backgroundColor: '#67c23a' }">
              <el-icon><Check /></el-icon>
            </div>
            <div class="summary-info">
              <div class="summary-value">{{ summary.completedTasks }}</div>
              <div class="summary-label">已完成</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="summary-card">
          <div class="summary-content">
            <div class="summary-icon" :style="{ backgroundColor: '#e6a23c' }">
              <el-icon><Clock /></el-icon>
            </div>
            <div class="summary-info">
              <div class="summary-value">{{ summary.runningTasks }}</div>
              <div class="summary-label">运行中</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="summary-card">
          <div class="summary-content">
            <div class="summary-icon" :style="{ backgroundColor: '#f56c6c' }">
              <el-icon><Warning /></el-icon>
            </div>
            <div class="summary-info">
              <div class="summary-value">{{ summary.failedTasks }}</div>
              <div class="summary-label">失败</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-card class="chart-card">
      <template #header>
        <div class="card-header">
          <span>任务执行趋势</span>
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            @change="fetchTrendData"
          />
        </div>
      </template>
      
      <div ref="trendChartRef" class="chart-container"></div>
    </el-card>
    
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>任务状态分布</span>
            </div>
          </template>
          
          <div ref="statusChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>项目任务分布</span>
            </div>
          </template>
          
          <div ref="projectChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-card class="table-card">
      <template #header>
        <div class="card-header">
          <span>最近执行记录</span>
          <el-button @click="refreshExecutions">刷新</el-button>
        </div>
      </template>
      
      <el-table
        :data="recentExecutions"
        v-loading="loading"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="id" label="执行ID" width="100" />
        <el-table-column prop="taskName" label="任务名称" min-width="150" />
        <el-table-column prop="projectName" label="所属项目" min-width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="startTime" label="开始时间" width="180" />
        <el-table-column prop="duration" label="执行时长" width="120" />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import { Collection, Check, Clock, Warning } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { StatisticsService } from '@/services/statistics'
import { Execution } from '@/types/execution'

// 数据状态
const loading = ref(false)
const dateRange = ref<[string, string]>([
  new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
  new Date().toISOString().split('T')[0]
])

// 图表引用
const trendChartRef = ref<HTMLDivElement | null>(null)
const statusChartRef = ref<HTMLDivElement | null>(null)
const projectChartRef = ref<HTMLDivElement | null>(null)
let trendChart: echarts.ECharts | null = null
let statusChart: echarts.ECharts | null = null
let projectChart: echarts.ECharts | null = null

// 汇总数据
const summary = ref({
  totalTasks: 0,
  completedTasks: 0,
  runningTasks: 0,
  failedTasks: 0
})

// 最近执行记录
const recentExecutions = ref<Execution[]>([])

// 获取汇总数据
const fetchSummary = async () => {
  try {
    const response = await StatisticsService.getSummary()
    summary.value = response.data
  } catch (error) {
    ElMessage.error('获取汇总数据失败')
    console.error(error)
  }
}

// 获取趋势数据
const fetchTrendData = async () => {
  try {
    const params = {
      startDate: dateRange.value[0],
      endDate: dateRange.value[1]
    }
    
    const response = await StatisticsService.getTrend(params)
    renderTrendChart(response.data)
  } catch (error) {
    ElMessage.error('获取趋势数据失败')
    console.error(error)
  }
}

// 获取状态分布数据
const fetchStatusDistribution = async () => {
  try {
    const response = await StatisticsService.getStatusDistribution()
    renderStatusChart(response.data)
  } catch (error) {
    ElMessage.error('获取状态分布数据失败')
    console.error(error)
  }
}

// 获取项目分布数据
const fetchProjectDistribution = async () => {
  try {
    const response = await StatisticsService.getProjectDistribution()
    renderProjectChart(response.data)
  } catch (error) {
    ElMessage.error('获取项目分布数据失败')
    console.error(error)
  }
}

// 获取最近执行记录
const fetchRecentExecutions = async () => {
  loading.value = true
  try {
    const response = await StatisticsService.getRecentExecutions({ limit: 10 })
    recentExecutions.value = response.data
  } catch (error) {
    ElMessage.error('获取执行记录失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 渲染趋势图表
const renderTrendChart = (data: any[]) => {
  if (!trendChartRef.value) return
  
  if (!trendChart) {
    trendChart = echarts.init(trendChartRef.value)
  }
  
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['成功', '失败', '运行中']
    },
    xAxis: {
      type: 'category',
      data: data.map(item => item.date)
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '成功',
        type: 'line',
        stack: '总量',
        data: data.map(item => item.success),
        itemStyle: { color: '#67c23a' }
      },
      {
        name: '失败',
        type: 'line',
        stack: '总量',
        data: data.map(item => item.failed),
        itemStyle: { color: '#f56c6c' }
      },
      {
        name: '运行中',
        type: 'line',
        stack: '总量',
        data: data.map(item => item.running),
        itemStyle: { color: '#e6a23c' }
      }
    ]
  }
  
  trendChart.setOption(option)
}

// 渲染状态分布图表
const renderStatusChart = (data: any[]) => {
  if (!statusChartRef.value) return
  
  if (!statusChart) {
    statusChart = echarts.init(statusChartRef.value)
  }
  
  const option = {
    tooltip: {
      trigger: 'item'
    },
    legend: {
      top: '5%',
      left: 'center'
    },
    series: [
      {
        name: '任务状态',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: '18',
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: data.map(item => ({
          name: getStatusText(item.status),
          value: item.count,
          itemStyle: { color: getStatusColor(item.status) }
        }))
      }
    ]
  }
  
  statusChart.setOption(option)
}

// 渲染项目分布图表
const renderProjectChart = (data: any[]) => {
  if (!projectChartRef.value) return
  
  if (!projectChart) {
    projectChart = echarts.init(projectChartRef.value)
  }
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    xAxis: {
      type: 'category',
      data: data.map(item => item.projectName)
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '任务数',
        type: 'bar',
        barWidth: '60%',
        data: data.map(item => item.count),
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#83bff6' },
            { offset: 0.5, color: '#188df0' },
            { offset: 1, color: '#188df0' }
          ])
        },
        emphasis: {
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#2378f7' },
              { offset: 0.7, color: '#2378f7' },
              { offset: 1, color: '#83bff6' }
            ])
          }
        }
      }
    ]
  }
  
  projectChart.setOption(option)
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

const getStatusColor = (status: string) => {
  switch (status) {
    case 'success': return '#67c23a'
    case 'failed': return '#f56c6c'
    case 'running': return '#e6a23c'
    default: return '#909399'
  }
}

// 操作处理
const refreshExecutions = () => {
  fetchRecentExecutions()
}

const viewDetail = (row: Execution) => {
  // 跳转到执行详情页
  window.open(`/#/executions/${row.id}`, '_blank')
}

// 窗口大小变化时重绘图表
const handleResize = () => {
  if (trendChart) trendChart.resize()
  if (statusChart) statusChart.resize()
  if (projectChart) projectChart.resize()
}

// 初始化
onMounted(() => {
  fetchSummary()
  fetchTrendData()
  fetchStatusDistribution()
  fetchProjectDistribution()
  fetchRecentExecutions()
  
  window.addEventListener('resize', handleResize)
})

// 清理
onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  if (trendChart) trendChart.dispose()
  if (statusChart) statusChart.dispose()
  if (projectChart) projectChart.dispose()
})
</script>

<style scoped>
.task-statistics {
  padding: 20px;
}

.summary-cards {
  margin-bottom: 20px;
}

.summary-card {
  height: 120px;
}

.summary-content {
  display: flex;
  align-items: center;
  height: 100%;
}

.summary-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20px;
}

.summary-icon .el-icon {
  font-size: 30px;
  color: white;
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
  color: #606266;
}

.chart-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  width: 100%;
  height: 400px;
}

.table-card {
  margin-bottom: 20px;
}
</style>