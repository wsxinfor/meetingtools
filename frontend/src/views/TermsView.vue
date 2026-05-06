<template>
  <div class="terms-view">
    <div class="page-header">
      <el-button type="primary" class="btn-new-term" @click="openCreate">新增术语</el-button>
    </div>

    <el-table :data="terms" v-loading="loading" class="terms-table">
      <el-table-column label="分类" prop="category" width="100">
        <template #default="{ row }">{{ categoryLabel(row.category) }}</template>
      </el-table-column>
      <el-table-column label="错误写法" prop="wrong_text" />
      <el-table-column label="正确写法" prop="correct_text" />
      <el-table-column label="别名" min-width="120">
        <template #default="{ row }">
          <span
            v-for="(a, i) in (row.aliases ?? [])"
            :key="i"
            class="term-tag"
          >{{ a }}</span>
          <span v-if="!row.aliases?.length">-</span>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="80">
        <template #default="{ row }">
          <el-switch
            :model-value="row.enabled"
            @change="(v: boolean) => toggleEnabled(row, v)"
          />
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120">
        <template #default="{ row }">
          <el-button size="small" link @click="openEdit(row)">编辑</el-button>
          <el-button size="small" link type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- Create / Edit dialog -->
    <el-dialog v-model="dialogVisible" :title="editingTerm ? '编辑术语' : '新增术语'" width="480px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="分类">
          <el-select v-model="form.category" style="width: 100%">
            <el-option label="通用" value="common" />
            <el-option label="品牌" value="brand" />
            <el-option label="产品" value="product" />
            <el-option label="客户" value="customer" />
          </el-select>
        </el-form-item>
        <el-form-item label="错误写法" required>
          <el-input v-model="form.wrong_text" placeholder="如：A I" />
        </el-form-item>
        <el-form-item label="正确写法" required>
          <el-input v-model="form.correct_text" placeholder="如：AI" />
        </el-form-item>
        <el-form-item label="别名">
          <div class="alias-list">
            <el-tag
              v-for="(a, i) in form.aliases"
              :key="i"
              closable
              @close="removeAlias(i)"
              class="term-tag-interactive"
            >{{ a }}</el-tag>
            <el-input
              v-model="aliasInput"
              size="small"
              placeholder="输入别名回车添加"
              style="width: 140px"
              @keyup.enter="addAlias"
            />
          </div>
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="form.enabled" />
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
import { listTerms, createTerm, updateTerm, deleteTerm, type Term } from '@/api/terms'

const terms = ref<Term[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const saving = ref(false)
const editingTerm = ref<Term | null>(null)
const aliasInput = ref('')

const form = ref({
  category: 'common',
  wrong_text: '',
  correct_text: '',
  aliases: [] as string[],
  enabled: true,
})

async function load() {
  loading.value = true
  try {
    terms.value = await listTerms()
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingTerm.value = null
  form.value = { category: 'common', wrong_text: '', correct_text: '', aliases: [], enabled: true }
  aliasInput.value = ''
  dialogVisible.value = true
}

function openEdit(term: Term) {
  editingTerm.value = term
  form.value = {
    category: term.category,
    wrong_text: term.wrong_text,
    correct_text: term.correct_text,
    aliases: [...(term.aliases ?? [])],
    enabled: term.enabled,
  }
  aliasInput.value = ''
  dialogVisible.value = true
}

function addAlias() {
  const v = aliasInput.value.trim()
  if (v && !form.value.aliases.includes(v)) form.value.aliases.push(v)
  aliasInput.value = ''
}

function removeAlias(i: number) {
  form.value.aliases.splice(i, 1)
}

async function handleSave() {
  if (!form.value.wrong_text.trim() || !form.value.correct_text.trim()) {
    ElMessage.warning('错误写法和正确写法不能为空')
    return
  }
  saving.value = true
  try {
    const payload = {
      ...form.value,
      aliases: form.value.aliases.length ? form.value.aliases : null,
    }
    if (editingTerm.value) {
      const updated = await updateTerm(editingTerm.value.id, payload)
      const idx = terms.value.findIndex(t => t.id === updated.id)
      if (idx >= 0) terms.value[idx] = updated
    } else {
      const created = await createTerm(payload)
      terms.value.push(created)
    }
    dialogVisible.value = false
    ElMessage.success('保存成功')
  } catch {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

async function toggleEnabled(term: Term, enabled: boolean) {
  try {
    const updated = await updateTerm(term.id, { enabled })
    const idx = terms.value.findIndex(t => t.id === updated.id)
    if (idx >= 0) terms.value[idx] = updated
  } catch {
    ElMessage.error('操作失败')
  }
}

async function handleDelete(term: Term) {
  await ElMessageBox.confirm(`确认删除术语「${term.wrong_text}」？`, '删除确认', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消',
  })
  try {
    await deleteTerm(term.id)
    terms.value = terms.value.filter(t => t.id !== term.id)
    ElMessage.success('已删除')
  } catch {
    ElMessage.error('删除失败')
  }
}

function categoryLabel(c: string) {
  const map: Record<string, string> = { common: '通用', brand: '品牌', product: '产品', customer: '客户' }
  return map[c] ?? c
}

onMounted(load)
</script>

<style scoped>
.terms-view {
  display: flex;
  flex-direction: column;
  gap: var(--meeting-space-4);
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

.btn-new-term {
  border-radius: var(--meeting-radius-md);
  padding: 7px 16px;
  font-weight: var(--meeting-font-weight-medium);
}

.terms-table {
  border-radius: var(--meeting-radius-lg);
  overflow: hidden;
}

/* ── 术语标签 — 赭石色系 ── */
.term-tag {
  display: inline-block;
  background: var(--meeting-color-accent-bg);
  color: var(--meeting-color-accent);
  border: 0.5px solid var(--meeting-color-accent);
  border-radius: var(--meeting-radius-sm);
  padding: 1px var(--meeting-space-2);
  margin-right: var(--meeting-space-1);
  font-size: var(--meeting-font-size-sm);
  font-weight: var(--meeting-font-weight-normal);
  line-height: var(--meeting-line-height-tight);
}

.term-tag-interactive {
  margin-right: var(--meeting-space-1);
  margin-bottom: var(--meeting-space-1);
  background: var(--meeting-color-accent-bg);
  color: var(--meeting-color-accent);
  border-color: var(--meeting-color-accent);
}

.alias-list {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
}
</style>
