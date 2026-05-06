import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { login as apiLogin, type UserInfo } from '@/api/auth'

const TOKEN_KEY = 'mt_token'
const USER_KEY = 'mt_user'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem(TOKEN_KEY))
  const user = ref<UserInfo | null>((() => {
    const raw = localStorage.getItem(USER_KEY)
    return raw ? (JSON.parse(raw) as UserInfo) : null
  })())

  const isLoggedIn = computed(() => !!token.value && !!user.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  async function login(username: string, password: string): Promise<void> {
    const resp = await apiLogin(username, password)
    token.value = resp.access_token
    user.value = resp.user
    localStorage.setItem(TOKEN_KEY, resp.access_token)
    localStorage.setItem(USER_KEY, JSON.stringify(resp.user))
  }

  function logout(): void {
    token.value = null
    user.value = null
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  }

  return { token, user, isLoggedIn, isAdmin, login, logout }
})
