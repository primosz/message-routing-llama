import os
import logging
from typing import Dict, Any
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from email_service import send_routing_email
import ollama

logger = logging.getLogger(__name__)

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434/v1")
MODEL_NAME = os.getenv("OLLAMA_MODEL", "llama3.2")
DEPARTMENTS = {
    "human-resources@example.com": "Sprawy kadrowo-płacowe, rekrutacje i zapytania HR sformułowane w języku angielskim lub o charakterze międzynarodowym.",
    "help-desk@example.com": "Ogólne zgłoszenia problemów, zapytania użytkowników i pomoc techniczna pierwszej linii.",
    "it@example.com": "Sprawy techniczne, awarie komputerów, problemy z dostępami, sieciami, serwerami lub oprogramowaniem.",
    "kadry@example.com": "Sprawy pracownicze, wnioski urlopowe, zaświadczenia, umowy i sprawy płacowe sformułowane w języku polskim.",
    "other@example.com": "Zgłoszenia ogólne, zapytania ofertowe, spam lub wiadomości, których nie da się przypisać do żadnego z powyższych działów."
}
dept_list = "\n".join([f"- {email}: {desc}" for email, desc in DEPARTMENTS.items()])

logger.info(f"{MODEL_NAME}{OLLAMA_URL}")

model = OpenAIChatModel(
    MODEL_NAME,
    provider=OpenAIProvider(
        base_url=OLLAMA_URL,
        api_key="ollama"
    )
)

agent = Agent(
    model=model,
    system_prompt="Jesteś asystentem klasyfikującym wiadomości e-mail do odpowiednich działów firmowych."
)


async def run_routing_agent(sender_email: str, original_message: str) -> Dict[str, Any]:
    logger.info(f"zgłoszenie od {sender_email}. Przetwarzanie")
    
    system_content = f"""Jesteś automatycznym klasyfikatorem e-maili. Twoim jedynym zadaniem jest przypisanie wiadomości użytkownika do jednego z działów.
Dostępne są następujące działy wraz z ich opisami:
{dept_list}

ZASADY:
1. Odpowiedz W JEDNEJ LINII w formacie: ADRES_EMAIL: UZASADNIENIE
2. Wybierz ADRES_EMAIL WYŁĄCZNIE z powyższej listy (nie wymyślaj własnych adresów!).
3. NIE pisz żadnych wstępów, przeprosin, kodu ani dodatkowych zdań.

PRZYKŁAD:
help-desk@example.com: Zgłoszenie dotyczy awarii drukarki."""


    #client = ollama.Client(host=OLLAMA_URL)
    messages = [
        {'role' : 'system', 'content': system_content},
        {'role': 'user', 'content': original_message}
    ]
    response = ollama.chat(model=MODEL_NAME, messages=messages)
    logger.info("BOT:")
    logger.info(response.message.content)

    target_email = "help-desk@example.com"
    explanation = "test"
    
    raw_content = response.message.content if (response and response.message) else None

    if raw_content is not None:
        cleaned = raw_content.strip()
        if ":" in cleaned:
            target_email, explanation = cleaned.split(":", 1)
            target_email = target_email.strip()
            explanation = explanation.strip()
        else:
            target_email = "other@example.com"
            explanation = cleaned
    else:
        target_email = "other@example.com"
        explanation = "Brak odpowiedzi od Ollama."


    if target_email not in DEPARTMENTS:
        target_email = "other@example.com"

    send_routing_email(
        sender_email=sender_email,
        target_department_email=target_email,
        original_message=original_message,
        category_explanation=explanation
    )

    return {
        "status": "success",
        "routed_to": target_email,
        "explanation": explanation
    }
