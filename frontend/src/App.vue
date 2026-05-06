<template>
  <el-config-provider>
    <template v-if="$route.path === '/login'">
      <router-view />
    </template>

    <div v-else class="app-layout">
      <!-- 左侧导航栏 -->
      <aside class="app-sidebar">
        <div class="sidebar-brand" @click="handleTitleClick">
          <span class="brand-icon">◈</span>
          <span class="brand-text">会议记录工具</span>
        </div>

        <nav class="sidebar-nav">
          <router-link
            v-for="item in navItems"
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
              <el-tag v-if="authStore.isAdmin" type="warning" size="small" class="role-tag">
                管理员
              </el-tag>
            </div>
            <button class="logout-btn" @click="handleLogout">退出登录</button>
          </div>
        </div>
      </aside>

      <!-- 右侧内容区 -->
      <main class="app-content">
        <router-view :key="viewKey" />
      </main>
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

const navItems = computed(() => {
  const items = [
    { path: '/record', label: '开始录音' },
    { path: '/meetings', label: '会议列表' },
    { path: '/terms', label: '术语库' },
    { path: '/templates', label: '纪要模板' },
    { path: '/llm-configs', label: 'LLM 配置' },
  ]
  if (authStore.isAdmin) {
    items.push({ path: '/users', label: '用户管理' })
  }
  return items
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

/* ── 左侧导航栏 ── */
.app-sidebar {
  width: 188px;
  min-height: 100vh;
  background: var(--color-bg-card);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  position: sticky;
  top: 0;
  height: 100vh;
  overflow: hidden;
}

/* 品牌标题区 */
.sidebar-brand {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-5) var(--space-4);
  background: var(--color-primary);
  color: #fff;
  cursor: pointer;
  letter-spacing: 0.5px;
  user-select: none;
}

.brand-icon {
  font-size: 18px;
  line-height: 1;
  opacity: 0.85;
}

.brand-text {
  font-size: var(--font-size-body);
  font-weight: var(--font-weight-medium);
  line-height: 1.4;
}

/* 导航菜单 */
.sidebar-nav {
  flex: 1;
  padding: var(--space-3) 0;
  overflow-y: auto;
}

.nav-item {
  display: block;
  padding: var(--space-3) var(--space-5);
  font-size: var(--font-size-body);
  color: var(--color-text-secondary);
  text-decoration: none;
  border-left: 3px solid transparent;
  transition: color 0.15s, background 0.15s, border-color 0.15s;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.nav-item:hover {
  color: var(--color-text-primary);
  background: var(--color-bg-page);
}

.nav-item.is-active {
  color: var(--color-primary);
  background: rgba(92, 138, 120, 0.08);
  border-left-color: var(--color-primary);
  font-weight: var(--font-weight-medium);
}

/* 底部用户区 */
.sidebar-footer {
  border-top: 1px solid var(--color-border);
  padding: var(--space-4);
}

.user-block {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.user-meta {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  min-width: 0;
}

.username {
  font-size: var(--font-size-label);
  color: var(--color-text-secondary);
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
  font-size: var(--font-size-label);
  color: var(--color-text-placeholder);
  padding: 0;
  text-align: left;
  font-family: inherit;
  transition: color 0.15s;
}

.logout-btn:hover {
  color: var(--color-error);
}

/* ── 右侧内容区 ── */
.app-content {
  flex: 1;
  min-height: 100vh;
  overflow-y: auto;
  background: var(--color-bg-page);
}
</style>
