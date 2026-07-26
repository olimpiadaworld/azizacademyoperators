<template>
  <Teleport to="body">
    <button
      v-if="showInstallButton"
      class="pwa-install-button"
      type="button"
      aria-label="Dasturni telefonga o‘rnatish"
      title="Dasturni telefonga o‘rnatish"
      :disabled="installBusy"
      @click="installApp"
    >
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <path d="M12 3v11m0 0 4-4m-4 4-4-4M5 16v2.5A2.5 2.5 0 0 0 7.5 21h9a2.5 2.5 0 0 0 2.5-2.5V16" />
      </svg>
      <span>{{ installBusy ? 'Kutilmoqda...' : 'O‘rnatish' }}</span>
    </button>

    <div
      v-if="guideOpen"
      class="pwa-guide-backdrop"
      role="presentation"
      @click.self="closeGuide"
    >
      <section class="pwa-guide" role="dialog" aria-modal="true" aria-labelledby="pwa-guide-title">
        <button class="pwa-guide__close" type="button" aria-label="Yopish" @click="closeGuide">×</button>

        <div class="pwa-guide__logo" aria-hidden="true">A</div>
        <h2 id="pwa-guide-title">Dasturni telefonga o‘rnatish</h2>

        <ol v-if="isIOS" class="pwa-guide__steps">
          <li>Saytni <strong>Safari</strong> brauzerida oching.</li>
          <li>Pastdagi <strong>Ulashish</strong> tugmasini bosing.</li>
          <li><strong>“Add to Home Screen”</strong> yoki <strong>“Bosh ekranga qo‘shish”</strong>ni tanlang.</li>
          <li><strong>Add / Qo‘shish</strong> tugmasini bosing.</li>
        </ol>

        <ol v-else class="pwa-guide__steps">
          <li>Saytni <strong>Google Chrome</strong> brauzerida oching.</li>
          <li>Yuqoridagi <strong>⋮</strong> menyuni bosing.</li>
          <li><strong>“Install app”</strong> yoki <strong>“Bosh ekranga qo‘shish”</strong>ni tanlang.</li>
          <li><strong>O‘rnatish</strong> tugmasini tasdiqlang.</li>
        </ol>

        <p class="pwa-guide__note">
          O‘rnatilgandan keyin dastur telefon ekranida alohida ikonka bilan chiqadi va ilova kabi ochiladi.
        </p>

        <button class="pwa-guide__done" type="button" @click="closeGuide">Tushunarli</button>
      </section>
    </div>
  </Teleport>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

const deferredPrompt = ref(null)
const guideOpen = ref(false)
const installBusy = ref(false)
const installed = ref(false)
const mobileDevice = ref(false)
const isIOS = ref(false)

const showInstallButton = computed(() => mobileDevice.value && !installed.value)

function detectInstalled() {
  return window.matchMedia('(display-mode: standalone)').matches
    || window.navigator.standalone === true
}

function detectMobile() {
  const agent = window.navigator.userAgent || ''
  return /Android|iPhone|iPad|iPod|Mobile/i.test(agent)
    || window.matchMedia('(max-width: 900px)').matches
}

function handleBeforeInstallPrompt(event) {
  event.preventDefault()
  deferredPrompt.value = event
}

function handleInstalled() {
  installed.value = true
  deferredPrompt.value = null
  guideOpen.value = false
}

async function installApp() {
  if (installBusy.value) return

  if (!deferredPrompt.value) {
    guideOpen.value = true
    return
  }

  installBusy.value = true
  try {
    deferredPrompt.value.prompt()
    const choice = await deferredPrompt.value.userChoice
    if (choice?.outcome === 'accepted') {
      installed.value = true
    }
    deferredPrompt.value = null
  } catch (error) {
    console.error('Ilovani o‘rnatish oynasini ochib bo‘lmadi:', error)
    guideOpen.value = true
  } finally {
    installBusy.value = false
  }
}

function closeGuide() {
  guideOpen.value = false
}

onMounted(() => {
  const agent = window.navigator.userAgent || ''
  isIOS.value = /iPhone|iPad|iPod/i.test(agent)
    || (window.navigator.platform === 'MacIntel' && window.navigator.maxTouchPoints > 1)
  mobileDevice.value = detectMobile()
  installed.value = detectInstalled()

  window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt)
  window.addEventListener('appinstalled', handleInstalled)
})

onBeforeUnmount(() => {
  window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt)
  window.removeEventListener('appinstalled', handleInstalled)
})
</script>
