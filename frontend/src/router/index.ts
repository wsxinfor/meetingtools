import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import MeetingListView from '@/views/MeetingListView.vue'
import MeetingCreateView from '@/views/MeetingCreateView.vue'
import MeetingDetailView from '@/views/MeetingDetailView.vue'
import TermsView from '@/views/TermsView.vue'
import TemplatesView from '@/views/TemplatesView.vue'
import LlmConfigsView from '@/views/LlmConfigsView.vue'
import LoginView from '@/views/LoginView.vue'
import UsersView from '@/views/UsersView.vue'
import CustomersView from '@/views/CustomersView.vue'
import ProjectsView from '@/views/ProjectsView.vue'
import RecordView from '@/views/RecordView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', component: LoginView, meta: { public: true } },
    { path: '/', redirect: '/meetings' },
    { path: '/home', component: HomeView },
    { path: '/record', component: RecordView },
    { path: '/meetings', component: MeetingListView },
    { path: '/meetings/create', component: MeetingCreateView },
    { path: '/meetings/:id', component: MeetingDetailView },
    { path: '/terms', component: TermsView },
    { path: '/templates', component: TemplatesView },
    { path: '/customers', component: CustomersView },
    { path: '/projects', component: ProjectsView },
    { path: '/llm-configs', component: LlmConfigsView },
    { path: '/users', component: UsersView, meta: { requireAdmin: true } },
  ],
})

router.beforeEach((to) => {
  const token = localStorage.getItem('mt_token')
  if (!to.meta.public && !token) {
    return '/login'
  }
  // Admin-only routes: non-admin users get redirected to /meetings
  if (to.meta.requireAdmin) {
    const raw = localStorage.getItem('mt_user')
    const user = raw ? JSON.parse(raw) : null
    if (!user || user.role !== 'admin') {
      return '/meetings'
    }
  }
  return true
})

export default router
