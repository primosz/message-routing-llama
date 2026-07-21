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
    
    target_email = "help-desk@example.com"
    explanation = "test"
    
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
