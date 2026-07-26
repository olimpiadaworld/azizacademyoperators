<template>
  <router-view />
  <InstallAppPrompt :show-floating="showFloatingInstall" />
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import InstallAppPrompt from './components/ui/InstallAppPrompt.vue'

const route = useRoute()

const dashboardPaths = ['/admin', '/boss', '/operator', '/director']
const showFloatingInstall = computed(() => (
  !dashboardPaths.some((path) => route.path === path || route.path.startsWith(`${path}/`))
))
</script>
