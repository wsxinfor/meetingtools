<template>
  <div class="projects-view">
    <div class="page-header">
      <el-select
        v-model="filterCustomerId"
        placeholder="筛选客户"
        clearable
        style="width: 200px"
        @change="load"
      >
        <el-option
          v-for="c in allCustomers"
          :key="c.id"
          :label="c.name"
          :value="c.id"
        />
      </el-select>
      <el-button type="primary" class="btn-new" @click="openCreate">新增项目</el-button>
    </div>

    <el-table :data="projects" v-loading="loading" class="data-table">
      <el-table-column label="项目名称" prop="name" min-width="160" />
      <el-table-column label="所属客户" width="140">
        <template #default="{ row }">{{ customerName(row.customer_id) }}</template>
      </el-table-column>
      <el-table-column label="阶段" prop="stage" width="100">
        <template #default="{ row }">{{ row.stage ?? '-' }}</template>
      </el-table-column>
      <el-table-column label="预算" prop="budget" width="120">
        <template #default="{ row }">{{ row.budget ?? '-' }}</template>
      </el-table-column>
      <el-table-column label="备注" prop="notes" min-width="160">
        <template #default="{ row }">{{ row.notes ?? '-' }}</template>
      </el-table-column>
      <el-table-column label="创建时间" width="170">
        <template #default="{ row }">{{ fmtDate(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="120">
        <template #default="{ row }">
          <el-button size="small" link @click="openEdit(row)">编辑</el-button>
          <el-button size="small" link type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="editingItem ? '编辑项目' : '新增项目'" width="520px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="所属客户" required>
          <el-select v-model="form.customer_id" placeholder="选择客户" style="width: 100%" filterable>
            <el-option
              v-for="c in allCustomers"
              :key="c.id"
              :label="c.name"
              :value="c.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="项目名称" required>
          <el-input v-model="form.name" placeholder="项目名称" />
        </el-form-item>
        <el-form-item label="阶段">
          <el-select v-model="form.stage" placeholder="可选" clearable style="width: 100%">
            <el-option label="意向" value="intention" />
            <el-option label="跟进" value="followup" />
            <el-option label="方案" value="proposal" />
            <el-option label="商务" value="negotiation" />
            <el-option label="签约" value="closed" />
            <el-option label="交付" value="delivery" />
          </el-select>
        </el-form-item>
        <el-form-item label="预算">
          <el-input v-model="form.budget" placeholder="如：50万" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.notes" type="textarea" :rows="3" placeholder="可选" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { listCustomers, type Customer } from '@/api/customers'
import { listProjects, createProject, updateProject, deleteProject, type Project, type ProjectCreate } from '@/api/projects'

const projects = ref<Project[]>([])
const allCustomers = ref<Customer[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const saving = ref(false)
const editingItem = ref<Project | null>(null)
const filterCustomerId = ref<string>('')

const form = ref({
  customer_id: '',
  name: '',
  stage: '',
  budget: '',
  notes: '',
})

async function load() {
  loading.value = true
  try {
    projects.value = await listProjects(filterCustomerId.value || undefined)
  } finally {
    loading.value = false
  }
}

async function loadCustomers() {
  allCustomers.value = await listCustomers()
}

function customerName(customerId: string): string {
  return allCustomers.value.find(c => c.id === customerId)?.name ?? '-'
}

function openCreate() {
  editingItem.value = null
  form.value = { customer_id: '', name: '', stage: '', budget: '', notes: '' }
  dialogVisible.value = true
}

function openEdit(item: Project) {
  editingItem.value = item
  form.value = {
    customer_id: item.customer_id,
    name: item.name,
    stage: item.stage ?? '',
    budget: item.budget ?? '',
    notes: item.notes ?? '',
  }
  dialogVisible.value = true
}

async function handleSave() {
  if (!form.value.customer_id) {
    ElMessage.warning('请选择所属客户')
    return
  }
  if (!form.value.name.trim()) {
    ElMessage.warning('项目名称不能为空')
    return
  }
  saving.value = true
  try {
    const payload: ProjectCreate = {
      customer_id: form.value.customer_id,
      name: form.value.name.trim(),
    }
    if (form.value.stage) payload.stage = form.value.stage
    if (form.value.budget.trim()) payload.budget = form.value.budget.trim()
    if (form.value.notes.trim()) payload.notes = form.value.notes.trim()

    if (editingItem.value) {
      const updated = await updateProject(editingItem.value.id, payload)
      const idx = projects.value.findIndex(p => p.id === updated.id)
      if (idx >= 0) projects.value[idx] = updated
    } else {
      const created = await createProject(payload)
      projects.value.unshift(created)
    }
    dialogVisible.value = false
    ElMessage.success('保存成功')
  } catch (e: unknown) {
    const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    ElMessage.error(msg ?? '保存失败')
  } finally {
    saving.value = false
  }
}

async function handleDelete(item: Project) {
  await ElMessageBox.confirm(`确认删除项目「${item.name}」？`, '删除确认', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消',
  })
  try {
    await deleteProject(item.id)
    projects.value = projects.value.filter(p => p.id !== item.id)
    ElMessage.success('已删除')
  } catch (e: unknown) {
    const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    ElMessage.error(msg ?? '删除失败')
  }
}

function fmtDate(d: string) {
  return new Date(d).toLocaleString('zh-CN', { hour12: false })
}

onMounted(() => {
  loadCustomers()
  load()
})
</script>

<style scoped>
.projects-view {
  display: flex;
  flex-direction: column;
  gap: var(--meeting-space-4);
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.btn-new {
  border-radius: var(--meeting-radius-md);
  padding: 7px 16px;
  font-weight: var(--meeting-font-weight-medium);
}

.data-table {
  border-radius: var(--meeting-radius-lg);
  overflow: hidden;
}
</style>
