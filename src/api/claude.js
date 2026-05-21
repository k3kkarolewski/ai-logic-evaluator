export async function fetchModelC(prompt) {
  const response = await fetch('/api/model-c', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt: prompt.trim() }),
  })

  const data = await response.json().catch(() => ({}))

  if (!response.ok) {
    const detail =
      typeof data.detail === 'string'
        ? data.detail
        : Array.isArray(data.detail)
          ? data.detail.map((e) => e.msg).join(', ')
          : response.statusText
    throw new Error(detail || 'Nie udało się pobrać odpowiedzi z API.')
  }

  return data.response
}
