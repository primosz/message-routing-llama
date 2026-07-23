from pydantic_ai import RunContext
import os
import logging
from typing import Dict, Any
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from email_service import send_routing_email

logger = logging.getLogger(__name__)

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434/v1")
MODEL_NAME = os.getenv("OLLAMA_MODEL", "llama3.2")
DEPARTMENTS = {
    "it@example.com": (
        "Wszelkie sprawy techniczne i awarie sprzętu: awarie komputerów, laptopów, monitorów, "
        "drukarek, sieci, haseł, logowania, dostępów, serwerów i oprogramowania."
    ),
    "help-desk@example.com": (
        "Ogólna obsługa klienta i pytania organizacyjne: pytania o godziny otwarcia, lokalizację "
        "biura, kontakt do pracowników, przesyłki, informacje ogólne o firmie (BEZ spraw technicznych i komputerów)."
    ),
    "kadry@example.com": (
        "Sprawy pracownicze i płacowe (język polski): wypłaty, wynagrodzenia, paski płacowe, "
        "wnioski urlopowe, zaświadczenia o zatrudnieniu, zwolnienia L4, umowy o pracę."
    ),
    "human-resources@example.com": (
        "Sprawy związane z rozwojem pracownika, rekrutacją, szkoleniami, programem poleceń, wewnętrznymi inicjatywami firmowymi, budowaniem zespołu, opiniami i ocenami pracowniczymi, a także zapytania o karierę oraz możliwości rozwoju kompetencji w organizacji."
    ),
    "other@example.com": (
        "Zgłoszenia ogólne, oferty handlowe, spam, reklamy lub wiadomości, które nie pasują do żadnego z powyższych."
    )
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
system_prompt = f"""Jesteś inteligentnym asystentem routingu wiadomości. 
Twoim jedynym zadaniem jest przeanalizowanie treści wiadomości i przekierowanie jej do odpowiedniego działu poprzez wywołanie narzędzia 'send_email'.

Dostępne są następujące działy wraz z ich adresami e-mail:
{dept_list}

ZASADY PRZYPISYWANIA:
- Każdy problem związany z komputerem, sprzętem, oprogramowaniem, logowaniem lub siecią kieruj BEZWZGLĘDNIE do 'it@example.com'.
- Dział 'help-desk@example.com' obsługuje wyłącznie pytania organizacyjne (np. adres biura, godziny otwarcia).
- Problemy z wypłatą, wynagrodzeniem lub urlopem po polsku kieruj do 'kadry@example.com'.

KROKI DO WYKONANIA:
1. Przeanalizuj treść zgłoszenia.
2. Wybierz najbardziej odpowiedni dział z listy.
3. WYWOŁAJ NARZĘDZIE 'send_email' podając wybrany adres email działu oraz zwięzłe uzasadnienie po polsku (max 1 proste zdanie).

NIE ODPOWIADAJ TEKSTEM. TWOIM JEDYNYM ZADANIEM JEST WYWOŁANIE NARZĘDZIA 'send_email'.
"""



class AgentDeps:
    def __init__(self, sender_email: str, original_message: str):
        self.sender_email = sender_email
        self.original_message = original_message
        self.routing_target: str = "test@test.com"
        self.exp: str = "test"
        self.tool_called: bool = False

agent = Agent(
    model=model,
    deps_type=AgentDeps,
    system_prompt=system_prompt
)

@agent.tool
def send_email(ctx: RunContext[AgentDeps], target_email: str, exp: str) -> str:
    logger.info(f"Agent wywoluje narzedzie send_email dla {target_email}: {exp}")
    
    if ctx.deps.tool_called:
        return "Tool został już wywołany."
    
    ctx.deps.tool_called = True
    ctx.deps.routing_target = target_email
    ctx.deps.exp = exp    
    
    send_routing_email(
        sender_email=ctx.deps.sender_email,
        target_department_email=target_email,
        original_message=ctx.deps.original_message,
        category_explanation=exp
    )
    
    return f"Wiadomość została wysłana do {target_email}"


async def run_routing_agent(sender_email: str, original_message: str):
    logger.info(f"zgłoszenie od {sender_email}. Przetwarzanie") 

    deps = AgentDeps(sender_email=sender_email, original_message=original_message)
    result = await agent.run(original_message, deps = deps)

    return {
        "status": "success",
        "routed_to": deps.routing_target,
        "explanation": deps.exp
    }

    
