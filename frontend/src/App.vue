<template>
  <el-config-provider>
    <template v-if="$route.path === '/login'">
      <router-view />
    </template>

    <div v-else class="app-layout">
      <!-- 侧边栏 -->
      <aside class="app-sidebar">
        <div class="sidebar-brand" @click="handleTitleClick">
          <span class="brand-name">会议记录工具</span>
          <span class="brand-sub">Meeting Tools</span>
        </div>

        <nav class="sidebar-nav">
          <!-- 核心功能分组 -->
          <div class="nav-group-label">核心功能</div>
          <router-link
            v-for="item in coreNavItems"
            :key="item.path"
            :to="item.path"
            class="nav-item"
            :class="{ 'is-active': isActive(item.path) }"
          >
            {{ item.label }}
          </router-link>

          <!-- 配置管理分组 -->
          <div class="nav-group-label">配置管理</div>
          <router-link
            v-for="item in configNavItems"
            :key="item.path"
            :to="item.path"
            class="nav-item"
            :class="{ 'is-active': isActive(item.path) }"
          >
            {{ item.label }}
          </router-link>
        </nav>

        <div class="sidebar-footer">
          <div v-if="authStore.isLoggedIn" class="user-block">
            <div class="user-meta">
              <span class="username">{{ authStore.user?.username }}</span>
              <el-tag v-if="authStore.isAdmin" size="small" class="role-tag">
                管理员
              </el-tag>
            </div>
            <button class="logout-btn" @click="handleLogout">退出登录</button>
          </div>
        </div>
      </aside>

      <!-- 主内容区 -->
      <div class="app-main">
        <!-- 顶部栏 -->
        <header class="app-topbar">
          <div class="topbar-title">
            <h1 class="topbar-heading">{{ currentTitle }}</h1>
          </div>
        </header>

        <!-- 页面内容 -->
        <div class="app-content">
          <router-view :key="viewKey" />
        </div>
      </div>
    </div>
  </el-config-provider>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/useAuthStore'
import { useRouter, useRoute } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()

const viewKey = ref(0)

const coreNavItems = computed(() => [
  { path: '/record', label: '开始录音' },
  { path: '/meetings', label: '会议列表' },
])

const configNavItems = computed(() => {
  const items = [
    { path: '/customers', label: '客户管理' },
    { path: '/projects', label: '项目管理' },
    { path: '/terms', label: '术语库' },
    { path: '/templates', label: '纪要模板' },
    { path: '/llm-configs', label: 'LLM 配置' },
  ]
  if (authStore.isAdmin) {
    items.push({ path: '/users', label: '用户管理' })
  }
  return items
})

const currentTitle = computed(() => {
  const map: Record<string, string> = {
    '/record': '录音工作台',
    '/meetings': '会议列表',
    '/customers': '客户管理',
    '/projects': '项目管理',
    '/terms': '术语库',
    '/templates': '纪要模板',
    '/llm-configs': 'LLM 配置',
    '/users': '用户管理',
  }
  const base = '/' + (route.path.split('/')[1] || '')
  return map[base] || '会议记录工具'
})

function isActive(path: string): boolean {
  return route.path === path || route.path.startsWith(path + '/')
}

function handleTitleClick() {
  if (route.path === '/meetings') {
    viewKey.value++
  } else {
    router.push('/meetings')
  }
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
/* ── 整体框架 ── */
.app-layout {
  display: flex;
  min-height: 100vh;
}

/* ── 侧边栏 ── */
.app-sidebar {
  width: var(--meeting-sidebar-width);
  min-height: 100vh;
  background: var(--meeting-bg-sidebar);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  position: sticky;
  top: 0;
  height: 100vh;
  overflow: hidden;
}

/* Logo 区 */
.sidebar-brand {
  padding: var(--meeting-space-4);
  padding-bottom: var(--meeting-space-3);
  border-bottom: 0.5px solid var(--meeting-color-primary);
  cursor: pointer;
  user-select: none;
}

.brand-name {
  display: block;
  font-size: var(--meeting-font-size-base);
  font-weight: var(--meeting-font-weight-medium);
  color: var(--meeting-text-sidebar-active);
  line-height: var(--meeting-line-height-tight);
}

.brand-sub {
  display: block;
  font-size: var(--meeting-font-size-xs);
  font-weight: var(--meeting-font-weight-normal);
  color: var(--meeting-color-primary-light);
  margin-top: var(--meeting-space-1);
}

/* 导航分组标签 */
.nav-group-label {
  font-size: var(--meeting-font-size-xs);
  font-weight: var(--meeting-font-weight-medium);
  color: var(--meeting-text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  padding: var(--meeting-space-3) var(--meeting-space-4) var(--meeting-space-1);
}

/* 导航菜单 */
.sidebar-nav {
  flex: 1;
  padding: var(--meeting-space-2) 0;
  overflow-y: auto;
}

.nav-item {
  display: block;
  padding: 7px var(--meeting-space-4);
  padding-left: var(--meeting-space-4);
  font-size: var(--meeting-font-size-base);
  font-weight: var(--meeting-font-weight-normal);
  color: var(--meeting-text-sidebar);
  text-decoration: none;
  border-left: 2px solid transparent;
  transition: color var(--meeting-transition-fast),
              background var(--meeting-transition-fast);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.nav-item:hover {
  color: var(--meeting-text-sidebar-active);
  background: var(--meeting-bg-sidebar-hover);
}

.nav-item.is-active {
  color: var(--meeting-text-sidebar-active);
  background: var(--meeting-bg-sidebar-active);
  border-left-color: var(--meeting-color-primary-light);
  font-weight: var(--meeting-font-weight-medium);
  padding-left: 14px;
}

/* 底部用户区 */
.sidebar-footer {
  border-top: 0.5px solid var(--meeting-color-primary);
  padding: var(--meeting-space-3) var(--meeting-space-4);
}

.user-block {
  display: flex;
  flex-direction: column;
  gap: var(--meeting-space-2);
}

.user-meta {
  display: flex;
  align-items: center;
  gap: var(--meeting-space-1);
  min-width: 0;
}

.username {
  font-size: var(--meeting-font-size-sm);
  color: var(--meeting-text-sidebar);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.role-tag {
  flex-shrink: 0;
}

.logout-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: var(--meeting-font-size-sm);
  color: var(--meeting-text-tertiary);
  padding: 0;
  text-align: left;
  font-family: inherit;
  transition: color var(--meeting-transition-fast);
}

.logout-btn:hover {
  color: var(--meeting-color-danger);
}

/* ── 主内容区 ── */
.app-main {
  flex: 1;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--meeting-bg-base);
}

/* 顶部栏 */
.app-topbar {
  height: var(--meeting-topbar-height);
  background: var(--meeting-bg-surface);
  border-bottom: 0.5px solid var(--meeting-border-light);
  display: flex;
  align-items: center;
  padding: 0 var(--meeting-space-6);
  flex-shrink: 0;
}

.topbar-title {
  display: flex;
  align-items: baseline;
  gap: var(--meeting-space-2);
}

.topbar-heading {
  font-size: var(--meeting-font-size-md);
  font-weight: var(--meeting-font-weight-medium);
  color: var(--meeting-text-primary);
  margin: 0;
  line-height: var(--meeting-line-height-tight);
}

/* 页面内容区 */
.app-content {
  flex: 1;
  padding: var(--meeting-space-6);
  max-width: 1200px;
  width: 100%;
  overflow-y: auto;
}
</style>
