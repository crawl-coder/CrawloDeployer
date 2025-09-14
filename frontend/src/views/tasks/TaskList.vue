<template>
  <div class="task-list">
    <el-card class="search-card">
      <el-row :gutter="20">
        <el-col :span="18">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索任务名称或爬虫名称"
            clearable
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :span="6">
          <el-button type="primary" @click="handleCreateTask">
            <el-icon><Plus /></el-icon>
            创建任务
          </el-button>
        </el-col>
      </el-row>
    </el-card>
    
    <el-card class="tasks-card">
      <template #header>
        <div class="card-header">
          <span>任务列表</span>
          <div class="header-actions">
            <el-button link @click="handleRefresh">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>
      
      <el-table
        :data="filteredTasks"
        v-loading="taskStore.loading"
        style="width: 100%"
        row-key="id"
      >
        <el-table-column prop="name" label="任务名称" min-width="150">
          <template #default="{ row }">
            <el-link type="primary" @click="goToTaskDetail(row.id)">
              {{ row.name }}
            </el-link>
          </template>
        </el-table-column>
        <el-table-column prop="project_name" label="所属项目" width="150" />
        <el-table-column prop="spider_name" label="爬虫名称" width="150" />
        <el-table-column prop="cron_expression" label="调度表达式" width="150" />
        <el-table-column prop="priority" label="优先级" width="100">
          <template #default="{ row }">
            <el-tag :type="getPriorityTagType(row.priority)">
              {{ getPriorityText(row.priority) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_enabled" label="状态" width="100">
          <template #default="{ row }">
            <el-switch
              v-model="row.is_enabled"
              @change="toggleTaskStatus(row)"
            />
          </template>
        </el-table-column>
        <el-table-column prop="last_run_time" label="最后执行" width="180">
          <template #default="{ row }">
            {{ row.last_run_time ? formatDate(row.last_run_time) : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button link @click="handleRunTask(row)">立即执行</el-button>
            <el-button link @click="handleEditTask(row)">编辑</el-button>
            <el-popconfirm
              title="确定要删除这个任务吗？"
              @confirm="handleDeleteTask(row.id)"
            >
              <template #reference>
                <el-button link type="danger">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="taskStore.taskCount"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
    
    <!-- 创建/编辑任务对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="800px"
      @close="handleDialogClose"
    >
      <el-form
        ref="taskFormRef"
        :model="taskForm"
        :rules="taskRules"
        label-width="120px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="任务名称" prop="name">
              <el-input v-model="taskForm.name" placeholder="请输入任务名称" />
            </el-form-item>
          </el-col>
          
          <el-col :span="12">
            <el-form-item label="所属项目" prop="project_id">
              <el-select
                v-model="taskForm.project_id"
                placeholder="请选择项目"
                style="width: 100%"
              >
                <el-option
                  v-for="project in projectStore.projects"
                  :key="project.id"
                  :label="project.name"
                  :value="project.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="爬虫名称" prop="spider_name">
              <el-input v-model="taskForm.spider_name" placeholder="请输入爬虫名称" />
            </el-form-item>
          </el-col>
          
          <el-col :span="12">
            <el-form-item label="优先级" prop="priority">
              <el-select v-model="taskForm.priority" placeholder="请选择优先级" style="width: 100%">
                <el-option label="低" value="LOW" />
                <el-option label="中" value="MEDIUM" />
                <el-option label="高" value="HIGH" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="调度表达式" prop="cron_expression">
              <el-input
                v-model="taskForm.cron_expression"
                placeholder="如: 0 0 * * * (每天凌晨执行)"
              >
                <template #append>
                  <el-button @click="showCronDialog = true">生成器</el-button>
                </template>
              </el-input>
            </el-form-item>
          </el-col>
          
          <el-col :span="12">
            <el-form-item label="超时时间(秒)" prop="timeout_seconds">
              <el-input-number
                v-model="taskForm.timeout_seconds"
                :min="0"
                placeholder="超时时间"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="最大重试次数" prop="max_retries">
              <el-input-number
                v-model="taskForm.max_retries"
                :min="0"
                placeholder="重试次数"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          
          <el-col :span="12">
            <el-form-item label="入口文件" prop="entrypoint">
              <el-input v-model="taskForm.entrypoint" placeholder="如: run.py" />
            </el-form-item>
          </el-col>
          
          <el-col :span="12">
            <el-form-item label="执行器类型">
              <el-select v-model="taskForm.executorType" placeholder="选择执行器类型" style="width: 100%">
                <el-option label="通用脚本" value="generic" />
                <el-option label="Crawlo爬虫" value="crawlo" />
                <el-option label="Scrapy爬虫" value="scrapy" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <!-- Crawlo特定选项 -->
        <div v-if="taskForm.executorType === 'crawlo'">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="爬虫名称">
                <el-input v-model="taskForm.crawloSpiderName" placeholder="如: myspider 或 all" />
              </el-form-item>
            </el-col>
            
            <el-col :span="12">
              <el-form-item label="输出格式">
                <el-checkbox v-model="taskForm.crawloJsonOutput">JSON输出</el-checkbox>
                <el-checkbox v-model="taskForm.crawloNoStats">无统计信息</el-checkbox>
              </el-form-item>
            </el-col>
          </el-row>
        </div>
        
        <!-- Scrapy特定选项 -->
        <div v-if="taskForm.executorType === 'scrapy'">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="爬虫名称">
                <el-input v-model="taskForm.scrapySpiderName" placeholder="如: myspider" />
              </el-form-item>
            </el-col>
            
            <el-col :span="12">
              <el-form-item label="输出设置">
                <el-input v-model="taskForm.scrapyOutputFile" placeholder="输出文件名" />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="输出格式">
                <el-select v-model="taskForm.scrapyOutputFormat" placeholder="选择输出格式" style="width: 100%">
                  <el-option label="JSON" value="json" />
                  <el-option label="CSV" value="csv" />
                  <el-option label="XML" value="xml" />
                  <el-option label="默认" value="" />
                </el-select>
              </el-form-item>
            </el-col>
            
            <el-col :span="12">
              <el-form-item label="日志设置">
                <el-checkbox v-model="taskForm.scrapyNoLog">禁用日志</el-checkbox>
              </el-form-item>
            </el-col>
          </el-row>
        </div>
        
        <el-form-item label="执行参数">
          <el-input
            v-model="taskForm.args"
            type="textarea"
            :rows="3"
            placeholder='JSON格式，如: {"key": "value"}'
          />
        </el-form-item>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="失败时通知">
              <el-switch v-model="taskForm.notify_on_failure" />
            </el-form-item>
          </el-col>
          
          <el-col :span="12">
            <el-form-item label="成功时通知">
              <el-switch v-model="taskForm.notify_on_success" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="通知邮箱">
          <el-input
            v-model="taskForm.notification_emails"
            placeholder="多个邮箱用逗号分隔"
          />
        </el-form-item>
        
        <!-- 节点绑定设置 -->
        <el-divider content-position="left">节点绑定设置</el-divider>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="分发模式">
              <el-select v-model="taskForm.distribution_mode" placeholder="选择分发模式" style="width: 100%">
                <el-option label="任意节点" value="ANY" />
                <el-option label="指定单个节点" value="SPECIFIC" />
                <el-option label="指定多个节点" value="MULTIPLE" />
                <el-option label="基于标签分发" value="TAG_BASED" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <!-- 指定单个节点 -->
        <el-row v-if="taskForm.distribution_mode === 'SPECIFIC'" :gutter="20">
          <el-col :span="12">
            <el-form-item label="目标节点">
              <el-select
                v-model="taskForm.target_node_id"
                placeholder="请选择目标节点"
                style="width: 100%"
              >
                <el-option
                  v-for="node in nodeStore.nodes"
                  :key="node.id"
                  :label="`${node.hostname} (${node.ip_address})`"
                  :value="node.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <!-- 指定多个节点 -->
        <el-row v-if="taskForm.distribution_mode === 'MULTIPLE'" :gutter="20">
          <el-col :span="12">
            <el-form-item label="目标节点">
              <el-select
                v-model="taskForm.target_node_ids"
                multiple
                placeholder="请选择目标节点"
                style="width: 100%"
              >
                <el-option
                  v-for="node in nodeStore.nodes"
                  :key="node.id"
                  :label="`${node.hostname} (${node.ip_address})`"
                  :value="node.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <!-- 基于标签分发 -->
        <el-row v-if="taskForm.distribution_mode === 'TAG_BASED'" :gutter="20">
          <el-col :span="12">
            <el-form-item label="节点标签">
              <el-input
                v-model="taskForm.target_node_tags"
                placeholder="请输入节点标签"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item v-if="dialogMode === 'edit'" label="任务依赖">
          <el-select
            v-model="taskForm.dependency_task_ids"
            multiple
            placeholder="请选择依赖的任务"
            style="width: 100%"
          >
            <el-option
              v-for="task in availableDependencies"
              :key="task.id"
              :label="`${task.name} (${task.project_name})`"
              :value="task.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button
            type="primary"
            :loading="taskStore.loading"
            @click="handleSaveTask"
          >
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- CRON表达式生成器对话框 -->
    <el-dialog
      v-model="showCronDialog"
      title="CRON表达式生成器"
      width="600px"
    >
      <div class="cron-generator">
        <el-row :gutter="10">
          <el-col :span="4">
            <el-form-item label="分钟">
              <el-input v-model="cronForm.minute" placeholder="*" />
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item label="小时">
              <el-input v-model="cronForm.hour" placeholder="*" />
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item label="日">
              <el-input v-model="cronForm.day" placeholder="*" />
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item label="月">
              <el-input v-model="cronForm.month" placeholder="*" />
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item label="星期">
              <el-input v-model="cronForm.week" placeholder="*" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <div class="cron-result">
          <el-input v-model="generatedCron" readonly>
            <template #prepend>生成的表达式:</template>
          </el-input>
        </div>
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showCronDialog = false">取消</el-button>
          <el-button
            type="primary"
            @click="applyCronExpression"
          >
            应用
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Search,
  Plus,
  Refresh
} from '@element-plus/icons-vue'
import { useTaskStore } from '@/store/task'
import { useProjectStore } from '@/store/project'
import { useNodeStore } from '@/store/node'  // 添加节点store
import type { TaskCreate, TaskUpdate } from '@/types/task'
import type { FormInstance, FormRules } from 'element-plus'

// 路由
const route = useRoute()
const router = useRouter()

// Store
const taskStore = useTaskStore()
const projectStore = useProjectStore()
const nodeStore = useNodeStore()  // 添加节点store

// 响应式数据
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(10)

const dialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const dialogTitle = computed(() => dialogMode.value === 'create' ? '创建任务' : '编辑任务')

const showCronDialog = ref(false)

// 表单引用
const taskFormRef = ref<FormInstance>()

// 表单数据
const taskForm = reactive({
  id: 0,
  name: '',
  project_id: undefined as number | undefined,
  spider_name: '',
  cron_expression: '',
  args: '',
  priority: 'MEDIUM' as 'LOW' | 'MEDIUM' | 'HIGH',
  timeout_seconds: 3600,
  max_retries: 0,
  notify_on_failure: true,
  notify_on_success: false,
  notification_emails: '',
  entrypoint: 'run.py',
  dependency_task_ids: [] as number[],
  // 执行器类型
  executorType: 'generic' as 'generic' | 'crawlo' | 'scrapy',
  // Crawlo相关字段
  crawloSpiderName: 'all',
  crawloJsonOutput: false,
  crawloNoStats: false,
  // Scrapy相关字段
  scrapySpiderName: '',
  scrapyOutputFile: '',
  scrapyOutputFormat: '',
  scrapyNoLog: false,
  // 节点绑定相关字段
  distribution_mode: 'ANY' as 'ANY' | 'SPECIFIC' | 'MULTIPLE' | 'TAG_BASED',
  target_node_id: undefined as number | undefined,
  target_node_ids: [] as number[],
  target_node_tags: ''
})

// CRON表达式生成器表单
const cronForm = reactive({
  minute: '*',
  hour: '*',
  day: '*',
  month: '*',
  week: '*'
})

// 表单验证规则
const taskRules = reactive<FormRules>({
  name: [
    { required: true, message: '请输入任务名称', trigger: 'blur' }
  ],
  project_id: [
    { required: true, message: '请选择所属项目', trigger: 'change' }
  ],
  spider_name: [
    { required: true, message: '请输入爬虫名称', trigger: 'blur' }
  ],
  priority: [
    { required: true, message: '请选择优先级', trigger: 'change' }
  ]
})

// 计算属性
const filteredTasks = computed(() => {
  if (!searchKeyword.value) {
    return taskStore.tasks.map(task => ({
      ...task,
      project_name: projectStore.projects.find(p => p.id === task.project_id)?.name || '未知项目'
    }))
  }
  
  const keyword = searchKeyword.value.toLowerCase()
  return taskStore.tasks
    .filter(
      task =>
        task.name.toLowerCase().includes(keyword) ||
        task.spider_name.toLowerCase().includes(keyword)
    )
    .map(task => ({
      ...task,
      project_name: projectStore.projects.find(p => p.id === task.project_id)?.name || '未知项目'
    }))
})

const generatedCron = computed(() => {
  return `${cronForm.minute} ${cronForm.hour} ${cronForm.day} ${cronForm.month} ${cronForm.week}`
})

const availableDependencies = computed(() => {
  // 排除当前任务和已经选择的依赖任务
  return taskStore.tasks
    .filter(task => task.id !== taskForm.id)
    .map(task => ({
      ...task,
      project_name: projectStore.projects.find(p => p.id === task.project_id)?.name || '未知项目'
    }))
})

// 方法
const getPriorityTagType = (priority: string) => {
  switch (priority) {
    case 'HIGH':
      return 'danger'
    case 'LOW':
      return 'success'
    case 'MEDIUM':
    default:
      return 'warning'
  }
}

const getPriorityText = (priority: string) => {
  switch (priority) {
    case 'HIGH':
      return '高'
    case 'LOW':
      return '低'
    case 'MEDIUM':
    default:
      return '中'
  }
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

const handleSearch = () => {
  // 搜索功能可以在这里实现
  // 目前使用前端过滤
}

const handleRefresh = async () => {
  await taskStore.fetchTasks({
    skip: (currentPage.value - 1) * pageSize.value,
    limit: pageSize.value
  })
}

const handleCreateTask = () => {
  dialogMode.value = 'create'
  resetForm()
  
  // 如果URL中有projectId参数，设置为默认项目
  const projectId = route.query.projectId
  if (projectId) {
    taskForm.project_id = Number(projectId)
  }
  
  dialogVisible.value = true
}

const handleEditTask = (task: any) => {
  dialogMode.value = 'edit'
  taskForm.id = task.id
  taskForm.name = task.name
  taskForm.project_id = task.project_id
  taskForm.spider_name = task.spider_name
  taskForm.cron_expression = task.cron_expression || ''
  taskForm.args = task.args ? JSON.stringify(task.args, null, 2) : ''
  taskForm.priority = task.priority
  taskForm.timeout_seconds = task.timeout_seconds || 3600
  taskForm.max_retries = task.max_retries
  taskForm.notify_on_failure = task.notify_on_failure
  taskForm.notify_on_success = task.notify_on_success
  taskForm.notification_emails = task.notification_emails?.join(', ') || ''
  taskForm.dependency_task_ids = task.dependency_task_ids || []
  // 节点绑定相关字段
  taskForm.distribution_mode = task.distribution_mode || 'ANY'
  taskForm.target_node_id = task.target_node_id || undefined
  taskForm.target_node_ids = task.target_node_ids || []
  taskForm.target_node_tags = task.target_node_tags || ''
  
  // 检查是否是Crawlo任务
  if (task.args && task.args.crawlo_command) {
    taskForm.executorType = 'crawlo'
    taskForm.crawloSpiderName = task.args.spider_name || 'all'
    taskForm.crawloJsonOutput = !!task.args.json_output
    taskForm.crawloNoStats = !!task.args.no_stats
  } 
  // 检查是否是Scrapy任务
  else if (task.args && task.args.scrapy_command) {
    taskForm.executorType = 'scrapy'
    taskForm.scrapySpiderName = task.args.spider_name || ''
    taskForm.scrapyOutputFile = task.args.output_file || ''
    taskForm.scrapyOutputFormat = task.args.output_format || ''
    taskForm.scrapyNoLog = !!task.args.no_log
  }
  // 默认为通用脚本
  else {
    taskForm.executorType = 'generic'
    // 重置特定字段
    taskForm.crawloSpiderName = 'all'
    taskForm.crawloJsonOutput = false
    taskForm.crawloNoStats = false
    taskForm.scrapySpiderName = ''
    taskForm.scrapyOutputFile = ''
    taskForm.scrapyOutputFormat = ''
    taskForm.scrapyNoLog = false
  }
  
  dialogVisible.value = true
}

const handleDeleteTask = async (id: number) => {
  try {
    const result = await taskStore.deleteExistingTask(id)
    if (result.success) {
      ElMessage.success('删除成功')
      await handleRefresh()
    } else {
      ElMessage.error(result.message || '删除失败')
    }
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

const handleRunTask = async (task: any) => {
  try {
    const result = await taskStore.runTaskNow(task.id)
    if (result.success) {
      ElMessage.success('任务已提交执行')
    } else {
      ElMessage.error(result.message || '执行任务失败')
    }
  } catch (error) {
    ElMessage.error('执行任务失败')
  }
}

const toggleTaskStatus = async (task: any) => {
  try {
    const result = await taskStore.toggleTaskStatus(task.id, task.is_enabled)
    if (result.success) {
      ElMessage.success('状态更新成功')
    } else {
      ElMessage.error(result.message || '状态更新失败')
      // 恢复开关状态
      task.is_enabled = !task.is_enabled
    }
  } catch (error) {
    ElMessage.error('状态更新失败')
    // 恢复开关状态
    task.is_enabled = !task.is_enabled
  }
}

const handleSaveTask = async () => {
  if (!taskFormRef.value) return
  
  await taskFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        // 解析参数
        let args = null
        if (taskForm.args) {
          try {
            args = JSON.parse(taskForm.args)
          } catch (e) {
            ElMessage.error('参数格式不正确，请输入有效的JSON格式')
            return
          }
        }
        
        // 如果是Crawlo任务，添加Crawlo特定参数
        if (taskForm.executorType === 'crawlo') {
          args = args || {}
          args.crawlo_command = true
          args.spider_name = taskForm.crawloSpiderName || 'all'
          if (taskForm.crawloJsonOutput) {
            args.json_output = true
          }
          if (taskForm.crawloNoStats) {
            args.no_stats = true
          }
        }
        // 如果是Scrapy任务，添加Scrapy特定参数
        else if (taskForm.executorType === 'scrapy') {
          args = args || {}
          args.scrapy_command = true
          args.spider_name = taskForm.scrapySpiderName || 'default'
          if (taskForm.scrapyOutputFile) {
            args.output_file = taskForm.scrapyOutputFile
          }
          if (taskForm.scrapyOutputFormat) {
            args.output_format = taskForm.scrapyOutputFormat
          }
          if (taskForm.scrapyNoLog) {
            args.no_log = true
          }
        }
        
        // 解析通知邮箱
        let emails: string[] | null = null
        if (taskForm.notification_emails) {
          emails = taskForm.notification_emails
            .split(',')
            .map(email => email.trim())
            .filter(email => email)
        }
        
        let result
        if (dialogMode.value === 'create') {
          // 创建任务
          const taskData: TaskCreate = {
            name: taskForm.name,
            project_id: taskForm.project_id!,
            spider_name: taskForm.spider_name,
            cron_expression: taskForm.cron_expression || undefined,
            args,
            priority: taskForm.priority,
            timeout_seconds: taskForm.timeout_seconds || undefined,
            max_retries: taskForm.max_retries,
            notify_on_failure: taskForm.notify_on_failure,
            notify_on_success: taskForm.notify_on_success,
            notification_emails: emails || undefined,
            // 节点绑定相关字段
            distribution_mode: taskForm.distribution_mode,
            target_node_id: taskForm.target_node_id,
            target_node_ids: taskForm.target_node_ids.length > 0 ? taskForm.target_node_ids : undefined,
            target_node_tags: taskForm.target_node_tags || undefined
          }
          
          result = await taskStore.createNewTask(taskData)
        } else {
          // 更新任务
          const taskData: TaskUpdate = {
            name: taskForm.name,
            project_id: taskForm.project_id,
            spider_name: taskForm.spider_name,
            cron_expression: taskForm.cron_expression || null,
            args: args || null,
            priority: taskForm.priority,
            timeout_seconds: taskForm.timeout_seconds || null,
            max_retries: taskForm.max_retries,
            notify_on_failure: taskForm.notify_on_failure,
            notify_on_success: taskForm.notify_on_success,
            notification_emails: emails || null,
            dependency_task_ids: taskForm.dependency_task_ids,
            // 节点绑定相关字段
            distribution_mode: taskForm.distribution_mode,
            target_node_id: taskForm.target_node_id,
            target_node_ids: taskForm.target_node_ids.length > 0 ? taskForm.target_node_ids : null,
            target_node_tags: taskForm.target_node_tags || null
          }
          
          result = await taskStore.updateExistingTask(taskForm.id, taskData)
        }
        
        if (result.success) {
          ElMessage.success(dialogMode.value === 'create' ? '创建成功' : '更新成功')
          dialogVisible.value = false
          await handleRefresh()
        } else {
          ElMessage.error(result.message || (dialogMode.value === 'create' ? '创建失败' : '更新失败'))
        }
      } catch (error) {
        ElMessage.error(dialogMode.value === 'create' ? '创建失败' : '更新失败')
      }
    }
  })
}

const handleDialogClose = () => {
  resetForm()
}

const resetForm = () => {
  taskForm.id = 0
  taskForm.name = ''
  taskForm.project_id = undefined
  taskForm.spider_name = ''
  taskForm.cron_expression = ''
  taskForm.args = ''
  taskForm.priority = 'MEDIUM'
  taskForm.timeout_seconds = 3600
  taskForm.max_retries = 0
  taskForm.notify_on_failure = true
  taskForm.notify_on_success = false
  taskForm.notification_emails = ''
  taskForm.dependency_task_ids = []
  // 执行器类型
  taskForm.executorType = 'generic'
  // Crawlo相关字段
  taskForm.crawloSpiderName = 'all'
  taskForm.crawloJsonOutput = false
  taskForm.crawloNoStats = false
  // Scrapy相关字段
  taskForm.scrapySpiderName = ''
  taskForm.scrapyOutputFile = ''
  taskForm.scrapyOutputFormat = ''
  taskForm.scrapyNoLog = false
  // 节点绑定相关字段
  taskForm.distribution_mode = 'ANY'
  taskForm.target_node_id = undefined
  taskForm.target_node_ids = []
  taskForm.target_node_tags = ''
  
  if (taskFormRef.value) {
    taskFormRef.value.resetFields()
  }
}

const goToTaskDetail = (id: number) => {
  router.push(`/tasks/${id}`)
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  handleRefresh()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  handleRefresh()
}

const applyCronExpression = () => {
  taskForm.cron_expression = generatedCron.value
  showCronDialog.value = false
}

// 生命周期
onMounted(async () => {
  // 获取项目列表
  await projectStore.fetchProjects()
  
  // 获取节点列表
  await nodeStore.fetchNodes()
  
  // 获取任务列表
  await taskStore.fetchTasks({
    skip: 0,
    limit: pageSize.value
  })
})

// 监听分页变化
watch([currentPage, pageSize], async () => {
  await taskStore.fetchTasks({
    skip: (currentPage.value - 1) * pageSize.value,
    limit: pageSize.value
  })
})
</script>

<style scoped>
.task-list {
  padding: 20px;
}

.search-card {
  margin-bottom: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.tasks-card {
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

.cron-generator {
  padding: 20px 0;
}

.cron-result {
  margin-top: 20px;
}
</style>