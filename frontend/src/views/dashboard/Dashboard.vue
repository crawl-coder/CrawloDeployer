<template>
  <div class="dashboard">
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon primary">
              <el-icon><Folder /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.projects }}</div>
              <div class="stat-label">项目总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon success">
              <el-icon><Collection /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.tasks }}</div>
              <div class="stat-label">任务总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon warning">
              <el-icon><Monitor /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.nodes }}</div>
              <div class="stat-label">节点总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon info">
              <el-icon><Tickets /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.successRate }}%</div>
              <div class="stat-label">成功率</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" class="charts-row">
      <el-col :span="16">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>最近7天任务执行趋势</span>
            </div>
          </template>
          <div ref="trendChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>节点状态分布</span>
            </div>
          </template>
          <div ref="nodeChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" class="recent-row">
      <el-col :span="24">
        <el-card class="recent-card">
          <template #header>
            <div class="card-header">
              <span>最近执行记录</span>
              <el-button link @click="goToTaskRuns">查看更多</el-button>
            </div>
          </template>
          <el-table :data="recentRuns" style="width: 100%">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="task_name" label="任务名称" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusTagType(row.status)">
                  {{ row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="start_time" label="开始时间" width="180" />
            <el-table-column prop="duration" label="执行时长" width="100" />
            <el-table-column label="操作" width="100">
              <template #default="{ row }">
                <el-button link @click="viewTaskRunDetail(row.id)">查看详情</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Folder, Collection, Monitor, Tickets } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

// 路由
const router = useRouter()

// 响应式数据
const stats = reactive({
  projects: 0,
  tasks: 0,
  nodes: 0,
  successRate: 0
})

const recentRuns = ref<any[]>([])

// 图表引用
const trendChartRef = ref<HTMLDivElement | null>(null)
const nodeChartRef = ref<HTMLDivElement | null>(null)

let trendChart: echarts.ECharts | null = null
let nodeChart: echarts.ECharts | null = null

// 方法
const getStatusTagType = (status: string) => {
  switch (status) {
    case 'SUCCESS':
      return 'success'
    case 'FAILURE':
      return 'danger'
    case 'RUNNING':
      return 'warning'
    default:
      return 'info'
  }
}

const goToTaskRuns = () => {
  router.push('/task-runs')
}

const viewTaskRunDetail = (id: number) => {
  router.push(`/task-runs/${id}`)
}

// 图表初始化
const initCharts = () => {
  if (trendChartRef.value) {
    trendChart = echarts.init(trendChartRef.value)
    trendChart.setOption({
      tooltip: {
        trigger: 'axis'
      },
      xAxis: {
        type: 'category',
        data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
      },
      yAxis: {
        type: 'value'
      },
      series: [
        {
          data: [120, 200, 150, 80, 70, 110, 130],
          type: 'line',
          smooth: true
        }
      ]
    })
  }
  
  if (nodeChartRef.value) {
    nodeChart = echarts.init(nodeChartRef.value)
    nodeChart.setOption({
      tooltip: {
        trigger: 'item'
      },
      legend: {
        top: '5%',
        left: 'center'
      },
      series: [
        {
          name: '节点状态',
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
          data: [
            { value: 10, name: '在线' },
            { value: 2, name: '离线' }
          ]
        }
      ]
    })
  }
}

// 获取统计数据
const fetchStats = async () => {
  try {
    // 模拟数据
    stats.projects = 5
    stats.tasks = 12
    stats.nodes = 3
    stats.successRate = 92.5
    
    // 模拟最近执行记录
    recentRuns.value = [
      {
        id: 1,
        task_name: '电商网站爬虫',
        status: 'SUCCESS',
        start_time: '2023-12-01 10:30:25',
        duration: '5m 23s'
      },
      {
        id: 2,
        task_name: '新闻网站采集',
        status: 'RUNNING',
        start_time: '2023-12-01 11:15:10',
        duration: '2m 45s'
      },
      {
        id: 3,
        task_name: '社交媒体分析',
        status: 'FAILURE',
        start_time: '2023-12-01 09:45:30',
        duration: '3m 12s'
      }
    ]
  } catch (error) {
    ElMessage.error('获取统计数据失败')
  }
}

// 生命周期
onMounted(() => {
  fetchStats()
  initCharts()
  
  // 监听窗口大小变化
  window.addEventListener('resize', () => {
    if (trendChart) {
      trendChart.resize()
    }
    if (nodeChart) {
      nodeChart.resize()
    }
  })
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.stat-content {
  display: flex;
  align-items: center;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20px;
  font-size: 24px;
}

.stat-icon.primary {
  background-color: #ecf5ff;
  color: #409eff;
}

.stat-icon.success {
  background-color: #f0f9ff;
  color: #67c23a;
}

.stat-icon.warning {
  background-color: #fdf6ec;
  color: #e6a23c;
}

.stat-icon.info {
  background-color: #f4f4f5;
  color: #909399;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 5px;
}

.stat-label {
  color: #999;
  font-size: 14px;
}

.charts-row {
  margin-bottom: 20px;
}

.chart-card {
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  height: 300px;
}

.recent-card {
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.recent-card :deep(.el-card__header) {
  border-bottom: 1px solid #ebeef5;
}
</style>