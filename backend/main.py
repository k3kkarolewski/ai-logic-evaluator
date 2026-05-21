import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from google.genai import errors as genai_errors
from anthropic import (
    Anthropic,
    APIConnectionError as AnthropicAPIConnectionError,
    APIStatusError as AnthropicAPIStatusError,
    AuthenticationError as AnthropicAuthenticationError,
    RateLimitError as AnthropicRateLimitError,
)
from openai import APIConnectionError, APIStatusError, AuthenticationError, OpenAI, RateLimitError
from pydantic import BaseModel, Field

BACKEND_DIR = Path(__file__).resolve().parent


def reload_settings() -> dict:
    """Wczytuje .env przy każdym żądaniu (działa po edycji pliku bez restartu)."""
    load_dotenv(BACKEND_DIR / ".env", override=True)
    return {
        "gemini_api_key": os.getenv("GEMINI_API_KEY", "").strip(),
        "gemini_model": os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip(),
        "openai_api_key": os.getenv("OPENAI_API_KEY", "").strip(),
        "openai_model": os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip(),
        "anthropic_api_key": os.getenv("ANTHROPIC_API_KEY", "").strip(),
        "anthropic_model": os.getenv(
            "ANTHROPIC_MODEL", "claude-sonnet-4-20250514"
        ).strip(),
        "anthropic_max_tokens": int(os.getenv("ANTHROPIC_MAX_TOKENS", "4096")),
    }

app = FastAPI(title="AI Logic Evaluator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PromptRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=32000)


class PromptResponse(BaseModel):
    response: str
    model: str


@app.get("/api/health")
def health():
    settings = reload_settings()
    return {
        "status": "ok",
        "gemini_configured": bool(settings["gemini_api_key"]),
        "gemini_model": settings["gemini_model"],
        "openai_configured": bool(settings["openai_api_key"]),
        "openai_model": settings["openai_model"],
        "anthropic_configured": bool(settings["anthropic_api_key"]),
        "anthropic_model": settings["anthropic_model"],
    }


def gemini_error_detail(exc: Exception) -> tuple[int, str]:
    message = str(exc)

    if isinstance(exc, genai_errors.ClientError):
        code = getattr(exc, "code", None)
        if code == 429:
            return (
                429,
                "Przekroczono limit zapytań Gemini (quota). "
                f"Spróbuj za chwilę lub zmień model w backend/.env "
                f"(zalecane: gemini-2.5-flash). Szczegóły: {message}",
            )
        if code == 404:
            return (
                400,
                f"Model Gemini nie jest dostępny. "
                f"Ustaw GEMINI_MODEL=gemini-2.5-flash w pliku backend/.env. "
                f"Szczegóły: {message}",
            )

    if "quota" in message.lower() or "429" in message:
        return (
            429,
            "Przekroczono limit zapytań Gemini. Zmień GEMINI_MODEL na gemini-2.5-flash "
            f"w backend/.env i uruchom backend ponownie. Szczegóły: {message}",
        )

    return 502, f"Błąd Gemini API: {message}"


@app.post("/api/model-a", response_model=PromptResponse)
def model_a(body: PromptRequest):
    settings = reload_settings()
    if not settings["gemini_api_key"]:
        raise HTTPException(
            status_code=500,
            detail=(
                "Brak klucza GEMINI_API_KEY. Utwórz plik backend/.env "
                "na podstawie backend/.env.example."
            ),
        )

    prompt = body.prompt.strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt nie może być pusty.")

    try:
        client = genai.Client(api_key=settings["gemini_api_key"])
        result = client.models.generate_content(
            model=settings["gemini_model"],
            contents=prompt,
        )
        text = (result.text or "").strip()
        if not text:
            raise HTTPException(
                status_code=502,
                detail="Gemini zwróciło pustą odpowiedź.",
            )
        return PromptResponse(response=text, model=settings["gemini_model"])
    except HTTPException:
        raise
    except Exception as exc:
        status_code, detail = gemini_error_detail(exc)
        raise HTTPException(status_code=status_code, detail=detail) from exc


def openai_error_detail(exc: Exception) -> tuple[int, str]:
    message = str(exc)

    if isinstance(exc, RateLimitError) or "insufficient_quota" in message:
        return (
            429,
            "Konto OpenAI nie ma dostępnego limitu (insufficient_quota). "
            "Wejdź na https://platform.openai.com/settings/organization/billing "
            "i doładuj kredyt lub użyj innego klucza API z aktywnym planem.",
        )
    if isinstance(exc, AuthenticationError):
        return (
            401,
            "Nieprawidłowy klucz OPENAI_API_KEY w pliku backend/.env. "
            f"Szczegóły: {message}",
        )
    if isinstance(exc, APIConnectionError):
        return (
            502,
            "Brak połączenia z OpenAI. Sprawdź internet i spróbuj ponownie.",
        )
    if isinstance(exc, APIStatusError):
        return exc.status_code or 502, f"Błąd OpenAI API: {message}"

    return 502, f"Błąd OpenAI API: {message}"


@app.post("/api/model-b", response_model=PromptResponse)
def model_b(body: PromptRequest):
    settings = reload_settings()
    if not settings["openai_api_key"]:
        raise HTTPException(
            status_code=500,
            detail=(
                "Brak klucza OPENAI_API_KEY. Dodaj go do pliku backend/.env "
                "(klucz z platform.openai.com)."
            ),
        )

    prompt = body.prompt.strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt nie może być pusty.")

    try:
        client = OpenAI(api_key=settings["openai_api_key"])
        completion = client.chat.completions.create(
            model=settings["openai_model"],
            messages=[{"role": "user", "content": prompt}],
        )
        choice = completion.choices[0] if completion.choices else None
        text = (choice.message.content if choice and choice.message else "") or ""
        text = text.strip()
        if not text:
            raise HTTPException(
                status_code=502,
                detail="ChatGPT zwróciło pustą odpowiedź.",
            )
        return PromptResponse(response=text, model=settings["openai_model"])
    except HTTPException:
        raise
    except Exception as exc:
        status_code, detail = openai_error_detail(exc)
        raise HTTPException(status_code=status_code, detail=detail) from exc


def anthropic_error_detail(exc: Exception) -> tuple[int, str]:
    message = str(exc)

    if isinstance(exc, AnthropicRateLimitError):
        return (
            429,
            "Przekroczono limit zapytań Claude. Spróbuj za chwilę. "
            f"Szczegóły: {message}",
        )
    if isinstance(exc, AnthropicAuthenticationError):
        return (
            401,
            "Nieprawidłowy klucz ANTHROPIC_API_KEY w pliku backend/.env. "
            f"Szczegóły: {message}",
        )
    if isinstance(exc, AnthropicAPIConnectionError):
        return (
            502,
            "Brak połączenia z Anthropic. Sprawdź internet i spróbuj ponownie.",
        )
    if isinstance(exc, AnthropicAPIStatusError):
        return exc.status_code or 502, f"Błąd Claude API: {message}"

    return 502, f"Błąd Claude API: {message}"


def extract_claude_text(message) -> str:
    parts = []
    for block in message.content:
        if getattr(block, "type", None) == "text":
            parts.append(block.text)
    return "\n".join(parts).strip()


@app.post("/api/model-c", response_model=PromptResponse)
def model_c(body: PromptRequest):
    settings = reload_settings()
    if not settings["anthropic_api_key"]:
        raise HTTPException(
            status_code=500,
            detail=(
                "Brak klucza ANTHROPIC_API_KEY. Dodaj go do pliku backend/.env "
                "(klucz z console.anthropic.com)."
            ),
        )

    prompt = body.prompt.strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt nie może być pusty.")

    try:
        client = Anthropic(api_key=settings["anthropic_api_key"])
        message = client.messages.create(
            model=settings["anthropic_model"],
            max_tokens=settings["anthropic_max_tokens"],
            messages=[{"role": "user", "content": prompt}],
        )
        text = extract_claude_text(message)
        if not text:
            raise HTTPException(
                status_code=502,
                detail="Claude zwróciło pustą odpowiedź.",
            )
        return PromptResponse(response=text, model=settings["anthropic_model"])
    except HTTPException:
        raise
    except Exception as exc:
        status_code, detail = anthropic_error_detail(exc)
        raise HTTPException(status_code=status_code, detail=detail) from exc
