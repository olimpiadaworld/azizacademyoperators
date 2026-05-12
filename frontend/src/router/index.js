import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/auth/LoginView.vue'
import AdminDashboard from '../views/admin/AdminDashboard.vue'
import BossDashboard from '../views/boss/BossDashboard.vue'
import OperatorDashboard from '../views/operator/OperatorDashboard.vue'
import DashboardLayout from '../layouts/DashboardLayout.vue'
import LeadCaptureView from '../views/public/LeadCaptureView.vue'

const routes = [
  { path: '/login', name: 'login', component: LoginView },
  { path: '/lead', name: 'lead-capture', component: LeadCaptureView },
  {
    path: '/',
    component: DashboardLayout,
    meta: { requiresAuth: true },
    children: [
      { path: 'admin', component: AdminDashboard, meta: { role: 'admin' } },
      { path: 'boss', component: BossDashboard, meta: { role: ['boss', 'filial_rahbari'] } },
      { path: 'operator', component: OperatorDashboard, meta: { role: 'operator' } },
    ],
  },
  { path: '/:pathMatch(.*)*', redirect: '/login' },
]

const router = createRouter({ history: createWebHistory(), routes })

function getHomePath(user) {
  if (!user?.role) return '/login'
  if (user.role === 'boss' || user.role === 'filial_rahbari') return { path: '/boss', query: { tab: 'leads' } }
  if (user.role === 'operator') return { path: '/operator', query: { tab: 'general' } }
  return `/${user.role}`
}

router.beforeEach((to) => {
  const user = JSON.parse(localStorage.getItem('user') || 'null')
  if (to.path === '/' && user) return getHomePath(user)
  if (to.meta.requiresAuth && !user) return '/login'
  if (to.meta.role) {
    const allowedRoles = Array.isArray(to.meta.role) ? to.meta.role : [to.meta.role]
    if (!allowedRoles.includes(user?.role)) {
      return getHomePath(user)
    }
  }
  if (to.path === '/login' && user) return getHomePath(user)
})

export default router
