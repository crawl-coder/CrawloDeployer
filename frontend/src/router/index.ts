import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/store/auth'

// 公共页面
const Login = () => import('@/views/auth/Login.vue')
const Register = () => import('@/views/auth/Register.vue')

// 布局组件
const Layout = () => import('@/components/layout/Layout.vue')

// 主要页面
const Dashboard = () => import('@/views/dashboard/Dashboard.vue')
const ProjectList = () => import('@/views/projects/ProjectList.vue')
const ProjectDetail = () => import('@/views/projects/ProjectDetail.vue')
const GitCredentialManagement = () => import('@/views/projects/GitCredentialManagement.vue')
const TaskList = () => import('@/views/tasks/TaskList.vue')
const NodeList = () => import('@/views/nodes/NodeList.vue')
const ExecutionList = () => import('@/views/executions/ExecutionList.vue')
const ExecutionDetail = () => import('@/views/executions/ExecutionDetail.vue')
const EnvManagement = () => import('@/views/environment/EnvManagement.vue')
const ProfileManagement = () => import('@/views/profile/ProfileManagement.vue')
const TaskStatistics = () => import('@/views/statistics/TaskStatistics.vue')
const WorkflowManagement = () => import('@/views/workflow/WorkflowManagement.vue')

const routes: Array<RouteRecordRaw> = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresGuest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { requiresGuest: true }
  },
  {
    path: '/',
    component: Layout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: Dashboard
      },
      {
        path: 'projects',
        name: 'ProjectList',
        component: ProjectList
      },
      {
        path: 'projects/:id',
        name: 'ProjectDetail',
        component: ProjectDetail,
        props: true
      },
      {
        path: 'git-credentials',
        name: 'GitCredentialManagement',
        component: GitCredentialManagement
      },
      {
        path: 'tasks',
        name: 'TaskList',
        component: TaskList
      },
      {
        path: 'nodes',
        name: 'NodeList',
        component: NodeList
      },
      {
        path: 'executions',
        name: 'ExecutionList',
        component: ExecutionList
      },
      {
        path: 'executions/:id',
        name: 'ExecutionDetail',
        component: ExecutionDetail,
        props: true
      },
      {
        path: 'environment',
        name: 'EnvManagement',
        component: EnvManagement
      },
      {
        path: 'profile',
        name: 'ProfileManagement',
        component: ProfileManagement
      },
      {
        path: 'statistics',
        name: 'TaskStatistics',
        component: TaskStatistics
      },
      {
        path: 'workflows',
        name: 'WorkflowManagement',
        component: WorkflowManagement
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 添加路由守卫
router.beforeEach(async (to, from, next) => {
  try {
    const authStore = useAuthStore()
    
    // 初始化认证状态
    if (!authStore.token) {
      await authStore.initAuth()
    }
    
    // 记录导航信息（用于调试）
    console.log(`导航: 从 ${from.path} 到 ${to.path}`)
    console.log(`认证状态: ${authStore.isAuthenticated ? '已认证' : '未认证'}`)
    
    // 检查是否需要认证
    if (to.meta.requiresAuth && !authStore.isAuthenticated) {
      // 需要认证但未登录，重定向到登录页
      console.log('需要认证但未登录，重定向到登录页')
      next('/login')
    } else if (to.meta.requiresGuest && authStore.isAuthenticated) {
      // 不需要认证但已登录，重定向到首页
      console.log('不需要认证但已登录，重定向到首页')
      next('/')
    } else {
      // 其他情况，允许访问
      console.log('允许访问')
      next()
    }
  } catch (error) {
    console.error('路由守卫出错:', error)
    // 发生错误时，为了保证用户体验，仍然允许访问
    next()
  }
})

export default router