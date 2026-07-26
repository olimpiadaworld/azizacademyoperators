<template>
  <section class="pwa-install-card" :class="{ 'is-installed': installed }" aria-label="Dasturni telefonga o‘rnatish">
    <div class="pwa-install-card__icon" aria-hidden="true">
      <svg viewBox="0 0 24 24">
        <rect x="7" y="2.75" width="10" height="18.5" rx="2.25" />
        <path d="M10.25 5.75h3.5M11.25 18.25h1.5" />
      </svg>
    </div>

    <div class="pwa-install-card__content">
      <strong>Dasturni telefon ekraniga o‘rnating</strong>
      <span>Panelni iPhone yoki Android’da alohida ilova kabi oching.</span>
    </div>

    <button
      class="pwa-install-card__action"
      :class="{ 'is-installed': installed }"
      type="button"
      :disabled="installed"
      @click="requestInstall"
    >
      <svg v-if="installed" viewBox="0 0 24 24" aria-hidden="true">
        <circle cx="12" cy="12" r="8.5" />
        <path d="m8.7 12.1 2.15 2.15 4.55-4.75" />
      </svg>
      <svg v-else viewBox="0 0 24 24" aria-hidden="true">
        <path d="M12 3v11m0 0 4-4m-4 4-4-4M5 16v2.5A2.5 2.5 0 0 0 7.5 21h9a2.5 2.5 0 0 0 2.5-2.5V16" />
      </svg>
      <span>{{ installed ? 'Ilova o‘rnatilgan' : 'Ilovani o‘rnatish' }}</span>
    </button>
  </section>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'

const installed = ref(false)
let displayModeQuery = null

function detectInstalled() {
  return window.matchMedia('(display-mode: standalone)').matches
    || window.navigator.standalone === true
}

function syncInstalledState() {
  installed.value = detectInstalled()
}

function requestInstall() {
  if (installed.value) return
  window.dispatchEvent(new CustomEvent('aziz:install-app'))
}

onMounted(() => {
  syncInstalledState()
  displayModeQuery = window.matchMedia('(display-mode: standalone)')
  displayModeQuery.addEventListener?.('change', syncInstalledState)
  window.addEventListener('appinstalled', syncInstalledState)
})

onBeforeUnmount(() => {
  displayModeQuery?.removeEventListener?.('change', syncInstalledState)
  window.removeEventListener('appinstalled', syncInstalledState)
})
</script>
