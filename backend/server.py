from fastapi import FastAPI, APIRouter, Request, Form
from fastapi.responses import Response, PlainTextResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
from typing import Optional

from twilio.twiml.messaging_response import MessagingResponse

from bot_messages import build_reply, WELCOME_MESSAGE, SERVICES

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

TWILIO_WHATSAPP_NUMBER = os.environ.get('TWILIO_WHATSAPP_NUMBER', '')

# Create the main app without a prefix
app = FastAPI(title="Alfa Polarizados - Bot Andrea")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Estado en memoria: sesión por contacto (saludo, servicio, esperando vehículo)
sessions: dict[str, dict] = {}


@api_router.get("/")
async def root():
    return {"message": "Bot Andrea de Alfa Polarizados está activo", "status": "ok"}


@api_router.get("/bot/info")
async def bot_info():
    """Datos del bot para mostrar en la landing page."""
    return {
        "name": "Andrea",
        "business": "Alfa Polarizados",
        "location": "Cra. 49 #134A-41 – Barrio Spring, Bogotá",
        "whatsapp_number": TWILIO_WHATSAPP_NUMBER,
        "welcome_message": WELCOME_MESSAGE,
        "services": [
            {"id": "1", "title": "Polarizado y seguridad vehicular", "detail": SERVICES["1"]},
            {"id": "2", "title": "PPF (Protección de pintura)", "detail": SERVICES["2"]},
            {"id": "3", "title": "Película Antiatraco", "detail": SERVICES["3"]},
            {"id": "4", "title": "Polarizado Arquitectónico", "detail": SERVICES["4"]},
            {"id": "5", "title": "Detailing Profesional", "detail": SERVICES["5"]},
        ],
    }


@api_router.post("/bot/preview")
async def bot_preview(payload: dict):
    """Endpoint de prueba para simular la respuesta del bot sin usar WhatsApp."""
    message = payload.get("message", "")
    reset = payload.get("reset", False)
    contact = payload.get("contact", "preview-user")
    name = payload.get("name")
    if reset or contact not in sessions:
        sessions[contact] = {}
    if name and not sessions[contact].get("name"):
        sessions[contact]["name"] = name
    messages = build_reply(message, sessions[contact])
    return {"messages": messages}


@api_router.post("/whatsapp/webhook")
async def whatsapp_webhook(
    Body: str = Form(default=""),
    From: str = Form(default=""),
    ProfileName: str = Form(default=""),
):
    """Webhook que Twilio invoca al recibir un mensaje de WhatsApp."""
    logger.info("WhatsApp entrante de %s (%s): %s", From, ProfileName, Body)

    session = sessions.setdefault(From, {})
    # Nombre automático desde el perfil de WhatsApp (nunca se pregunta)
    if ProfileName and not session.get("name"):
        session["name"] = ProfileName.split()[0] if ProfileName.split() else ProfileName
    messages = build_reply(Body, session)

    twiml = MessagingResponse()
    for m in messages:
        msg = twiml.message(m.get("text", ""))
        for url in m.get("media") or []:
            msg.media(url)
    return Response(content=str(twiml), media_type="application/xml")


@api_router.get("/whatsapp/webhook")
async def whatsapp_webhook_health():
    return PlainTextResponse("Webhook de WhatsApp de Andrea activo ✅")


# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)
