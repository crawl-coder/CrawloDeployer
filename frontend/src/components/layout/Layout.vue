<template>
  <el-container class="layout-container">
    <!-- 侧边栏 -->
    <el-aside width="200px" class="sidebar">
      <div class="logo">
        <h2>CrawloDeployer</h2>
      </div>
      <el-menu
        :default-active="activeMenu"
        class="sidebar-menu"
        router
        @select="handleMenuSelect"
      >
        <el-menu-item index="/">
          <el-icon><House /></el-icon>
          <span>仪表板</span>
        </el-menu-item>
        <el-menu-item index="/projects">
          <el-icon><Folder /></el-icon>
          <span>项目管理</span>
        </el-menu-item>
        <el-menu-item index="/git-credentials">
          <el-icon><Key /></el-icon>
          <span>Git凭证</span>
        </el-menu-item>
        <el-menu-item index="/tasks">
          <el-icon><Collection /></el-icon>
          <span>任务管理</span>
        </el-menu-item>
        <el-menu-item index="/nodes">
          <el-icon><Monitor /></el-icon>
          <span>节点管理</span>
        </el-menu-item>
        <el-menu-item index="/executions">
          <el-icon><Document /></el-icon>
          <span>执行详情</span>
        </el-menu-item>
        <el-menu-item index="/workflows">
          <el-icon><Connection /></el-icon>
          <span>工作流</span>
        </el-menu-item>
        <el-menu-item index="/environment">
          <el-icon><SetUp /></el-icon>
          <span>环境变量</span>
        </el-menu-item>
        <el-menu-item index="/statistics">
          <el-icon><DataAnalysis /></el-icon>
          <span>统计分析</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <!-- 主体区域 -->
    <el-container>
      <!-- 头部 -->
      <el-header class="header">
        <div class="header-left">
          <el-button @click="toggleSidebar" link>
            <el-icon><Expand /></el-icon>
          </el-button>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleUserCommand">
            <span class="user-info">
              <el-avatar :size="30" :icon="User" />
              <span class="username">{{ username }}</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人信息</el-dropdown-item>
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 主要内容 -->
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import {
  House,
  Folder,
  Collection,
  Monitor,
  Expand,
  User,
  Document,
  Connection,
  SetUp,
  DataAnalysis,
  Key
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// 计算属性
const activeMenu = computed(() => route.path)
const username = computed(() => authStore.user?.username || '未知用户')

// 响应式数据
const isSidebarCollapsed = ref(false)

// 方法
const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
}

const handleMenuSelect = (index: string) => {
  // 菜单选择处理
  console.log('Selected menu index:', index)
}

const handleUserCommand = (command: string) => {
  if (command === 'logout') {
    authStore.logout()
    router.push('/login')
  } else if (command === 'profile') {
    // 跳转到个人信息页面
    router.push('/profile')
  }
}

// 生命周期
onMounted(() => {
  if (!authStore.user) {
    authStore.fetchUserInfo()
  }
})
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.sidebar {
  background-color: #304156;
  color: #fff;
  transition: width 0.3s ease;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid #4a5b70;
}

.logo h2 {
  color: #fff;
  margin: 0;
}

.sidebar-menu {
  border-right: none;
  background-color: #304156;
}

.sidebar-menu :deep(.el-menu-item) {
  color: #bfcbd9;
}

.sidebar-menu :deep(.el-menu-item:hover) {
  background-color: #2c3e50;
  color: #fff;
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background-color: #2c3e50;
  color: #409eff;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #fff;
  border-bottom: 1px solid #dcdfe6;
  padding: 0 20px;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.username {
  margin-left: 10px;
  font-size: 14px;
}

.main-content {
  background-color: #f5f5f5;
  padding: 20px;
  overflow: auto;
}
</style>