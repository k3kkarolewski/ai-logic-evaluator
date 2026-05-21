<script setup>
import { ref, reactive } from 'vue'
import PromptSidebar from './components/PromptSidebar.vue'
import ModelColumn from './components/ModelColumn.vue'
import { MODELS } from './constants/models.js'
import { MOCK_RESPONSES } from './data/mockResponses.js'

const prompt = ref('')
const isRunning = ref(false)
const hasRun = ref(false)
const responses = reactive(
  Object.fromEntries(MODELS.map((name) => [name, ''])),
)
const scores = reactive(
  Object.fromEntries(
    MODELS.map((name) => [
      name,
      { businessLogic: 5, safety: 5, tone: 5 },
    ]),
  ),
)

const reportMessage = ref('')
const reportStatus = ref('')

async function runTest() {
  if (!prompt.value.trim() || isRunning.value) return

  isRunning.value = true
  hasRun.value = false
  reportMessage.value = ''
  reportStatus.value = ''

  for (const name of MODELS) {
    responses[name] = ''
  }

  const loadResponses = new Promise((resolve) => {
    setTimeout(() => {
      for (const name of MODELS) {
        responses[name] = MOCK_RESPONSES[name]
      }
      resolve()
    }, 600)
  })

  try {
    await loadResponses
    hasRun.value = true
  } finally {
    isRunning.value = false
  }
}

function saveReport() {
  if (!hasRun.value) {
    reportStatus.value = 'error'
    reportMessage.value = 'Najpierw uruchom test i oceń odpowiedzi modeli.'
    return
  }

  const report = {
    timestamp: new Date().toISOString(),
    prompt: prompt.value.trim(),
    evaluations: MODELS.map((name) => ({
      model: name,
      response: responses[name],
      scores: { ...scores[name] },
    })),
  }

  console.log('[AI Logic Evaluator] Raport:', report)

  reportStatus.value = 'success'
  reportMessage.value =
    'Raport zapisany (mock). Szczegóły w konsoli przeglądarki (F12).'
}
</script>

<template>
  <div class="app-shell">
    <PromptSidebar
      v-model:prompt="prompt"
      :is-running="isRunning"
      @run-test="runTest"
    />

    <main class="main-panel">
      <header class="main-panel__header">
        <h2>Wyniki modeli</h2>
        <p v-if="hasRun" class="main-panel__meta">
          Prompt: „{{ prompt.trim().slice(0, 80)
          }}{{ prompt.trim().length > 80 ? '…' : '' }}”
        </p>
      </header>

      <div class="models-grid">
        <ModelColumn
          v-for="name in MODELS"
          :key="name"
          :model-name="name"
          :response="responses[name]"
          :is-running="isRunning"
          :has-run="hasRun"
          v-model:business-logic="scores[name].businessLogic"
          v-model:safety="scores[name].safety"
          v-model:tone="scores[name].tone"
        />
      </div>

      <footer class="main-panel__footer">
        <p
          v-if="reportMessage"
          class="report-toast"
          :class="`report-toast--${reportStatus}`"
          role="status"
        >
          {{ reportMessage }}
        </p>
        <button
          type="button"
          class="btn btn--secondary"
          :disabled="!hasRun"
          @click="saveReport"
        >
          Zapisz raport
        </button>
      </footer>
    </main>
  </div>
</template>
