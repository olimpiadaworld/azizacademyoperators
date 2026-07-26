<template>
  <router-view />
  <InstallAppPrompt :show-floating="false" />
</template>

<script setup>
import InstallAppPrompt from './components/ui/InstallAppPrompt.vue'
</script>
