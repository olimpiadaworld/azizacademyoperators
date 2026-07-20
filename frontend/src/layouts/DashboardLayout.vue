<template>
  <div class="dashboard">
    <header class="dashboard-nav">
      <div class="dashboard-nav__top">
        <RouterLink
          :to="homePath"
          class="dashboard-nav__brand"
          title="Bosh sahifaga qaytish"
          aria-label="Bosh sahifaga qaytish"
          @click.prevent="goHome"
        >
          <span class="dashboard-nav__dot"></span>
          <div>
            <div>AZIZ ACADEMY</div>
            <small>Lead boshqaruvi</small>
          </div>
        </RouterLink>

        <button
          class="dashboard-nav__toggle"
          type="button"
          @click="toggleMobileMenu"
          :aria-expanded="mobileMenuOpen ? 'true' : 'false'"
          aria-label="Menyuni ochish"
        >
          <span></span>
          <span></span>
          <span></span>
        </button>
      </div>

      <nav class="dashboard-nav__content" :class="{ 'is-open': mobileMenuOpen }">
        <div class="dashboard-nav__links">
          <RouterLink
            v-for="item in links"
            :key="item.label"
            :to="item.to"
            class="dashboard-nav__link"
            :class="{ 'is-active': isLinkActive(item) }"
            @click="closeMobileMenu"
          >
            <span v-if="item.icon" class="dashboard-nav__link-icon">{{ item.icon }}</span>
            <span>{{ item.label }}</span>
          </RouterLink>
        </div>

        <button class="dashboard-nav__logout" type="button" @click="logout">Chiqish</button>
      </nav>
    </header>

    <div class="dashboard__body">
      <main class="main">
        <router-view />
      </main>
    </div>

    <TopOperatorCelebration />
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import TopOperatorCelebration from '../components/ui/TopOperatorCelebration.vue'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const mobileMenuOpen = ref(false)

const bossCurrentTab = computed(() => {
  const allowed = auth.role === 'filial_rahbari'
    ? ['leads', 'manager', 'payment']
    : ['leads', 'operators', 'manager', 'payment', 'online', 'accounting', 'incoming']
  const tab = typeof route.query.tab === 'string' ? route.query.tab : 'leads'
  return allowed.includes(tab) ? tab : 'leads'
})


const operatorCurrentTab = computed(() => {
  const tab = typeof route.query.tab === 'string' ? route.query.tab : 'general'
  return ['general', 'assigned', 'incoming', 'timed', 'report'].includes(tab) ? tab : 'general'
})

const adminCurrentTab = computed(() => {
  const tab = typeof route.query.tab === 'string' ? route.query.tab : 'main'
  return ['main', 'database'].includes(tab) ? tab : 'main'
})

const links = computed(() => {
  if (auth.role === 'boss') {
    return [
      { to: { path: '/boss', query: { tab: 'leads' } }, label: 'Leadlar', tab: 'leads' },
      { to: { path: '/boss', query: { tab: 'operators' } }, label: 'Operatorlar', tab: 'operators' },
      { to: { path: '/boss', query: { tab: 'incoming' } }, label: "Kiruvchi qo'ng'iroqlar", tab: 'incoming' },
      { to: { path: '/boss', query: { tab: 'manager' } }, label: 'Menenjerlar nazorati', tab: 'manager' },
      { to: { path: '/boss', query: { tab: 'payment' } }, label: "Keldi/To'lov", tab: 'payment' },
      { to: { path: '/boss', query: { tab: 'online' } }, label: 'Online leadlar', tab: 'online' },
      { to: { path: '/boss', query: { tab: 'accounting' } }, label: 'Hisob kitob', tab: 'accounting' },
      { to: { path: '/boss', query: { tab: bossCurrentTab.value, action: 'daily-report' } }, label: 'Kunlik hisobot', action: 'daily-report' },
      { to: { path: '/boss', query: { tab: bossCurrentTab.value, action: 'full-report' } }, label: "To'liq hisobot", action: 'full-report' },
      { to: { path: '/boss', query: { tab: bossCurrentTab.value, action: 'create-operator' } }, label: 'Operator yaratish', action: 'create-operator' },
    ]
  }
  if (auth.role === 'filial_rahbari') {
    return [
      { to: { path: '/boss', query: { tab: 'leads' } }, label: 'Leadlar', tab: 'leads' },
      { to: { path: '/boss', query: { tab: 'manager' } }, label: 'Menenjer nazorati', tab: 'manager' },
      { to: { path: '/boss', query: { tab: 'payment' } }, label: "Keldi/To'lov", tab: 'payment' },
    ]
  }
  if (auth.role === 'admin') return [
    { to: { path: '/admin', query: { tab: 'main' } }, label: 'Admin paneli', tab: 'main' },
    { to: { path: '/admin', query: { tab: 'database' } }, label: "Ma'lumotlar bazasi", tab: 'database' },
  ]
  if (auth.role === 'director' || auth.role === 'director_deputy') return [
    { to: { path: '/director' }, label: 'Umumiy nazorat', icon: '📊' },
  ]
  return [
    { to: { path: '/operator', query: { tab: 'general' } }, label: 'Leadlar', tab: 'general', icon: '👥' },
    { to: { path: '/operator', query: { tab: 'assigned' } }, label: 'Biriktirilgan leadlar', tab: 'assigned', icon: '👪' },
    { to: { path: '/operator', query: { tab: 'incoming' } }, label: "Kiruvchi qo'ng'iroqlar", tab: 'incoming', icon: '📞' },
    { to: { path: '/operator', query: { tab: 'timed' } }, label: "Vaqt qo'yilganlar", tab: 'timed', icon: '📅' },
    { to: { path: '/operator', query: { tab: 'report' } }, label: 'Kunlik hisobot', tab: 'report', icon: '▣' },
  ]
})

const homePath = computed(() => {
  if (auth.role === 'boss' || auth.role === 'filial_rahbari') {
    return { path: '/boss', query: { tab: 'leads' } }
  }
  if (auth.role === 'operator') {
    return { path: '/operator', query: { tab: 'general' } }
  }
  if (auth.role === 'director' || auth.role === 'director_deputy') {
    return { path: '/director' }
  }
  return links.value[0]?.to || '/login'
})

function isLinkActive(item) {
  if (auth.role === 'boss' || auth.role === 'filial_rahbari') {
    return item.tab ? bossCurrentTab.value === item.tab : false
  }
  if (auth.role === 'operator') {
    return item.tab ? operatorCurrentTab.value === item.tab : false
  }
  if (auth.role === 'admin') {
    return item.tab ? adminCurrentTab.value === item.tab : false
  }
  return route.path === (typeof item.to === 'string' ? item.to : item.to?.path)
}

function toggleMobileMenu() {
  mobileMenuOpen.value = !mobileMenuOpen.value
}

function closeMobileMenu() {
  mobileMenuOpen.value = false
}

function goHome() {
  closeMobileMenu()
  router.push(homePath.value)
}

function logout() {
  closeMobileMenu()
  auth.logout()
  router.push('/login')
}
</script>
