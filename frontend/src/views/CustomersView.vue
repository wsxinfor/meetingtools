<template>
  <div class="customers-view">
    <div class="page-header">
      <el-button type="primary" class="btn-new" @click="openCreate">新增客户</el-button>
    </div>

    <el-table :data="customers" v-loading="loading" class="data-table">
      <el-table-column label="客户名称" prop="name" min-width="160" />
      <el-table-column label="行业" prop="industry" width="120">
        <template #default="{ row }">{{ row.industry ?? '-' }}</template>
      </el-table-column>
      <el-table-column label="备注" prop="notes" min-width="200">
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

    <el-dialog v-model="dialogVisible" :title="editingItem ? '编辑客户' : '新增客户'" width="480px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="名称" required>
          <el-input v-model="form.name" placeholder="客户名称" />
        </el-form-item>
        <el-form-item label="行业">
          <el-input v-model="form.industry" placeholder="如：金融、制造" />
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
import { listCustomers, createCustomer, updateCustomer, deleteCustomer, type Customer, type CustomerCreate } from '@/api/customers'

const customers = ref<Customer[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const saving = ref(false)
const editingItem = ref<Customer | null>(null)

const form = ref({
  name: '',
  industry: '',
  notes: '',
})

async function load() {
  loading.value = true
  try {
    customers.value = await listCustomers()
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingItem.value = null
  form.value = { name: '', industry: '', notes: '' }
  dialogVisible.value = true
}

function openEdit(item: Customer) {
  editingItem.value = item
  form.value = {
    name: item.name,
    industry: item.industry ?? '',
    notes: item.notes ?? '',
  }
  dialogVisible.value = true
}

async function handleSave() {
  if (!form.value.name.trim()) {
    ElMessage.warning('客户名称不能为空')
    return
  }
  saving.value = true
  try {
    const payload: CustomerCreate = { name: form.value.name.trim() }
    if (form.value.industry.trim()) payload.industry = form.value.industry.trim()
    if (form.value.notes.trim()) payload.notes = form.value.notes.trim()

    if (editingItem.value) {
      const updated = await updateCustomer(editingItem.value.id, payload)
      const idx = customers.value.findIndex(c => c.id === updated.id)
      if (idx >= 0) customers.value[idx] = updated
    } else {
      const created = await createCustomer(payload)
      customers.value.unshift(created)
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

async function handleDelete(item: Customer) {
  await ElMessageBox.confirm(`确认删除客户「${item.name}」？`, '删除确认', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消',
  })
  try {
    await deleteCustomer(item.id)
    customers.value = customers.value.filter(c => c.id !== item.id)
    ElMessage.success('已删除')
  } catch (e: unknown) {
    const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    ElMessage.error(msg ?? '删除失败')
  }
}

function fmtDate(d: string) {
  return new Date(d).toLocaleString('zh-CN', { hour12: false })
}

onMounted(load)
</script>

<style scoped>
.customers-view {
  display: flex;
  flex-direction: column;
  gap: var(--meeting-space-4);
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: flex-end;
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
