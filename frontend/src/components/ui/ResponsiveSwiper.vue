<template>
  <div class="operator-swiper responsive-swiper" :class="wrapperClass">
    <div class="operator-swiper__head responsive-swiper__head">
      <div class="responsive-swiper__copy">
        <div v-if="eyebrow" class="eyebrow">{{ eyebrow }}</div>
        <strong v-if="title">{{ title }}</strong>
        <div class="operator-swiper__meta">{{ positionLabel }}</div>
      </div>
      <div class="operator-swiper__controls">
        <button class="swiper-arrow" type="button" :disabled="!canPrev" @click="scrollPrev" aria-label="Oldingi slide">←</button>
        <button class="swiper-arrow" type="button" :disabled="!canNext" @click="scrollNext" aria-label="Keyingi slide">→</button>
      </div>
    </div>

    <div ref="viewportRef" class="operator-swiper__viewport responsive-swiper__viewport" @scroll.passive="handleScroll">
      <div class="responsive-swiper__track" :style="trackStyle">
        <div
          v-for="(item, index) in items"
          :key="resolveKey(item, index)"
          class="responsive-swiper__slide"
          :style="slideStyle"
        >
          <slot :item="item" :index="index" />
        </div>
      </div>
    </div>

    <div v-if="pageCount > 1" class="responsive-swiper__dots">
      <button
        v-for="dotIndex in pageCount"
        :key="`dot-${dotIndex}`"
        type="button"
        class="responsive-swiper__dot"
        :class="{ 'is-active': dotIndex - 1 === currentPage }"
        @click="scrollToPage(dotIndex - 1)"
        :aria-label="`Page ${dotIndex}`"
      ></button>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps({
  items: { type: Array, default: () => [] },
  itemKey: { type: [String, Function], default: 'id' },
  eyebrow: { type: String, default: '' },
  title: { type: String, default: '' },
  wrapperClass: { type: [String, Array, Object], default: 'glass-soft' },
  desktopSlides: { type: Number, default: 3 },
  tabletSlides: { type: Number, default: 2 },
  mobileSlides: { type: Number, default: 1 },
  tabletBreakpoint: { type: Number, default: 1100 },
  mobileBreakpoint: { type: Number, default: 640 },
  gap: { type: Number, default: 14 },
})

const viewportRef = ref(null)
const viewportWidth = ref(typeof window !== 'undefined' ? window.innerWidth : 1440)
const scrollLeft = ref(0)

const updateViewportWidth = () => {
  if (typeof window === 'undefined') return
  viewportWidth.value = window.innerWidth
}

const slidesPerView = computed(() => {
  if (viewportWidth.value <= props.mobileBreakpoint) return props.mobileSlides
  if (viewportWidth.value <= props.tabletBreakpoint) return props.tabletSlides
  return props.desktopSlides
})

const pageCount = computed(() => Math.max(1, props.items.length - slidesPerView.value + 1))
const currentPage = computed(() => {
  const viewport = viewportRef.value
  if (!viewport || props.items.length <= slidesPerView.value) return 0
  const step = viewport.clientWidth
  if (!step) return 0
  return Math.min(pageCount.value - 1, Math.max(0, Math.round(scrollLeft.value / step)))
})

const canPrev = computed(() => currentPage.value > 0)
const canNext = computed(() => currentPage.value < pageCount.value - 1)
const positionLabel = computed(() => {
  if (!props.items.length) return '0 / 0'
  const start = currentPage.value + 1
  const end = Math.min(props.items.length, currentPage.value + slidesPerView.value)
  return `${start}-${end} / ${props.items.length}`
})

const trackStyle = computed(() => ({
  gap: `${props.gap}px`,
}))

const slideStyle = computed(() => ({
  flex: `0 0 calc((100% - ${(slidesPerView.value - 1) * props.gap}px) / ${slidesPerView.value})`,
}))

function resolveKey(item, index) {
  if (typeof props.itemKey === 'function') return props.itemKey(item, index)
  return item?.[props.itemKey] ?? index
}

function handleScroll() {
  const viewport = viewportRef.value
  if (!viewport) return
  scrollLeft.value = viewport.scrollLeft
}

function scrollToPage(page) {
  const viewport = viewportRef.value
  if (!viewport) return
  viewport.scrollTo({ left: viewport.clientWidth * page, behavior: 'smooth' })
}

function scrollPrev() {
  scrollToPage(Math.max(0, currentPage.value - 1))
}

function scrollNext() {
  scrollToPage(Math.min(pageCount.value - 1, currentPage.value + 1))
}

watch(() => props.items.length, () => {
  scrollLeft.value = 0
  if (viewportRef.value) viewportRef.value.scrollTo({ left: 0 })
})

onMounted(() => {
  updateViewportWidth()
  handleScroll()
  window.addEventListener('resize', updateViewportWidth, { passive: true })
})

onBeforeUnmount(() => {
  if (typeof window === 'undefined') return
  window.removeEventListener('resize', updateViewportWidth)
})
</script>
