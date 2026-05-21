# Backend — Model A (Gemini), B (ChatGPT), C (Claude)

## Krok 1 — Python

Potrzebujesz **Python 3.10+**:

```powershell
python --version
```

## Krok 2 — Paczki

```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate.bat
pip install -r requirements.txt
```

| Paczka | Po co |
|--------|--------|
| `fastapi` / `uvicorn` | Serwer HTTP |
| `python-dotenv` | Klucze z pliku `.env` |
| `google-genai` | Model A — Gemini |
| `openai` | Model B — ChatGPT |
| `anthropic` | Model C — Claude |

## Krok 3 — Klucze API w `backend/.env`

```powershell
copy .env.example .env
```

Otwórz **`backend/.env`** i uzupełnij:

```env
# Model A — Gemini
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-2.5-flash

# Model B — ChatGPT
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# Model C — Claude
ANTHROPIC_API_KEY=...
ANTHROPIC_MODEL=claude-sonnet-4-20250514
ANTHROPIC_MAX_TOKENS=4096
```

| Model | Skąd klucz |
|-------|------------|
| A (Gemini) | [Google AI Studio](https://aistudio.google.com/apikey) |
| B (ChatGPT) | [OpenAI API Keys](https://platform.openai.com/api-keys) |
| C (Claude) | [Anthropic Console](https://console.anthropic.com/settings/keys) |

**Nie commituj** pliku `.env`.

## Krok 4 — Uruchom backend

```powershell
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Sprawdzenie: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)

- `gemini_configured: true` — Model A gotowy  
- `openai_configured: true` — Model B gotowy  
- `anthropic_configured: true` — Model C gotowy  

## Krok 5 — Frontend (drugi terminal)

```powershell
cd ..
npm run dev
```

## Krok 6 — Test

1. Wpisz prompt → **Uruchom Test**
2. **Model A** — odpowiedź z Gemini  
3. **Model B** — odpowiedź z ChatGPT  
4. **Model C** — odpowiedź z Claude  

## Rozwiązywanie problemów

| Problem | Rozwiązanie |
|---------|-------------|
| `OPENAI_API_KEY` brak | Dodaj klucz do `backend/.env` |
| `401` OpenAI | Sprawdź klucz na platform.openai.com |
| `429` OpenAI / Claude | Limit konta — odczekaj lub doładuj kredyt |
| `401` Claude | Sprawdź `ANTHROPIC_API_KEY` |
| `ANTHROPIC_API_KEY` brak | Dodaj klucz do `backend/.env` |
| `502` Gemini / quota | Użyj `gemini-2.5-flash` w `.env` |
| Błąd połączenia w UI | Backend musi działać na porcie 8000 |
