<template>
  <div class="meeting-list">
    <div class="toolbar">
      <el-input
        v-model="keyword"
        placeholder="搜索会议标题"
        clearable
        style="width: 240px"
        @change="fetchMeetings"
      />
      <el-select
        v-model="statusFilter"
        placeholder="状态筛选"
        clearable
        style="width: 140px"
        @change="fetchMeetings"
      >
        <el-option label="草稿" value="draft" />
        <el-option label="已上传" value="uploaded" />
        <el-option label="处理中" value="processing" />
        <el-option label="已完成" value="done" />
        <el-option label="失败" value="failed" />
      </el-select>
      <el-button type="primary" @click="$router.push('/meetings/create')">新建会议</el-button>
    </div>

    <el-table :data="meetings" v-loading="loading" border style="margin-top: var(--space-4)">
      <el-table-column prop="title" label="会议标题" min-width="200">
        <template #default="{ row }">
          <el-link type="primary" @click="$router.push(`/meetings/${row.id}`)">
            {{ row.title }}
          </el-link>
        </template>
      </el-table-column>
      <el-table-column label="类型" width="120">
        <template #default="{ row }">{{ meetingTypeLabel(row.meeting_type) }}</template>
      </el-table-column>
      <el-table-column label="会议时间" width="180">
        <template #default="{ row }">
          {{ row.meeting_time ? formatDate(row.meeting_time) : '-' }}
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusTagType(row.status)">{{ statusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="创建时间" width="180">
        <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="100" fixed="right">
        <template #default="{ row }">
          <el-popconfirm title="确定删除该会议？" @confirm="handleDelete(row.id)">
            <template #reference>
              <el-button type="danger" size="small" link>删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      v-if="total > 0"
      style="margin-top: var(--space-4); justify-content: flex-end"
      layout="total, prev, pager, next"
      :total="total"
      :page-size="pageSize"
      :current-page="page"
      @current-change="handlePageChange"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { listMeetings, deleteMeeting, type Meeting } from '@/api/meetings'

const meetings = ref<Meeting[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = 20
const keyword = ref('')
const statusFilter = ref('')
const loading = ref(false)

const MEETING_TYPE_LABELS: Record<string, string> = {
  presales: '售前交流',
  project: '项目推进',
  technical: '技术方案',
  bidding: '招投标沟通',
  other: '其他',
}

async function fetchMeetings() {
  loading.value = true
  try {
    const res = await listMeetings({
      keyword: keyword.value || undefined,
      status: statusFilter.value || undefined,
      page: page.value,
      page_size: pageSize,
    })
    meetings.value = res.items
    total.value = res.total
  } finally {
    loading.value = false
  }
}

async function handleDelete(id: string) {
  await deleteMeeting(id)
  ElMessage.success('已删除')
  fetchMeetings()
}

function handlePageChange(p: number) {
  page.value = p
  fetchMeetings()
}

function meetingTypeLabel(t: string | null) {
  if (!t) return '-'
  return MEETING_TYPE_LABELS[t] ?? t
}

function formatDate(d: string) {
  return new Date(d).toLocaleString('zh-CN', { hour12: false })
}

function statusLabel(s: string) {
  const map: Record<string, string> = {
    draft: '草稿', uploaded: '已上传', processing: '处理中', done: '已完成', failed: '失败',
  }
  return map[s] ?? s
}

function statusTagType(s: string): 'info' | 'warning' | 'success' | 'danger' | '' {
  const map: Record<string, 'info' | 'warning' | 'success' | 'danger' | ''> = {
    draft: 'info', uploaded: '', processing: 'warning', done: 'success', failed: 'danger',
  }
  return map[s] ?? 'info'
}

onMounted(fetchMeetings)
</script>

<style scoped>
.meeting-list {
  padding: var(--space-6);
}
.toolbar {
  display: flex;
  gap: var(--space-3);
  align-items: center;
}
</style>
