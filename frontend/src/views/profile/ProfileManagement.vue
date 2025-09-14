<template>
  <div class="profile-management">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="profile-card">
          <div class="avatar-container">
            <el-avatar :size="100" :src="userInfo.avatar || defaultAvatar" />
            <el-button 
              type="primary" 
              link 
              @click="handleUploadAvatar"
              class="upload-btn"
            >
              更换头像
            </el-button>
          </div>
          
          <div class="user-info">
            <h3>{{ userInfo.username }}</h3>
            <p class="user-role">
              <el-tag :type="userInfo.is_superuser ? 'danger' : 'primary'">
                {{ userInfo.is_superuser ? '超级管理员' : '普通用户' }}
              </el-tag>
            </p>
            <p class="user-email">{{ userInfo.email }}</p>
            <p class="user-status">
              <el-tag :type="userInfo.is_active ? 'success' : 'danger'">
                {{ userInfo.is_active ? '活跃' : '禁用' }}
              </el-tag>
            </p>
          </div>
          
          <div class="user-stats">
            <div class="stat-item">
              <div class="stat-value">{{ userStats.projects }}</div>
              <div class="stat-label">项目数</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ userStats.tasks }}</div>
              <div class="stat-label">任务数</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ userStats.executions }}</div>
              <div class="stat-label">执行次数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="18">
        <el-tabs v-model="activeTab">
          <el-tab-pane label="基本信息" name="basic">
            <el-card>
              <template #header>
                <div class="card-header">
                  <span>基本信息</span>
                </div>
              </template>
              
              <el-form
                ref="basicFormRef"
                :model="basicInfo"
                :rules="basicRules"
                label-width="120px"
              >
                <el-row :gutter="20">
                  <el-col :span="12">
                    <el-form-item label="用户名" prop="username">
                      <el-input v-model="basicInfo.username" disabled />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="邮箱" prop="email">
                      <el-input v-model="basicInfo.email" />
                    </el-form-item>
                  </el-col>
                </el-row>
                
                <el-row :gutter="20">
                  <el-col :span="12">
                    <el-form-item label="姓名" prop="fullName">
                      <el-input v-model="basicInfo.fullName" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="电话" prop="phone">
                      <el-input v-model="basicInfo.phone" />
                    </el-form-item>
                  </el-col>
                </el-row>
                
                <el-form-item label="个人简介">
                  <el-input
                    v-model="basicInfo.bio"
                    type="textarea"
                    :rows="4"
                    placeholder="请输入个人简介"
                  />
                </el-form-item>
                
                <el-form-item>
                  <el-button type="primary" @click="updateBasicInfo">保存</el-button>
                </el-form-item>
              </el-form>
            </el-card>
          </el-tab-pane>
          
          <el-tab-pane label="安全设置" name="security">
            <el-card>
              <template #header>
                <div class="card-header">
                  <span>安全设置</span>
                </div>
              </template>
              
              <el-form
                ref="securityFormRef"
                :model="securityInfo"
                :rules="securityRules"
                label-width="150px"
              >
                <el-form-item label="当前密码" prop="currentPassword">
                  <el-input
                    v-model="securityInfo.currentPassword"
                    type="password"
                    show-password
                    placeholder="请输入当前密码"
                  />
                </el-form-item>
                
                <el-form-item label="新密码" prop="newPassword">
                  <el-input
                    v-model="securityInfo.newPassword"
                    type="password"
                    show-password
                    placeholder="请输入新密码"
                  />
                </el-form-item>
                
                <el-form-item label="确认新密码" prop="confirmPassword">
                  <el-input
                    v-model="securityInfo.confirmPassword"
                    type="password"
                    show-password
                    placeholder="请再次输入新密码"
                  />
                </el-form-item>
                
                <el-form-item>
                  <el-button type="primary" @click="updatePassword">修改密码</el-button>
                </el-form-item>
              </el-form>
              
              <el-divider />
              
              <div class="security-actions">
                <h4>安全操作</h4>
                <el-button @click="handleLogoutAll">退出所有设备</el-button>
                <el-button type="danger" @click="handleDeleteAccount">注销账户</el-button>
              </div>
            </el-card>
          </el-tab-pane>
          
          <el-tab-pane label="通知设置" name="notifications">
            <el-card>
              <template #header>
                <div class="card-header">
                  <span>通知设置</span>
                </div>
              </template>
              
              <el-form
                ref="notificationFormRef"
                :model="notificationInfo"
                label-width="200px"
              >
                <el-form-item label="任务执行完成通知">
                  <el-switch
                    v-model="notificationInfo.taskCompleted"
                    active-text="开启"
                    inactive-text="关闭"
                  />
                </el-form-item>
                
                <el-form-item label="任务执行失败通知">
                  <el-switch
                    v-model="notificationInfo.taskFailed"
                    active-text="开启"
                    inactive-text="关闭"
                  />
                </el-form-item>
                
                <el-form-item label="系统更新通知">
                  <el-switch
                    v-model="notificationInfo.systemUpdates"
                    active-text="开启"
                    inactive-text="关闭"
                  />
                </el-form-item>
                
                <el-form-item label="通知方式">
                  <el-checkbox-group v-model="notificationInfo.channels">
                    <el-checkbox label="email">邮件</el-checkbox>
                    <el-checkbox label="sms">短信</el-checkbox>
                    <el-checkbox label="web">站内信</el-checkbox>
                  </el-checkbox-group>
                </el-form-item>
                
                <el-form-item>
                  <el-button type="primary" @click="updateNotifications">保存设置</el-button>
                </el-form-item>
              </el-form>
            </el-card>
          </el-tab-pane>
        </el-tabs>
      </el-col>
    </el-row>
    
    <!-- 头像上传对话框 -->
    <el-dialog
      v-model="avatarDialogVisible"
      title="上传头像"
      width="40%"
      :before-close="handleAvatarDialogClose"
    >
      <el-upload
        ref="uploadRef"
        class="avatar-uploader"
        :action="uploadUrl"
        :headers="uploadHeaders"
        :show-file-list="false"
        :on-success="handleAvatarSuccess"
        :on-error="handleAvatarError"
        :before-upload="beforeAvatarUpload"
      >
        <img v-if="tempAvatar" :src="tempAvatar" class="avatar-preview" />
        <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
      </el-upload>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="avatarDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmAvatarUpload">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, FormInstance } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { 
  getProfile, 
  updateProfile as updateProfileService, 
  updatePassword as updatePasswordService, 
  getStats, 
  updateNotifications as updateNotificationsService, 
  logoutAll, 
  deleteAccount 
} from '@/services/user'
import { useAuthStore } from '@/store/auth'
import defaultAvatar from '@/assets/images/default-avatar.png'

// 数据状态
const activeTab = ref('basic')
const avatarDialogVisible = ref(false)
const tempAvatar = ref('')
const uploadRef = ref()
const basicFormRef = ref<FormInstance>()
const securityFormRef = ref<FormInstance>()
const notificationFormRef = ref<FormInstance>()

// 用户信息
const userInfo = ref({
  id: 0,
  username: '',
  email: '',
  full_name: '',
  phone: '',
  bio: '',
  avatar: '',
  is_superuser: false,
  is_active: true,
  created_at: '',
  updated_at: ''
})

// 用户统计
const userStats = ref({
  projects: 0,
  tasks: 0,
  executions: 0
})

// 基本信息
const basicInfo = reactive({
  username: '',
  email: '',
  fullName: '',
  phone: '',
  bio: ''
})

// 安全信息
const securityInfo = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 通知设置
const notificationInfo = reactive({
  taskCompleted: true,
  taskFailed: true,
  systemUpdates: false,
  channels: ['email', 'web']
})

// 上传配置
const uploadUrl = '/api/v1/users/avatar'
const uploadHeaders = {
  Authorization: `Bearer ${useAuthStore().token}`
}

// 表单验证规则
const basicRules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ]
}

const securityRules = {
  currentPassword: [{ required: true, message: '请输入当前密码', trigger: 'blur' }],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (_rule: any, value: string, callback: any) => {
        if (value !== securityInfo.newPassword) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 获取用户信息
const fetchUserInfo = async () => {
  try {
    const response = await getProfile()
    userInfo.value = {
      id: response.id,
      username: response.username,
      email: response.email,
      full_name: response.full_name || '',
      phone: response.phone || '',
      bio: response.bio || '',
      avatar: response.avatar || '',
      is_superuser: response.is_superuser,
      is_active: response.is_active,
      created_at: response.created_at,
      updated_at: response.updated_at || ''
    }
    basicInfo.username = response.username
    basicInfo.email = response.email
    basicInfo.fullName = response.full_name || ''
    basicInfo.phone = response.phone || ''
    basicInfo.bio = response.bio || ''
  } catch (error) {
    ElMessage.error('获取用户信息失败')
    console.error(error)
  }
}

// 获取用户统计
const fetchUserStats = async () => {
  try {
    const response = await getStats()
    userStats.value = response
  } catch (error) {
    ElMessage.error('获取用户统计失败')
    console.error(error)
  }
}

// 更新基本信息
const updateBasicInfo = async () => {
  if (!basicFormRef.value) return
  
  await basicFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    try {
      const updateData = {
        email: basicInfo.email,
        full_name: basicInfo.fullName,
        phone: basicInfo.phone,
        bio: basicInfo.bio
      }
      
      await updateProfileService(updateData)
      ElMessage.success('更新成功')
      fetchUserInfo()
    } catch (error) {
      ElMessage.error('更新失败')
      console.error(error)
    }
  })
}

// 更新密码
const updatePassword = async () => {
  if (!securityFormRef.value) return
  
  await securityFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    try {
      await updatePasswordService({
        current_password: securityInfo.currentPassword,
        new_password: securityInfo.newPassword
      })
      ElMessage.success('密码修改成功')
      
      // 重置表单
      securityInfo.currentPassword = ''
      securityInfo.newPassword = ''
      securityInfo.confirmPassword = ''
    } catch (error) {
      ElMessage.error('密码修改失败')
      console.error(error)
    }
  })
}

// 更新通知设置
const updateNotifications = async () => {
  try {
    await updateNotificationsService(notificationInfo)
    ElMessage.success('通知设置已保存')
  } catch (error) {
    ElMessage.error('保存失败')
    console.error(error)
  }
}

// 安全操作
const handleLogoutAll = () => {
  ElMessageBox.confirm(
    '确定要退出所有设备的登录吗？',
    '确认操作',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await logoutAll()
      ElMessage.success('已退出所有设备')
      // 跳转到登录页
      window.location.href = '/login'
    } catch (error) {
      ElMessage.error('操作失败')
      console.error(error)
    }
  })
}

const handleDeleteAccount = () => {
  ElMessageBox.prompt(
    '请输入您的用户名以确认注销账户，此操作不可恢复',
    '确认注销',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputPattern: new RegExp(`^${userInfo.value.username}$`),
      inputErrorMessage: '用户名不正确'
    }
  ).then(async () => {
    try {
      await deleteAccount()
      ElMessage.success('账户已注销')
      // 跳转到登录页
      window.location.href = '/login'
    } catch (error) {
      ElMessage.error('注销失败')
      console.error(error)
    }
  })
}

// 头像上传处理
const handleUploadAvatar = () => {
  avatarDialogVisible.value = true
}

const beforeAvatarUpload = (file: File) => {
  const isJPG = file.type === 'image/jpeg' || file.type === 'image/png'
  const isLt2M = file.size / 1024 / 1024 < 2
  
  if (!isJPG) {
    ElMessage.error('头像图片只能是 JPG 或 PNG 格式!')
  }
  if (!isLt2M) {
    ElMessage.error('头像图片大小不能超过 2MB!')
  }
  
  // 预览
  if (isJPG && isLt2M) {
    tempAvatar.value = URL.createObjectURL(file)
  }
  
  return isJPG && isLt2M
}

const handleAvatarSuccess = (response: any) => {
  if (response.success) {
    tempAvatar.value = response.data.url
    ElMessage.success('上传成功')
  } else {
    ElMessage.error('上传失败')
  }
}

const handleAvatarError = () => {
  ElMessage.error('上传失败')
}

const confirmAvatarUpload = () => {
  if (tempAvatar.value) {
    userInfo.value.avatar = tempAvatar.value
    avatarDialogVisible.value = false
    ElMessage.success('头像已更新')
  }
}

const handleAvatarDialogClose = () => {
  avatarDialogVisible.value = false
  tempAvatar.value = ''
}

// 初始化
onMounted(() => {
  fetchUserInfo()
  fetchUserStats()
})
</script>

<style scoped>
.profile-management {
  padding: 20px;
}

.profile-card {
  text-align: center;
}

.avatar-container {
  position: relative;
  display: inline-block;
  margin-bottom: 20px;
}

.upload-btn {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  opacity: 0;
  transition: opacity 0.3s;
}

.avatar-container:hover .upload-btn {
  opacity: 1;
}

.user-info {
  margin-bottom: 30px;
}

.user-info h3 {
  margin: 10px 0;
}

.user-role {
  margin: 10px 0;
}

.user-email {
  color: #606266;
  margin: 5px 0;
}

.user-stats {
  display: flex;
  justify-content: space-around;
  border-top: 1px solid #ebeef5;
  padding-top: 20px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 20px;
  font-weight: bold;
  color: #409eff;
}

.stat-label {
  font-size: 14px;
  color: #606266;
  margin-top: 5px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.security-actions {
  margin-top: 30px;
}

.security-actions h4 {
  margin-bottom: 15px;
}

.security-actions .el-button {
  margin-right: 10px;
}

.avatar-uploader .avatar-preview {
  width: 178px;
  height: 178px;
  display: block;
}

.avatar-uploader .el-upload {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: var(--el-transition-duration-fast);
}

.avatar-uploader .el-upload:hover {
  border-color: #409eff;
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 178px;
  height: 178px;
  text-align: center;
}
</style>