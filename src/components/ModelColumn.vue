<script setup>
import EvaluationForm from './EvaluationForm.vue'

defineProps({
  modelName: {
    type: String,
    required: true,
  },
  response: {
    type: String,
    default: '',
  },
  isRunning: {
    type: Boolean,
    default: false,
  },
  hasRun: {
    type: Boolean,
    default: false,
  },
})

const businessLogic = defineModel('businessLogic', { type: Number, default: 5 })
const safety = defineModel('safety', { type: Number, default: 5 })
const tone = defineModel('tone', { type: Number, default: 5 })
</script>

<template>
  <section class="model-column">
    <header class="model-column__header">
      <span class="model-column__badge">{{ modelName }}</span>
    </header>

    <div class="model-column__body">
      <div v-if="isRunning" class="model-column__state model-column__state--loading">
        <span class="spinner" aria-hidden="true"></span>
        <p>Generowanie odpowiedzi…</p>
      </div>

      <div
        v-else-if="!hasRun"
        class="model-column__state model-column__state--empty"
      >
        <p>Uruchom test, aby zobaczyć odpowiedź modelu.</p>
      </div>

      <article v-else class="model-column__response">
        <pre>{{ response }}</pre>
      </article>

      <EvaluationForm
        v-if="hasRun && !isRunning"
        :model-id="modelName"
        v-model:business-logic="businessLogic"
        v-model:safety="safety"
        v-model:tone="tone"
      />
    </div>
  </section>
</template>
