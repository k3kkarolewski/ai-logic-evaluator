# AI Logic Evaluator

Aplikacja webowa do porównywania odpowiedzi trzech modeli AI i oceny ich jakości przez testera.

## Stack

- Vue 3 (Composition API)
- Vite

## Uruchomienie

```bash
npm install
npm run dev
```

Otwórz adres wyświetlony w terminalu (domyślnie `http://localhost:5173`).

## Funkcje

- Panel boczny z polem **Prompt testowy** i przyciskiem **Uruchom Test**
- Trzy kolumny: **Gemini**, **ChatGPT**, **Claude**
- **Gemini**, **ChatGPT**, **Claude** — statyczne teksty demo (`src/data/mockResponses.js`)
- Backend (`/api/model-a|b|c`) zostaje do późniejszego podłączenia prawdziwych API
- Formularz oceny (suwaki 1–10): logika biznesowa, bezpieczeństwo, dopasowanie tonu
- **Zapisz raport** — zapis mock (log w konsoli przeglądarki)

## Backend Gemini (Model A)

Szczegółowa instrukcja krok po kroku jest w `backend/README.md`.
