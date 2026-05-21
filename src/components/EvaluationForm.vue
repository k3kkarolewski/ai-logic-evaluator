<script setup>
import RatingSlider from './RatingSlider.vue'

defineProps({
  modelId: {
    type: String,
    required: true,
  },
})

const businessLogic = defineModel('businessLogic', { type: Number, default: 5 })
const safety = defineModel('safety', { type: Number, default: 5 })
const tone = defineModel('tone', { type: Number, default: 5 })
</script>

<template>
  <form class="evaluation-form" @submit.prevent>
    <h3 class="evaluation-form__title">Ocena testera</h3>
    <RatingSlider
      :id="`${modelId}-businessLogic`"
      label="Logika biznesowa"
      v-model="businessLogic"
    />
    <RatingSlider
      :id="`${modelId}-safety`"
      label="Bezpieczeństwo (brak halucynacji)"
      v-model="safety"
    />
    <RatingSlider
      :id="`${modelId}-tone`"
      label="Dopasowanie tonu"
      v-model="tone"
    />
  </form>
</template>
