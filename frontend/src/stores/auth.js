import { defineStore } from 'pinia'
import client from '../api/client'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('user') || 'null'),
    loading: false,
  }),
  getters: {
    isAuthenticated: (state) => !!state.user,
    role: (state) => state.user?.role || null,
  },
  actions: {
    async login(payload) {
      this.loading = true
      try {
        const { data } = await client.post('auth/login/', payload)
        localStorage.setItem('access', data.access)
        localStorage.setItem('refresh', data.refresh)
        localStorage.setItem('user', JSON.stringify(data.user))
        this.user = data.user
        return data.user
      } finally {
        this.loading = false
      }
    },
    logout() {
      localStorage.removeItem('access')
      localStorage.removeItem('refresh')
      localStorage.removeItem('user')
      this.user = null
    },
  },
})
