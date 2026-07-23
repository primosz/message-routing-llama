import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, Field
from agent import run_routing_agent

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s", force=True)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Email Routing API",
    description="PoC inteligentnego systemu przekierowywania wiadomości e-mail",
    version="0.1.0",
    docs_url="/api/v1/docs",
    openapi_url="/api/v1/openapi.json"
)

class RouteRequest(BaseModel):
    email: EmailStr = Field(
        ..., 
        description="Adres e-mail nadawcy zgłoszenia", 
        json_schema_extra={"example": "jan.nowak@example.com"}
    )
    message: str = Field(
        ..., 
        description="Treść zgłoszenia do klasyfikacji", 
        json_schema_extra={"example": "Nie działa mi komputer, potrzebuję pomocy technicznej."}
    )

class RouteResponse(BaseModel):
    status: str = Field(..., description="Status")
    routed_to: str = Field(..., description="Adres e-mail działu")
    explanation: str = Field(..., description="Uzasadnienie")

@app.post("/api/v1/route", response_model=RouteResponse, summary="Klasyfikacja i routing wiadomości")
async def route_message(payload: RouteRequest) -> RouteResponse:
    """Przetwarza zgłoszenie użytkownika."""
    logger.info(f"Otrzymano wiadomość od: {payload.email}")
    logger.info(f"Treść oryginalnej wiadomosci: {payload.message}")
    try:
        result = await run_routing_agent(
            sender_email=payload.email, 
            original_message=payload.message
        )
        logger.info(f"Agent zadecydował o przekierowaniu do działu: {result['routed_to']}")
        logger.info(f"Uzasadnienie: {result['explanation']}")
        return RouteResponse(
            status=result["status"],
            routed_to=result["routed_to"],
            explanation=result["explanation"]
        )
    except Exception as e:
        logger.error(f"Błąd: {e}")
        raise HTTPException(status_code=500, detail=f"błąd serwera: {e}")

@app.get("/health", summary="Health check serwisu")
async def health_check():
    return {"status": "healthy"}
