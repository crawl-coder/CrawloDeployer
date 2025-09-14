<template>
  <div class="project-detail" v-loading="projectStore.loading">
    <el-page-header @back="goBack">
      <template #content>
        <span class="page-title">{{ projectStore.currentProject?.name || '项目详情' }}</span>
      </template>
    </el-page-header>
    
    <div v-if="projectStore.currentProject" class="content">
      <!-- 项目基本信息 -->
      <el-card class="info-card">
        <template #header>
          <div class="card-header">
            <span>基本信息</span>
            <el-button type="primary" @click="handleEditProject">编辑</el-button>
          </div>
        </template>
        
        <el-descriptions :column="2" border>
          <el-descriptions-item label="项目名称">
            {{ projectStore.currentProject.name }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusTagType(projectStore.currentProject.status)">
              {{ getStatusText(projectStore.currentProject.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="版本">
            {{ projectStore.currentProject.version }}
          </el-descriptions-item>
          <el-descriptions-item label="入口文件">
            {{ projectStore.currentProject.entrypoint }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间" :span="2">
            {{ formatDate(projectStore.currentProject.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="描述" :span="2">
            {{ projectStore.currentProject.description || '-' }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>
      
      <!-- Git凭证管理 -->
      <el-card class="git-card">
        <template #header>
          <div class="card-header">
            <span>Git凭证管理</span>
            <el-button type="primary" @click="goToGitCredentials">管理Git凭证</el-button>
          </div>
        </template>
        
        <el-alert
          title="提示"
          description="在创建Git项目时，系统将使用您配置的Git凭证进行身份验证。请确保已正确配置凭证。"
          type="info"
          show-icon
        />
      </el-card>
      
      <!-- 环境变量配置 -->
      <el-card class="env-card">
        <template #header>
          <div class="card-header">
            <span>环境变量</span>
            <el-button type="primary" @click="handleEditEnvVars">编辑环境变量</el-button>
          </div>
        </template>
        
        <el-table
          :data="envVarsList"
          style="width: 100%"
          empty-text="暂无环境变量"
        >
          <el-table-column prop="key" label="变量名" width="200" />
          <el-table-column prop="value" label="变量值" />
        </el-table>
      </el-card>
      
      <!-- 项目任务 -->
      <el-card class="tasks-card">
        <template #header>
          <div class="card-header">
            <span>项目任务</span>
            <el-button type="primary" @click="handleCreateTask">
              <el-icon><Plus /></el-icon>
              创建任务
            </el-button>
          </div>
        </template>
        
        <el-table
          :data="projectTasks"
          style="width: 100%"
          v-loading="tasksLoading"
        >
          <el-table-column prop="name" label="任务名称" min-width="150">
            <template #default="{ row }">
              <el-link type="primary" @click="goToTaskDetail(row.id)">
                {{ row.name }}
              </el-link>
            </template>
          </el-table-column>
          <el-table-column prop="spider_name" label="爬虫名称" width="150" />
          <el-table-column prop="cron_expression" label="调度表达式" width="150" />
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
      </el-card>
    </div>
    
    <!-- 编辑项目对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑项目"
      width="600px"
      @close="handleEditDialogClose"
    >
      <el-form
        ref="editFormRef"
        :model="editForm"
        :rules="editRules"
        label-width="100px"
      >
        <el-form-item label="项目名称" prop="name">
          <el-input v-model="editForm.name" placeholder="请输入项目名称" />
        </el-form-item>
        
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="editForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入项目描述"
          />
        </el-form-item>
        
        <el-form-item label="状态" prop="status">
          <el-select v-model="editForm.status" placeholder="请选择状态">
            <el-option label="开发中" value="DEVELOPING" />
            <el-option label="上线" value="ONLINE" />
            <el-option label="下线" value="OFFLINE" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="版本" prop="version">
          <el-input v-model="editForm.version" placeholder="请输入版本号" />
        </el-form-item>
        
        <el-form-item label="入口文件" prop="entrypoint">
          <el-input v-model="editForm.entrypoint" placeholder="请输入入口文件名" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button
            type="primary"
            :loading="projectStore.loading"
            @click="handleSaveProject"
          >
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 编辑环境变量对话框 -->
    <el-dialog
      v-model="envDialogVisible"
      title="编辑环境变量"
      width="600px"
      @close="handleEnvDialogClose"
    >
      <el-table :data="envVarsEditList" style="width: 100%">
        <el-table-column label="变量名" width="200">
          <template #default="{ row }">
            <el-input v-model="row.key" placeholder="变量名" />
          </template>
        </el-table-column>
        <el-table-column label="变量值">
          <template #default="{ row }">
            <el-input v-model="row.value" placeholder="变量值" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80">
          <template #default="{ $index }">
            <el-button
              type="danger"
              link
              @click="removeEnvVar($index)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div style="margin-top: 15px;">
        <el-button @click="addEnvVar">添加变量</el-button>
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="envDialogVisible = false">取消</el-button>
          <el-button
            type="primary"
            :loading="projectStore.loading"
            @click="handleSaveEnvVars"
          >
            确定
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
import { Plus } from '@element-plus/icons-vue'
import { useProjectStore } from '@/store/project'
import type { ProjectUpdate } from '@/types/project'
import type { FormInstance, FormRules } from 'element-plus'

// 路由
const route = useRoute()
const router = useRouter()

// Store
const projectStore = useProjectStore()

// 响应式数据
const tasksLoading = ref(false)
const projectTasks = ref<any[]>([])

const editDialogVisible = ref(false)
const envDialogVisible = ref(false)

// 表单引用
const editFormRef = ref<FormInstance>()

// 编辑表单数据
const editForm = reactive({
  name: '',
  description: '',
  status: 'DEVELOPING' as 'DEVELOPING' | 'ONLINE' | 'OFFLINE',
  version: '',
  entrypoint: ''
})

// 表单验证规则
const editRules = reactive<FormRules>({
  name: [
    { required: true, message: '请输入项目名称', trigger: 'blur' }
  ],
  status: [
    { required: true, message: '请选择项目状态', trigger: 'change' }
  ],
  version: [
    { required: true, message: '请输入版本号', trigger: 'blur' }
  ],
  entrypoint: [
    { required: true, message: '请输入入口文件名', trigger: 'blur' }
  ]
})

// 环境变量编辑列表
const envVarsEditList = ref<Array<{ key: string; value: string }>>([])

// 计算属性
const envVarsList = computed(() => {
  const envTemplate = projectStore.currentProject?.env_template
  if (!envTemplate) return []
  
  return Object.entries(envTemplate).map(([key, value]) => ({
    key,
    value
  }))
})

// 方法
const goBack = () => {
  router.push('/projects')
}

const getStatusTagType = (status: string) => {
  switch (status) {
    case 'ONLINE':
      return 'success'
    case 'OFFLINE':
      return 'danger'
    case 'DEVELOPING':
    default:
      return 'warning'
  }
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'ONLINE':
      return '上线'
    case 'OFFLINE':
      return '下线'
    case 'DEVELOPING':
    default:
      return '开发中'
  }
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

const handleEditProject = () => {
  if (projectStore.currentProject) {
    editForm.name = projectStore.currentProject.name
    editForm.description = projectStore.currentProject.description
    editForm.status = projectStore.currentProject.status
    editForm.version = projectStore.currentProject.version
    editForm.entrypoint = projectStore.currentProject.entrypoint
    editDialogVisible.value = true
  }
}

const handleEditEnvVars = () => {
  const envTemplate = projectStore.currentProject?.env_template || {}
  envVarsEditList.value = Object.entries(envTemplate).map(([key, value]) => ({
    key,
    value
  }))
  envDialogVisible.value = true
}

const goToGitCredentials = () => {
  router.push('/git-credentials')
}

const handleCreateTask = () => {
  // 跳转到创建任务页面，传递项目ID
  router.push(`/tasks?projectId=${route.params.id}`)
}

const handleEditTask = (task: any) => {
  // 跳转到编辑任务页面
  router.push(`/tasks/${task.id}`)
}

const handleRunTask = (task: any) => {
  // 立即执行任务
  ElMessage.info(`立即执行任务: ${task.name}`)
}

const handleDeleteTask = (id: number) => {
  // 删除任务
  ElMessage.info(`删除任务 ID: ${id}`)
}

const toggleTaskStatus = (task: any) => {
  // 切换任务状态
  ElMessage.info(`切换任务状态: ${task.name}`)
}

const goToTaskDetail = (id: number) => {
  // 跳转到任务详情
  router.push(`/tasks/${id}`)
}

const handleSaveProject = async () => {
  if (!editFormRef.value || !projectStore.currentProject) return
  
  await editFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        const projectData: ProjectUpdate = {
          name: editForm.name,
          description: editForm.description,
          status: editForm.status,
          version: editForm.version,
          entrypoint: editForm.entrypoint
        }
        
        const result = await projectStore.updateExistingProject(
          projectStore.currentProject!.id,
          projectData
        )
        
        if (result.success) {
          ElMessage.success('更新成功')
          editDialogVisible.value = false
        } else {
          ElMessage.error(result.message || '更新失败')
        }
      } catch (error) {
        ElMessage.error('更新失败')
      }
    }
  })
}

const handleEditDialogClose = () => {
  if (editFormRef.value) {
    editFormRef.value.resetFields()
  }
}

const addEnvVar = () => {
  envVarsEditList.value.push({ key: '', value: '' })
}

const removeEnvVar = (index: number) => {
  envVarsEditList.value.splice(index, 1)
}

const handleSaveEnvVars = async () => {
  if (!projectStore.currentProject) return
  
  try {
    // 转换为对象格式
    const envVars: Record<string, string> = {}
    envVarsEditList.value.forEach(item => {
      if (item.key) {
        envVars[item.key] = item.value
      }
    })
    
    const result = await projectStore.updateProjectEnvVarsAction(
      projectStore.currentProject.id,
      envVars
    )
    
    if (result.success) {
      ElMessage.success('环境变量更新成功')
      envDialogVisible.value = false
    } else {
      ElMessage.error(result.message || '环境变量更新失败')
    }
  } catch (error) {
    ElMessage.error('环境变量更新失败')
  }
}

const handleEnvDialogClose = () => {
  envVarsEditList.value = []
}

// 获取项目详情
const fetchProjectDetail = async (id: number) => {
  await projectStore.fetchProject(id)
}

// 获取项目任务
const fetchProjectTasks = async (projectId: number) => {
  tasksLoading.value = true
  try {
    // 模拟获取任务数据
    projectTasks.value = [
      {
        id: 1,
        name: '电商网站爬虫',
        spider_name: 'ecommerce_spider',
        cron_expression: '0 0 * * *',
        is_enabled: true,
        last_run_time: '2023-12-01T10:30:25'
      },
      {
        id: 2,
        name: '新闻网站采集',
        spider_name: 'news_spider',
        cron_expression: '*/30 * * * *',
        is_enabled: false,
        last_run_time: null
      }
    ]
    console.log(`获取项目 ${projectId} 的任务列表`)
  } catch (error) {
    ElMessage.error('获取任务列表失败')
  } finally {
    tasksLoading.value = false
  }
}

// 生命周期
onMounted(async () => {
  const projectId = Number(route.params.id)
  if (projectId) {
    await fetchProjectDetail(projectId)
    await fetchProjectTasks(projectId)
  }
})

// 监听路由变化
watch(
  () => route.params.id,
  async (newId) => {
    if (newId) {
      const projectId = Number(newId)
      await fetchProjectDetail(projectId)
      await fetchProjectTasks(projectId)
    }
  }
)
</script>

<style scoped>
.project-detail {
  padding: 20px;
}

.page-title {
  font-size: 18px;
  font-weight: bold;
}

.content {
  margin-top: 20px;
}

.info-card,
.env-card,
.git-card,
.tasks-card {
  margin-bottom: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>