import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

export function useViewport(compactBreakpoint = 960, mobileBreakpoint = 640) {
  const width = ref(typeof window !== 'undefined' ? window.innerWidth : 1440)

  const updateWidth = () => {
    if (typeof window === 'undefined') return
    width.value = window.innerWidth
  }

  onMounted(() => {
    updateWidth()
    window.addEventListener('resize', updateWidth, { passive: true })
  })

  onBeforeUnmount(() => {
    if (typeof window === 'undefined') return
    window.removeEventListener('resize', updateWidth)
  })

  const isCompact = computed(() => width.value <= compactBreakpoint)
  const isMobile = computed(() => width.value <= mobileBreakpoint)

  return {
    width,
    isCompact,
    isMobile,
  }
}
