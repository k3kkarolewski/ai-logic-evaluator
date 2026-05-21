<script setup>
import {
  ref,
  computed,
  watch,
  onMounted,
  onUnmounted,
  nextTick,
  useTemplateRef,
} from 'vue'

defineProps({
  id: {
    type: String,
    required: true,
  },
  label: {
    type: String,
    required: true,
  },
})

const value = defineModel({
  type: Number,
  default: 5,
})

const SLIDER_MIN = 1
const SLIDER_MAX = 10

const sliderRef = useTemplateRef('slider')
const wrapRef = useTemplateRef('wrap')
const measuredFillPx = ref(null)

function getRatio() {
  return (Number(value.value) - SLIDER_MIN) / (SLIDER_MAX - SLIDER_MIN)
}

function syncFillWidth() {
  const input = sliderRef.value
  if (!input) return

  const trackWidth = input.getBoundingClientRect().width
  if (trackWidth <= 0) return

  const thumbSize =
    parseFloat(getComputedStyle(input).getPropertyValue('--slider-thumb-size')) || 24
  measuredFillPx.value = getRatio() * (trackWidth - thumbSize) + thumbSize / 2
}

function scheduleSync() {
  syncFillWidth()
  nextTick(() => {
    syncFillWidth()
    requestAnimationFrame(() => {
      syncFillWidth()
      requestAnimationFrame(syncFillWidth)
    })
  })
}

const fillStyle = computed(() => {
  const ratio = getRatio()

  if (measuredFillPx.value != null && measuredFillPx.value > 0) {
    return { width: `${measuredFillPx.value}px` }
  }

  return {
    width: `calc((100% - var(--slider-thumb-size)) * ${ratio} + var(--slider-thumb-size) / 2)`,
  }
})

let resizeObserver

onMounted(() => {
  scheduleSync()

  const target = wrapRef.value ?? sliderRef.value
  if (!target || typeof ResizeObserver === 'undefined') return

  resizeObserver = new ResizeObserver(scheduleSync)
  resizeObserver.observe(target)
})

onUnmounted(() => {
  resizeObserver?.disconnect()
})

watch(value, scheduleSync, { flush: 'post' })
</script>

<template>
  <div class="evaluation-form__row">
    <div class="evaluation-form__label-row">
      <label :for="id">{{ label }}</label>
      <span class="evaluation-form__value">{{ value }}</span>
    </div>
    <div ref="wrap" class="evaluation-slider-wrap">
      <div class="evaluation-slider__track" aria-hidden="true">
        <div class="evaluation-slider__fill" :style="fillStyle" />
      </div>
      <input
        :id="id"
        ref="slider"
        v-model.number="value"
        type="range"
        class="evaluation-slider"
        :min="SLIDER_MIN"
        :max="SLIDER_MAX"
        step="1"
        @input="syncFillWidth"
      />
    </div>
    <div class="evaluation-form__scale">
      <span>1</span>
      <span>10</span>
    </div>
  </div>
</template>
