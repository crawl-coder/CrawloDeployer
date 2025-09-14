<template>
  <div class="project-list">
    <el-card class="search-card">
      <el-row :gutter="20">
        <el-col :span="18">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索项目名称或描述"
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
          <el-button type="primary" @click="handleCreateProject">
            <el-icon><Plus /></el-icon>
            创建项目
          </el-button>
        </el-col>
      </el-row>
    </el-card>
    
    <el-card class="projects-card">
      <template #header>
        <div class="card-header">
          <span>项目列表</span>
          <div class="header-actions">
            <el-button link @click="handleRefresh">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>
      
      <el-table
        :data="filteredProjects"
        v-loading="projectStore.loading"
        style="width: 100%"
        row-key="id"
      >
        <el-table-column prop="name" label="项目名称" min-width="150">
          <template #default="{ row }">
            <el-link type="primary" @click="goToProjectDetail(row.id)">
              {{ row.name }}
            </el-link>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="version" label="版本" width="100" />
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button link @click="goToProjectDetail(row.id)">查看</el-button>
            <el-button link @click="handleEditProject(row)">编辑</el-button>
            <el-popconfirm
              title="确定要删除这个项目吗？"
              @confirm="handleDeleteProject(row.id)"
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
          :total="projectStore.projectCount"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
    
    <!-- 创建/编辑项目对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      @close="handleDialogClose"
    >
      <el-form
        ref="projectFormRef"
        :model="projectForm"
        :rules="projectRules"
        label-width="100px"
      >
        <el-form-item label="项目名称" prop="name">
          <el-input v-model="projectForm.name" placeholder="请输入项目名称" />
        </el-form-item>
        
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="projectForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入项目描述"
          />
        </el-form-item>
        
        <el-form-item label="状态" prop="status">
          <el-select v-model="projectForm.status" placeholder="请选择状态">
            <el-option label="开发中" value="DEVELOPING" />
            <el-option label="上线" value="ONLINE" />
            <el-option label="下线" value="OFFLINE" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="版本" prop="version">
          <el-input v-model="projectForm.version" placeholder="请输入版本号" />
        </el-form-item>
        
        <el-form-item label="入口文件" prop="entrypoint">
          <el-input v-model="projectForm.entrypoint" placeholder="请输入入口文件名" />
        </el-form-item>
        
        <template v-if="dialogMode === 'create'">
          <el-form-item label="部署方式">
            <el-radio-group v-model="deployMethod">
              <el-radio label="upload">上传文件</el-radio>
              <el-radio label="git">Git仓库</el-radio>
            </el-radio-group>
          </el-form-item>
          
          <el-form-item v-if="deployMethod === 'upload'" label="上传文件">
            <el-upload
              v-model:file-list="fileList"
              :auto-upload="false"
              :multiple="true"
              :directory="true"
              :limit="5"
              :on-change="handleFileChange"
            >
              <el-button type="primary">选择文件/文件夹</el-button>
              <template #tip>
                <div class="el-upload__tip">
                  支持上传ZIP包、Python脚本、文件夹或多个文件
                </div>
              </template>
            </el-upload>
          </el-form-item>
          
          <template v-if="deployMethod === 'git'">
            <el-form-item label="Git地址" prop="git_repo_url">
              <el-input v-model="projectForm.git_repo_url" placeholder="请输入Git仓库地址" />
            </el-form-item>
            
            <el-form-item label="分支" prop="git_branch">
              <el-input v-model="projectForm.git_branch" placeholder="请输入分支名称" />
            </el-form-item>
          </template>
        </template>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
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
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Search,
  Plus,
  Refresh
} from '@element-plus/icons-vue'
import { useProjectStore } from '@/store/project'
import type { Project, ProjectCreate, ProjectUpdate } from '@/types/project'
import type { FormInstance, FormRules, UploadUserFile } from 'element-plus'

// 路由
const router = useRouter()

// Store
const projectStore = useProjectStore()

// 响应式数据
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(10)

const dialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const dialogTitle = computed(() => dialogMode.value === 'create' ? '创建项目' : '编辑项目')

const deployMethod = ref<'upload' | 'git'>('upload')
const fileList = ref<UploadUserFile[]>([])

// 表单引用
const projectFormRef = ref<FormInstance>()

// 表单数据
const projectForm = reactive({
  id: 0,
  name: '',
  description: '',
  status: 'DEVELOPING' as 'DEVELOPING' | 'ONLINE' | 'OFFLINE',
  version: '1.0.0',
  entrypoint: 'run.py',
  git_repo_url: '',
  git_branch: 'main'
})

// 表单验证规则
const projectRules = reactive<FormRules>({
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
  ],
  git_repo_url: [
    { required: true, message: '请输入Git仓库地址', trigger: 'blur' }
  ],
  git_branch: [
    { required: true, message: '请输入分支名称', trigger: 'blur' }
  ]
})

// 计算属性
const filteredProjects = computed(() => {
  if (!searchKeyword.value) {
    return projectStore.projects
  }
  
  const keyword = searchKeyword.value.toLowerCase()
  return projectStore.projects.filter(
    project =>
      project.name.toLowerCase().includes(keyword) ||
      project.description.toLowerCase().includes(keyword)
  )
})

// 方法
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

const handleSearch = () => {
  // 搜索功能目前使用前端过滤，通过 filteredProjects 计算属性实现
  // 这里可以添加额外的搜索逻辑（如服务端搜索）
}

const handleRefresh = async () => {
  await projectStore.fetchProjects({
    skip: (currentPage.value - 1) * pageSize.value,
    limit: pageSize.value
  })
}

const handleCreateProject = () => {
  dialogMode.value = 'create'
  resetForm()
  dialogVisible.value = true
}

const handleEditProject = (project: Project) => {
  dialogMode.value = 'edit'
  projectForm.id = project.id
  projectForm.name = project.name
  projectForm.description = project.description
  projectForm.status = project.status
  projectForm.version = project.version
  projectForm.entrypoint = project.entrypoint
  dialogVisible.value = true
}

const handleDeleteProject = async (id: number) => {
  try {
    const result = await projectStore.deleteExistingProject(id)
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

const handleSaveProject = async () => {
  if (!projectFormRef.value) return
  
  await projectFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        let result
        if (dialogMode.value === 'create') {
          // 创建项目
          // 过滤掉 undefined 的文件并确保 raw 字段存在
          const validFiles = fileList.value
            .filter(f => f.raw !== undefined)
            .map(f => f.raw as File)
          
          const projectData: ProjectCreate = {
            name: projectForm.name,
            description: projectForm.description,
            git_repo_url: deployMethod.value === 'git' ? projectForm.git_repo_url : undefined,
            git_branch: deployMethod.value === 'git' ? projectForm.git_branch : undefined,
            // 添加文件上传支持
            file: validFiles.length > 0 ? validFiles[0] : undefined,
            files: validFiles.length > 1 ? validFiles : 
                   (validFiles.length === 1 ? [validFiles[0]] : undefined)
          }
          
          result = await projectStore.createNewProject(projectData)
        } else {
          // 更新项目
          const projectData: ProjectUpdate = {
            name: projectForm.name,
            description: projectForm.description,
            status: projectForm.status,
            version: projectForm.version,
            entrypoint: projectForm.entrypoint
          }
          
          result = await projectStore.updateExistingProject(projectForm.id, projectData)
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

const handleFileChange = (newFileList: UploadUserFile[]) => {
  // 更新文件列表
  fileList.value = newFileList
}

const resetForm = () => {
  projectForm.id = 0
  projectForm.name = ''
  projectForm.description = ''
  projectForm.status = 'DEVELOPING'
  projectForm.version = '1.0.0'
  projectForm.entrypoint = 'run.py'
  projectForm.git_repo_url = ''
  projectForm.git_branch = 'main'
  fileList.value = []
  deployMethod.value = 'upload'
  
  if (projectFormRef.value) {
    projectFormRef.value.resetFields()
  }
}

const goToProjectDetail = (id: number) => {
  router.push(`/projects/${id}`)
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
  await projectStore.fetchProjects({
    skip: 0,
    limit: pageSize.value
  })
})

// 监听分页变化
watch([currentPage, pageSize], async () => {
  await projectStore.fetchProjects({
    skip: (currentPage.value - 1) * pageSize.value,
    limit: pageSize.value
  })
})
</script>

<style scoped>
.project-list {
  padding: 20px;
}

.search-card {
  margin-bottom: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.projects-card {
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