<template>
  <div class="panel glass stat-card">
    <div class="stat-card__head">
      <h4>{{ title }}</h4>
      <span class="stat-card__spark"></span>
    </div>
    <strong>{{ value }}</strong>
    <div v-if="subtitle" class="badge muted stat-card__badge">{{ subtitle }}</div>
  </div>
</template>

<script setup>
defineProps({ title: String, value: [String, Number], subtitle: String })
</script>
