<template>
  <div class="users-view">
    <div class="toolbar">
      <span class="section-label">用户管理</span>
      <el-button type="primary" @click="openCreate">新建用户</el-button>
    </div>

    <el-table :data="users" v-loading="loading" border style="margin-top: var(--space-4)">
      <el-table-column prop="username" label="用户名" min-width="140" />
      <el-table-column label="角色" width="100">
        <template #default="{ row }">
          <el-tag :type="row.role === 'admin' ? 'warning' : 'info'" size="small">
            {{ row.role === 'admin' ? '管理员' : '普通用户' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
            {{ row.is_active ? '正常' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="创建时间" width="180">
        <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button size="small" link @click="openEdit(row)">修改</el-button>
          <el-button
            size="small"
            link
            :type="row.is_active ? 'warning' : 'success'"
            :disabled="row.id === authStore.user?.id"
            @click="toggleActive(row)"
          >
            {{ row.is_active ? '禁用' : '启用' }}
          </el-button>
          <el-popconfirm
            title="确定删除该用户？"
            @confirm="handleDelete(row.id)"
          >
            <template #reference>
              <el-button
                size="small"
                link
                type="danger"
                :disabled="row.id === authStore.user?.id"
              >
                删除
              </el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <!-- Create / Edit Drawer -->
    <el-drawer
      v-model="drawerVisible"
      :title="editingUser ? '修改用户' : '新建用户'"
      size="400px"
      :close-on-click-modal="false"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" :disabled="!!editingUser" placeholder="仅限字母数字下划线" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            :placeholder="editingUser ? '不填则保持不变' : '至少6位'"
            show-password
          />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="form.role" style="width: 100%">
            <el-option label="普通用户" value="user" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="drawerVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">保存</el-button>
      </template>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { listUsers, createUser, updateUser, deleteUser, type UserInfo } from '@/api/users'
import { useAuthStore } from '@/stores/useAuthStore'

const authStore = useAuthStore()
const users = ref<UserInfo[]>([])
const loading = ref(false)
const drawerVisible = ref(false)
const saving = ref(false)
const editingUser = ref<UserInfo | null>(null)
const formRef = ref<FormInstance>()

const form = ref({ username: '', password: '', role: 'user' })

const rules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [
    {
      validator: (_rule, value: string, callback) => {
        if (!editingUser.value && (!value || value.length < 6)) {
          callback(new Error('密码至少6位'))
        } else if (value && value.length > 0 && value.length < 6) {
          callback(new Error('密码至少6位'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
}

async function fetchUsers() {
  loading.value = true
  try {
    users.value = await listUsers()
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingUser.value = null
  form.value = { username: '', password: '', role: 'user' }
  drawerVisible.value = true
}

function openEdit(user: UserInfo) {
  editingUser.value = user
  form.value = { username: user.username, password: '', role: user.role }
  drawerVisible.value = true
}

async function save() {
  await formRef.value?.validate()
  saving.value = true
  try {
    if (editingUser.value) {
      const payload: Record<string, unknown> = { role: form.value.role }
      if (form.value.password) payload.password = form.value.password
      await updateUser(editingUser.value.id, payload)
      ElMessage.success('修改成功')
    } else {
      await createUser({ username: form.value.username, password: form.value.password, role: form.value.role })
      ElMessage.success('创建成功')
    }
    drawerVisible.value = false
    await fetchUsers()
  } finally {
    saving.value = false
  }
}

async function toggleActive(user: UserInfo) {
  await updateUser(user.id, { is_active: !user.is_active })
  await fetchUsers()
}

async function handleDelete(id: string) {
  await deleteUser(id)
  ElMessage.success('已删除')
  await fetchUsers()
}

function formatDate(d: string) {
  return new Date(d).toLocaleString('zh-CN', { hour12: false })
}

onMounted(fetchUsers)
</script>

<style scoped>
.users-view {
  padding: var(--space-6);
}
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.section-label {
  font-size: var(--font-size-section-title);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}
</style>
