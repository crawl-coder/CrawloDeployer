<template>
  <div class="env-management">
    <el-card class="filter-card">
      <el-form :model="filterForm" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-form-item label="项目名称">
              <el-input v-model="filterForm.projectName" placeholder="请输入项目名称" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="环境变量名">
              <el-input v-model="filterForm.envName" placeholder="请输入环境变量名" />
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
          <span>环境变量管理</span>
          <el-button type="primary" @click="handleAdd">新增环境变量</el-button>
        </div>
      </template>

      <el-table
        :data="envList"
        v-loading="loading"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="projectName" label="所属项目" min-width="150" />
        <el-table-column prop="name" label="变量名" min-width="200" />
        <el-table-column prop="value" label="变量值" min-width="200">
          <template #default="{ row }">
            <span v-if="!row.isSecret">{{ row.value }}</span>
            <span v-else>********</span>
          </template>
        </el-table-column>
        <el-table-column prop="isSecret" label="是否保密" width="100">
          <template #default="{ row }">
            <el-tag :type="row.isSecret ? 'danger' : 'info'">
              {{ row.isSecret ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" />
        <el-table-column prop="updatedAt" label="更新时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
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

    <!-- 环境变量编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="50%"
      :before-close="handleDialogClose"
    >
      <el-form
        ref="envFormRef"
        :model="currentEnv"
        :rules="envRules"
        label-width="120px"
      >
        <el-form-item label="所属项目" prop="projectId">
          <el-select
            v-model="currentEnv.projectId"
            placeholder="请选择项目"
            style="width: 100%"
            :disabled="!!currentEnv.id"
          >
            <el-option
              v-for="project in projectList"
              :key="project.id"
              :label="project.name"
              :value="project.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="变量名" prop="name">
          <el-input v-model="currentEnv.name" placeholder="请输入变量名" />
        </el-form-item>
        
        <el-form-item label="变量值" prop="value">
          <el-input
            v-model="currentEnv.value"
            type="textarea"
            :rows="3"
            placeholder="请输入变量值"
          />
        </el-form-item>
        
        <el-form-item label="是否保密" prop="isSecret">
          <el-switch
            v-model="currentEnv.isSecret"
            active-text="是"
            inactive-text="否"
          />
        </el-form-item>
        
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="currentEnv.description"
            type="textarea"
            :rows="2"
            placeholder="请输入描述"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, FormInstance } from 'element-plus'
import { EnvService } from '@/services/env'
import { getProjects } from '@/services/project'
import { EnvVariable, Project } from '@/types'

// 数据状态
const loading = ref(false)
const envList = ref<EnvVariable[]>([])
const projectList = ref<Project[]>([])
const dialogVisible = ref(false)
const dialogTitle = ref('')
const envFormRef = ref<FormInstance>()

// 当前环境变量
const currentEnv = ref<EnvVariable>({
  id: 0,
  projectId: 0,
  projectName: '',
  name: '',
  value: '',
  isSecret: false,
  description: '',
  createdAt: '',
  updatedAt: ''
})

// 过滤表单
const filterForm = reactive({
  projectName: '',
  envName: ''
})

// 分页
const pagination = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 0
})

// 表单验证规则
const envRules = {
  projectId: [{ required: true, message: '请选择项目', trigger: 'change' }],
  name: [
    { required: true, message: '请输入变量名', trigger: 'blur' },
    { pattern: /^[a-zA-Z_][a-zA-Z0-9_]*$/, message: '变量名格式不正确', trigger: 'blur' }
  ],
  value: [{ required: true, message: '请输入变量值', trigger: 'blur' }]
}

// 获取环境变量列表
const fetchEnvList = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.currentPage,
      size: pagination.pageSize,
      projectName: filterForm.projectName || undefined,
      envName: filterForm.envName || undefined
    }
    
    const response = await EnvService.getList(params)
    envList.value = response.data.items
    pagination.total = response.data.total
  } catch (error) {
    ElMessage.error('获取环境变量失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 获取项目列表
const fetchProjectList = async () => {
  try {
    const response = await getProjects({ skip: 0, limit: 1000 })
    projectList.value = response
  } catch (error) {
    ElMessage.error('获取项目列表失败')
    console.error(error)
  }
}

// 操作处理
const handleSearch = () => {
  pagination.currentPage = 1
  fetchEnvList()
}

const handleReset = () => {
  filterForm.projectName = ''
  filterForm.envName = ''
  pagination.currentPage = 1
  fetchEnvList()
}

const handleAdd = () => {
  dialogTitle.value = '新增环境变量'
  currentEnv.value = {
    id: 0,
    projectId: 0,
    projectName: '',
    name: '',
    value: '',
    isSecret: false,
    description: '',
    createdAt: '',
    updatedAt: ''
  }
  dialogVisible.value = true
}

const handleEdit = (row: EnvVariable) => {
  dialogTitle.value = '编辑环境变量'
  currentEnv.value = { ...row }
  dialogVisible.value = true
}

const handleDelete = (row: EnvVariable) => {
  ElMessageBox.confirm(
    `确定要删除环境变量 "${row.name}" 吗？`,
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await EnvService.delete(row.id)
      ElMessage.success('删除成功')
      fetchEnvList()
    } catch (error) {
      ElMessage.error('删除失败')
      console.error(error)
    }
  }).catch(() => {
    // 取消删除
  })
}

const handleSizeChange = (val: number) => {
  pagination.pageSize = val
  pagination.currentPage = 1
  fetchEnvList()
}

const handleCurrentChange = (val: number) => {
  pagination.currentPage = val
  fetchEnvList()
}

const handleDialogClose = () => {
  dialogVisible.value = false
}

const handleSubmit = async () => {
  if (!envFormRef.value) return
  
  await envFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    try {
      if (currentEnv.value.id) {
        // 编辑
        await EnvService.update(currentEnv.value.id, currentEnv.value)
        ElMessage.success('更新成功')
      } else {
        // 新增
        await EnvService.create(currentEnv.value)
        ElMessage.success('创建成功')
      }
      
      dialogVisible.value = false
      fetchEnvList()
    } catch (error) {
      ElMessage.error(currentEnv.value.id ? '更新失败' : '创建失败')
      console.error(error)
    }
  })
}

// 初始化
onMounted(() => {
  fetchEnvList()
  fetchProjectList()
})
</script>

<style scoped>
.env-management {
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
</style>