<template>
  <div class="git-credential-management">
    <el-card class="credential-card">
      <template #header>
        <div class="card-header">
          <span>Git 凭证管理</span>
          <el-button type="primary" @click="handleCreateCredential">
            <el-icon><Plus /></el-icon>
            添加凭证
          </el-button>
        </div>
      </template>
      
      <el-table
        :data="gitStore.credentials"
        v-loading="gitStore.loading"
        style="width: 100%"
      >
        <el-table-column prop="provider" label="提供商" width="150" />
        <el-table-column prop="username" label="用户名" width="200" />
        <el-table-column label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button link @click="handleEditCredential(row)">编辑</el-button>
            <el-popconfirm
              title="确定要删除这个凭证吗？"
              @confirm="handleDeleteCredential(row.id)"
            >
              <template #reference>
                <el-button link type="danger">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 创建/编辑凭证对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      @close="handleDialogClose"
    >
      <el-form
        ref="credentialFormRef"
        :model="credentialForm"
        :rules="credentialRules"
        label-width="120px"
      >
        <el-form-item label="提供商" prop="provider">
          <el-select v-model="credentialForm.provider" placeholder="请选择提供商" style="width: 100%">
            <el-option label="GitHub" value="github" />
            <el-option label="GitLab" value="gitlab" />
            <el-option label="Gitee" value="gitee" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="用户名" prop="username">
          <el-input v-model="credentialForm.username" placeholder="请输入用户名" />
        </el-form-item>
        
        <el-form-item label="密码/Token" prop="token">
          <el-input
            v-model="credentialForm.token"
            type="password"
            placeholder="请输入密码或访问令牌"
            show-password
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button
            type="primary"
            :loading="gitStore.loading"
            @click="handleSaveCredential"
          >
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { useGitStore } from '@/store/git'
import type { FormInstance, FormRules } from 'element-plus'
import type { GitCredential } from '@/types/project'

// Store
const gitStore = useGitStore()

// 响应式数据
const dialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')

const dialogTitle = computed(() => dialogMode.value === 'create' ? '添加Git凭证' : '编辑Git凭证')

// 表单引用
const credentialFormRef = ref<FormInstance>()

// 表单数据
const credentialForm = reactive({
  id: 0,
  provider: 'github',
  username: '',
  token: ''
})

// 表单验证规则
const credentialRules = reactive<FormRules>({
  provider: [
    { required: true, message: '请选择提供商', trigger: 'change' }
  ],
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  token: [
    { required: true, message: '请输入密码或访问令牌', trigger: 'blur' }
  ]
})

// 方法
const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

const handleCreateCredential = () => {
  dialogMode.value = 'create'
  resetForm()
  dialogVisible.value = true
}

const handleEditCredential = (credential: GitCredential) => {
  dialogMode.value = 'edit'
  credentialForm.id = credential.id
  credentialForm.provider = credential.provider
  credentialForm.username = credential.username
  dialogVisible.value = true
}

const handleDeleteCredential = async (id: number) => {
  try {
    const result = await gitStore.deleteCredential(id)
    if (result.success) {
      ElMessage.success('删除成功')
    } else {
      ElMessage.error(result.message || '删除失败')
    }
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

const handleSaveCredential = async () => {
  if (!credentialFormRef.value) return
  
  await credentialFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        let result
        if (dialogMode.value === 'create') {
          // 创建凭证
          const credentialData = {
            provider: credentialForm.provider,
            username: credentialForm.username,
            token: credentialForm.token
          }
          result = await gitStore.createCredential(credentialData)
          if (result.success) {
            ElMessage.success('添加成功')
          }
        } else {
          // 更新凭证
          const credentialData = {
            provider: credentialForm.provider,
            username: credentialForm.username,
            token: credentialForm.token
          }
          result = await gitStore.updateCredential(credentialForm.id, credentialData)
          if (result.success) {
            ElMessage.success('更新成功')
          }
        }
        
        if (result.success) {
          dialogVisible.value = false
          await gitStore.fetchCredentials()
        } else {
          ElMessage.error(result.message || (dialogMode.value === 'create' ? '添加失败' : '更新失败'))
        }
      } catch (error) {
        ElMessage.error(dialogMode.value === 'create' ? '添加失败' : '更新失败')
      }
    }
  })
}

const handleDialogClose = () => {
  resetForm()
}

const resetForm = () => {
  credentialForm.id = 0
  credentialForm.provider = 'github'
  credentialForm.username = ''
  credentialForm.token = ''
  
  if (credentialFormRef.value) {
    credentialFormRef.value.resetFields()
  }
}

// 生命周期
onMounted(async () => {
  await gitStore.fetchCredentials()
})
</script>

<style scoped>
.git-credential-management {
  padding: 20px;
}

.credential-card {
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