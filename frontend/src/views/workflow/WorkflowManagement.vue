<template>
  <div class="workflow-management">
    <el-card class="filter-card">
      <el-form :model="filterForm" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-form-item label="项目名称">
              <el-input v-model="filterForm.projectName" placeholder="请输入项目名称" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="工作流名称">
              <el-input v-model="filterForm.workflowName" placeholder="请输入工作流名称" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="状态">
              <el-select v-model="filterForm.status" placeholder="请选择状态" clearable>
                <el-option label="启用" value="enabled" />
                <el-option label="禁用" value="disabled" />
              </el-select>
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
          <span>工作流管理</span>
          <el-button type="primary" @click="handleAdd">新增工作流</el-button>
        </div>
      </template>

      <el-table
        :data="workflowList"
        v-loading="loading"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="工作流名称" min-width="200" />
        <el-table-column prop="projectName" label="所属项目" min-width="150" />
        <el-table-column prop="taskCount" label="任务数" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-switch
              v-model="row.status"
              active-value="enabled"
              inactive-value="disabled"
              @change="updateWorkflowStatus(row)"
            />
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="创建时间" width="180" />
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewTasks(row)">任务列表</el-button>
            <el-button link type="primary" @click="editWorkflow(row)">编辑</el-button>
            <el-button link type="primary" @click="designWorkflow(row)">设计</el-button>
            <el-button link type="danger" @click="deleteWorkflow(row)">删除</el-button>
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

    <!-- 工作流编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="60%"
      :before-close="handleDialogClose"
    >
      <el-form
        ref="workflowFormRef"
        :model="currentWorkflow"
        :rules="workflowRules"
        label-width="120px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="工作流名称" prop="name">
              <el-input v-model="currentWorkflow.name" placeholder="请输入工作流名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="所属项目" prop="projectId">
              <el-select
                v-model="currentWorkflow.projectId"
                placeholder="请选择项目"
                style="width: 100%"
                :disabled="!!currentWorkflow.id"
              >
                <el-option
                  v-for="project in projectList"
                  :key="project.id"
                  :label="project.name"
                  :value="project.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="描述">
          <el-input
            v-model="currentWorkflow.description"
            type="textarea"
            :rows="3"
            placeholder="请输入工作流描述"
          />
        </el-form-item>
        
        <el-form-item label="并发执行">
          <el-switch
            v-model="currentWorkflow.concurrent"
            active-text="允许"
            inactive-text="禁止"
          />
        </el-form-item>
        
        <el-form-item label="失败策略">
          <el-radio-group v-model="currentWorkflow.failureStrategy">
            <el-radio label="stop">停止执行</el-radio>
            <el-radio label="continue">继续执行</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 工作流设计对话框 -->
    <el-dialog
      v-model="designDialogVisible"
      title="工作流设计"
      width="80%"
      :before-close="handleDesignDialogClose"
      class="workflow-design-dialog"
    >
      <div class="design-toolbar">
        <el-button type="primary" @click="addTaskNode">添加任务节点</el-button>
        <el-button @click="addDependency">添加依赖关系</el-button>
        <el-button @click="autoLayout">自动布局</el-button>
        <el-button type="success" @click="saveWorkflowDesign">保存设计</el-button>
      </div>
      
      <div ref="flowChartRef" class="flow-chart-container"></div>
    </el-dialog>

    <!-- 任务列表对话框 -->
    <el-dialog
      v-model="tasksDialogVisible"
      title="工作流任务列表"
      width="70%"
      :before-close="handleTasksDialogClose"
    >
      <el-table
        :data="workflowTasks"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="id" label="任务ID" width="80" />
        <el-table-column prop="name" label="任务名称" min-width="200" />
        <el-table-column prop="type" label="类型" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getTaskStatusType(row.status)">
              {{ getTaskStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="dependencies" label="依赖任务" min-width="200">
          <template #default="{ row }">
            <el-tag
              v-for="dep in row.dependencies"
              :key="dep.id"
              size="small"
              style="margin-right: 5px;"
            >
              {{ dep.name }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="editTask(row)">编辑</el-button>
            <el-button link type="danger" @click="removeTask(row)">移除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="tasksDialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, FormInstance } from 'element-plus'
import G6 from '@antv/g6'
import { WorkflowService } from '@/services/workflow'
import { getProjects } from '@/services/project'
import { Workflow, Project, Task } from '@/types'

// 数据状态
const loading = ref(false)
const workflowList = ref<Workflow[]>([])
const projectList = ref<Project[]>([])
const workflowTasks = ref<Task[]>([])
const dialogVisible = ref(false)
const designDialogVisible = ref(false)
const tasksDialogVisible = ref(false)
const dialogTitle = ref('')
const workflowFormRef = ref<FormInstance>()
const flowChartRef = ref<HTMLDivElement | null>(null)
let graph: any = null

// 当前工作流
const currentWorkflow = ref<Workflow>({
  id: 0,
  name: '',
  projectId: 0,
  projectName: '',
  description: '',
  status: 'enabled',
  concurrent: false,
  failureStrategy: 'stop',
  taskCount: 0,
  createdAt: '',
  updatedAt: ''
})

// 当前设计的工作流ID
const currentWorkflowId = ref(0)

// 过滤表单
const filterForm = reactive({
  projectName: '',
  workflowName: '',
  status: ''
})

// 分页
const pagination = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 0
})

// 表单验证规则
const workflowRules = {
  name: [
    { required: true, message: '请输入工作流名称', trigger: 'blur' },
    { max: 50, message: '工作流名称不能超过50个字符', trigger: 'blur' }
  ],
  projectId: [{ required: true, message: '请选择项目', trigger: 'change' }]
}

// 获取工作流列表
const fetchWorkflowList = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.currentPage,
      size: pagination.pageSize,
      projectName: filterForm.projectName || undefined,
      workflowName: filterForm.workflowName || undefined,
      status: filterForm.status || undefined
    }
    
    const response = await WorkflowService.getList(params)
    workflowList.value = response.data.items
    pagination.total = response.data.total
  } catch (error) {
    ElMessage.error('获取工作流列表失败')
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

// 获取工作流任务列表
const fetchWorkflowTasks = async (workflowId: number) => {
  try {
    const response = await WorkflowService.getTasks(workflowId)
    workflowTasks.value = response.data
  } catch (error) {
    ElMessage.error('获取任务列表失败')
    console.error(error)
  }
}

// 操作处理
const handleSearch = () => {
  pagination.currentPage = 1
  fetchWorkflowList()
}

const handleReset = () => {
  filterForm.projectName = ''
  filterForm.workflowName = ''
  filterForm.status = ''
  pagination.currentPage = 1
  fetchWorkflowList()
}

const handleAdd = () => {
  dialogTitle.value = '新增工作流'
  currentWorkflow.value = {
    id: 0,
    name: '',
    projectId: 0,
    projectName: '',
    description: '',
    status: 'enabled',
    concurrent: false,
    failureStrategy: 'stop',
    taskCount: 0,
    createdAt: '',
    updatedAt: ''
  }
  dialogVisible.value = true
}

const editWorkflow = (row: Workflow) => {
  dialogTitle.value = '编辑工作流'
  currentWorkflow.value = { ...row }
  dialogVisible.value = true
}

const deleteWorkflow = (row: Workflow) => {
  ElMessageBox.confirm(
    `确定要删除工作流 "${row.name}" 吗？`,
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await WorkflowService.delete(row.id)
      ElMessage.success('删除成功')
      fetchWorkflowList()
    } catch (error) {
      ElMessage.error('删除失败')
      console.error(error)
    }
  })
}

const viewTasks = async (row: Workflow) => {
  await fetchWorkflowTasks(row.id)
  tasksDialogVisible.value = true
}

const designWorkflow = (row: Workflow) => {
  currentWorkflowId.value = row.id
  designDialogVisible.value = true
  // 延迟初始化图表，确保DOM已渲染
  setTimeout(initFlowChart, 100)
}

const updateWorkflowStatus = async (row: Workflow) => {
  try {
    await WorkflowService.update(row.id, { status: row.status })
    ElMessage.success('状态更新成功')
  } catch (error) {
    ElMessage.error('状态更新失败')
    console.error(error)
    // 恢复状态
    row.status = row.status === 'enabled' ? 'disabled' : 'enabled'
  }
}

const handleSizeChange = (val: number) => {
  pagination.pageSize = val
  pagination.currentPage = 1
  fetchWorkflowList()
}

const handleCurrentChange = (val: number) => {
  pagination.currentPage = val
  fetchWorkflowList()
}

const handleDialogClose = () => {
  dialogVisible.value = false
}

const handleSubmit = async () => {
  if (!workflowFormRef.value) return
  
  await workflowFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    try {
      if (currentWorkflow.value.id) {
        // 编辑
        await WorkflowService.update(currentWorkflow.value.id, currentWorkflow.value)
        ElMessage.success('更新成功')
      } else {
        // 新增
        await WorkflowService.create(currentWorkflow.value)
        ElMessage.success('创建成功')
      }
      
      dialogVisible.value = false
      fetchWorkflowList()
    } catch (error) {
      ElMessage.error(currentWorkflow.value.id ? '更新失败' : '创建失败')
      console.error(error)
    }
  })
}

const handleDesignDialogClose = () => {
  designDialogVisible.value = false
  if (graph) {
    graph.destroy()
    graph = null
  }
}

const handleTasksDialogClose = () => {
  tasksDialogVisible.value = false
}

// 工作流设计相关方法
const initFlowChart = async () => {
  if (!flowChartRef.value) return
  
  // 销毁之前的实例
  if (graph) {
    graph.destroy()
  }
  
  // 初始化G6图实例
  graph = new G6.Graph({
    container: flowChartRef.value,
    width: flowChartRef.value.clientWidth,
    height: 600,
    layout: {
      type: 'dagre',
      rankdir: 'LR',
      nodesep: 30,
      ranksep: 50
    },
    node: {
      type: 'rect',
      style: {
        width: 120,
        height: 40,
        radius: 6,
        stroke: '#5B8FF9',
        fill: '#C6E5FF'
      }
    },
    edge: {
      type: 'polyline',
      style: {
        stroke: '#999',
        lineAppendWidth: 10
      }
    }
  })
  
  // 获取工作流数据
  try {
    const response = await WorkflowService.getDesign(currentWorkflowId.value)
    const data = response.data
    
    // 转换数据格式
    const nodes = data.tasks.map((task: any) => ({
      id: task.id.toString(),
      label: task.name,
      task: task
    }))
    
    const edges = data.dependencies.map((dep: any) => ({
      source: dep.sourceId.toString(),
      target: dep.targetId.toString(),
      label: '依赖'
    }))
    
    graph.data({ nodes, edges })
    graph.render()
  } catch (error) {
    ElMessage.error('获取工作流设计数据失败')
    console.error(error)
  }
}

const addTaskNode = () => {
  ElMessage.info('添加任务节点功能待实现')
}

const addDependency = () => {
  ElMessage.info('添加依赖关系功能待实现')
}

const autoLayout = () => {
  if (graph) {
    graph.updateLayout({
      type: 'dagre',
      rankdir: 'LR',
      nodesep: 30,
      ranksep: 50
    })
  }
}

const saveWorkflowDesign = async () => {
  if (!graph) return
  
  try {
    const data = graph.save()
    const workflowData = {
      tasks: data.nodes.map((node: any) => node.task),
      dependencies: data.edges.map((edge: any) => ({
        sourceId: parseInt(edge.source),
        targetId: parseInt(edge.target)
      }))
    }
    
    await WorkflowService.saveDesign(currentWorkflowId.value, workflowData)
    ElMessage.success('工作流设计保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
    console.error(error)
  }
}

// 任务状态显示
const getTaskStatusType = (status: string) => {
  switch (status) {
    case 'active': return 'success'
    case 'inactive': return 'info'
    case 'error': return 'danger'
    default: return 'info'
  }
}

const getTaskStatusText = (status: string) => {
  switch (status) {
    case 'active': return '启用'
    case 'inactive': return '禁用'
    case 'error': return '错误'
    default: return status
  }
}

// 编辑任务
const editTask = (_row: Task) => {
  ElMessage.info('编辑任务功能待实现')
}

// 移除任务
const removeTask = (row: Task) => {
  ElMessageBox.confirm(
    `确定要从工作流中移除任务 "${row.name}" 吗？`,
    '确认移除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    ElMessage.success('任务已移除')
    // 重新获取任务列表
    fetchWorkflowTasks(currentWorkflowId.value)
  })
}

// 初始化
onMounted(() => {
  fetchWorkflowList()
  fetchProjectList()
})
</script>

<style scoped>
.workflow-management {
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

.workflow-design-dialog :deep(.el-dialog__body) {
  padding: 0;
}

.design-toolbar {
  padding: 15px 20px;
  border-bottom: 1px solid #ebeef5;
}

.flow-chart-container {
  width: 100%;
  height: 600px;
}
</style>