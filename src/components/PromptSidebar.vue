<script setup>
const prompt = defineModel('prompt', { type: String, default: '' })

defineProps({
  isRunning: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['run-test'])
</script>

<template>
  <aside class="sidebar">
    <div class="sidebar__brand">
      <div class="sidebar__logo" aria-hidden="true">AI</div>
      <div>
        <h1>AI Logic Evaluator</h1>
        <p class="sidebar__subtitle">Porównanie odpowiedzi modeli</p>
      </div>
    </div>

    <label class="sidebar__label" for="test-prompt">Prompt testowy</label>
    <textarea
      id="test-prompt"
      v-model="prompt"
      class="sidebar__textarea"
      placeholder="Wpisz prompt testowy, który zostanie wysłany do Gemini, ChatGPT i Claude…"
      rows="14"
      :disabled="isRunning"
    />

    <button
      type="button"
      class="btn btn--primary sidebar__run"
      :disabled="isRunning || !prompt.trim()"
      @click="emit('run-test')"
    >
      <span v-if="isRunning" class="spinner spinner--sm" aria-hidden="true"></span>
      {{ isRunning ? 'Uruchamianie…' : 'Uruchom Test' }}
    </button>
  </aside>
</template>
