<template>
  <div class="project-detail" v-loading="loading">
    <el-page-header @back="goBack" :content="project?.name" />
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="16">
        <el-card class="project-info-card">
          <template #header>
            <div class="card-header">
              <span>项目信息</span>
              <el-button type="primary" @click="handleEditProject">编辑</el-button>
            </div>
          </template>
          
          <el-descriptions :column="1" border>
            <el-descriptions-item label="项目名称">{{ project?.name }}</el-descriptions-item>
            <el-descriptions-item label="描述">{{ project?.description }}</el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="getStatusTagType(project?.status)">
                {{ getStatusText(project?.status) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="版本">{{ project?.version }}</el-descriptions-item>
            <el-descriptions-item label="入口文件">{{ project?.entrypoint }}</el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ formatDate(project?.created_at) }}</el-descriptions-item>
            <el-descriptions-item label="项目路径">{{ project?.package_path }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
        
        <el-card class="project-files-card" style="margin-top: 20px;">
          <template #header>
            <div class="card-header">
              <span>项目文件</span>
              <el-button @click="refreshFiles">刷新</el-button>
            </div>
          </template>
          
          <el-table :data="projectFiles" style="width: 100%">
            <el-table-column prop="name" label="文件名">
              <template #default="{ row }">
                <el-icon v-if="row.type === 'directory'"><Folder /></el-icon>
                <el-icon v-else><Document /></el-icon>
                {{ row.name }}
              </template>
            </el-table-column>
            <el-table-column prop="size" label="大小" width="120">
              <template #default="{ row }">
                {{ formatFileSize(row.size) }}
              </template>
            </el-table-column>
            <el-table-column prop="modified" label="修改时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.modified) }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card class="project-actions-card">
          <template #header>
            <div class="card-header">
              <span>项目操作</span>
            </div>
          </template>
          
          <div class="action-buttons">
            <el-button type="primary" @click="handleSyncToNodes" style="width: 100%; margin-bottom: 10px;">
              <el-icon><Upload /></el-icon>
              同步到节点
            </el-button>
            
            <el-button @click="handleViewEnvVars" style="width: 100%; margin-bottom: 10px;">
              <el-icon><Setting /></el-icon>
              环境变量
            </el-button>
            
            <el-button @click="handleViewTasks" style="width: 100%; margin-bottom: 10px;">
              <el-icon><List /></el-icon>
              任务管理
            </el-button>
            
            <el-button type="danger" @click="handleDeleteProject" style="width: 100%;">
              <el-icon><Delete /></el-icon>
              删除项目
            </el-button>
          </div>
        </el-card>
        
        <el-card class="project-stats-card" style="margin-top: 20px;">
          <template #header>
            <div class="card-header">
              <span>项目统计</span>
            </div>
          </template>
          
          <div class="stats-content">
            <div class="stat-item">
              <div class="stat-label">任务数</div>
              <div class="stat-value">{{ projectStats?.taskCount || 0 }}</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">执行次数</div>
              <div class="stat-value">{{ projectStats?.runCount || 0 }}</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">成功率</div>
              <div class="stat-value">{{ projectStats?.successRate || 0 }}%</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 同步到节点对话框 -->
    <el-dialog
      v-model="syncDialogVisible"
      title="同步项目到节点"
      width="600px"
    >
      <el-form
        ref="syncFormRef"
        :model="syncForm"
        :rules="syncRules"
        label-width="100px"
      >
        <el-form-item label="选择节点" prop="nodeIds">
          <el-select
            v-model="syncForm.nodeIds"
            multiple
            placeholder="请选择要同步到的节点"
            style="width: 100%"
          >
            <el-option
              v-for="node in onlineNodes"
              :key="node.id"
              :label="`${node.hostname} (${node.ip_address})`"
              :value="node.id"
            />
          </el-select>
        </el-form-item>
        
        <el-alert
          title="项目文件将被同步到选中的节点上，确保节点可以访问主节点的文件系统或网络共享"
          type="info"
          show-icon
        />
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="syncDialogVisible = false">取消</el-button>
          <el-button
            type="primary"
            :loading="syncing"
            @click="handleSyncConfirm"
          >
            确定同步
          </el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 编辑项目对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑项目"
      width="600px"
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
            :loading="updating"
            @click="handleUpdateProject"
          >
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Folder,
  Document,
  Upload,
  Setting,
  List,
  Delete
} from '@element-plus/icons-vue'
import { useProjectStore } from '@/store/project'
import { useNodeStore } from '@/store/node'
import { useTaskStore } from '@/store/task'
import type { ProjectUpdate } from '@/types/project'
import type { FormInstance, FormRules } from 'element-plus'

// 路由
const route = useRoute()
const router = useRouter()

// Store
const projectStore = useProjectStore()
const nodeStore = useNodeStore()
const taskStore = useTaskStore()

// 响应式数据
const loading = ref(false)
const syncing = ref(false)
const updating = ref(false)
const syncDialogVisible = ref(false)
const editDialogVisible = ref(false)

const project = ref<any>(null)
const projectFiles = ref<any[]>([])
const projectStats = ref<any>(null)

// 表单引用
const syncFormRef = ref<FormInstance>()
const editFormRef = ref<FormInstance>()

// 表单数据
const syncForm = reactive({
  nodeIds: [] as number[]
})

const editForm = reactive({
  name: '',
  description: '',
  status: 'DEVELOPING' as 'DEVELOPING' | 'ONLINE' | 'OFFLINE',
  version: '1.0.0',
  entrypoint: 'run.py'
})

// 表单验证规则
const syncRules = reactive<FormRules>({
  nodeIds: [
    { required: true, message: '请选择要同步到的节点', trigger: 'change' }
  ]
})

const editRules = reactive<FormRules>({
  name: [
    { required: true, message: '请输入项目名称', trigger: 'blur' }
  ],
  status: [
    { required: true, message: '请选择状态', trigger: 'change' }
  ],
  version: [
    { required: true, message: '请输入版本号', trigger: 'blur' }
  ],
  entrypoint: [
    { required: true, message: '请输入入口文件名', trigger: 'blur' }
  ]
})

// 计算属性
const onlineNodes = computed(() => nodeStore.onlineNodes)

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

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const fetchProjectDetail = async () => {
  loading.value = true
  try {
    const projectId = Number(route.params.id)
    const result = await projectStore.fetchProjectById(projectId)
    if (result.success) {
      project.value = result.data
      editForm.name = project.value.name
      editForm.description = project.value.description
      editForm.status = project.value.status
      editForm.version = project.value.version
      editForm.entrypoint = project.value.entrypoint
    } else {
      ElMessage.error(result.message || '获取项目详情失败')
    }
  } catch (error) {
    ElMessage.error('获取项目详情失败')
  } finally {
    loading.value = false
  }
}

const refreshFiles = async () => {
  try {
    const projectId = Number(route.params.id)
    const result = await projectStore.getProjectFiles(projectId)
    if (result.success) {
      // 转换文件数据格式
      projectFiles.value = result.data.map((file: string) => ({
        name: file,
        type: file.endsWith('/') ? 'directory' : 'file',
        size: 0, // 实际应用中可以从API获取
        modified: new Date().toISOString() // 实际应用中可以从API获取
      }))
    } else {
      ElMessage.error(result.message || '获取项目文件失败')
    }
  } catch (error) {
    ElMessage.error('获取项目文件失败')
  }
}

const fetchProjectStats = async () => {
  try {
    const projectId = Number(route.params.id)
    const result = await projectStore.getProjectStats(projectId)
    if (result.success) {
      projectStats.value = result.data
    } else {
      ElMessage.error(result.message || '获取项目统计失败')
    }
  } catch (error) {
    ElMessage.error('获取项目统计失败')
  }
}

const handleSyncToNodes = () => {
  syncForm.nodeIds = []
  syncDialogVisible.value = true
}

const handleSyncConfirm = async () => {
  if (!syncFormRef.value) return
  
  await syncFormRef.value.validate(async (valid) => {
    if (valid) {
      syncing.value = true
      try {
        // 获取选中节点的主机名
        const selectedNodes = nodeStore.nodes.filter(node => 
          syncForm.nodeIds.includes(node.id)
        )
        const nodeHostnames = selectedNodes.map(node => node.hostname)
        
        const result = await projectStore.syncProjectToNodes(
          project.value.id,
          nodeHostnames
        )
        
        if (result.success) {
          ElMessage.success('项目同步成功')
          syncDialogVisible.value = false
        } else {
          ElMessage.error(result.message || '项目同步失败')
        }
      } catch (error) {
        ElMessage.error('项目同步失败')
      } finally {
        syncing.value = false
      }
    }
  })
}

const handleEditProject = () => {
  editDialogVisible.value = true
}

const handleUpdateProject = async () => {
  if (!editFormRef.value) return
  
  await editFormRef.value.validate(async (valid) => {
    if (valid) {
      updating.value = true
      try {
        const projectData: ProjectUpdate = {
          name: editForm.name,
          description: editForm.description,
          status: editForm.status,
          version: editForm.version,
          entrypoint: editForm.entrypoint
        }
        
        const result = await projectStore.updateExistingProject(
          project.value.id,
          projectData
        )
        
        if (result.success) {
          ElMessage.success('更新成功')
          editDialogVisible.value = false
          await fetchProjectDetail()
        } else {
          ElMessage.error(result.message || '更新失败')
        }
      } catch (error) {
        ElMessage.error('更新失败')
      } finally {
        updating.value = false
      }
    }
  })
}

const handleViewEnvVars = () => {
  router.push(`/projects/${project.value.id}/env-vars`)
}

const handleViewTasks = () => {
  router.push(`/projects/${project.value.id}/tasks`)
}

const handleDeleteProject = () => {
  ElMessageBox.confirm(
    '确定要删除这个项目吗？此操作不可恢复！',
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      const result = await projectStore.deleteExistingProject(project.value.id)
      if (result.success) {
        ElMessage.success('删除成功')
        router.push('/projects')
      } else {
        ElMessage.error(result.message || '删除失败')
      }
    } catch (error) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {
    // 用户取消删除
  })
}

// 生命周期
onMounted(async () => {
  await fetchProjectDetail()
  await refreshFiles()
  await fetchProjectStats()
  
  // 获取节点列表
  await nodeStore.fetchNodes()
})
</script>

<style scoped>
.project-detail {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.action-buttons {
  display: flex;
  flex-direction: column;
}

.stats-content {
  display: flex;
  justify-content: space-around;
}

.stat-item {
  text-align: center;
}

.stat-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 5px;
}

.stat-value {
  font-size: 20px;
  font-weight: bold;
  color: #303133;
}
</style>