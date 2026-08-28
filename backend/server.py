from fastapi import FastAPI, APIRouter, Request, Form
from fastapi.responses import Response, PlainTextResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import time
import asyncio
import logging
from pathlib import Path
from typing import Optional

from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client as TwilioClient

from bot_messages import build_reply, WELCOME_MESSAGE, SERVICES, AUDIO_HANDOFF

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', '')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', '')
TWILIO_WHATSAPP_NUMBER = os.environ.get('TWILIO_WHATSAPP_NUMBER', '')

# Reenganche si el cliente no responde en más de 3 horas
REENGAGE_AFTER_SECONDS = 3 * 60 * 60
REENGAGE_CHECK_INTERVAL = 10 * 60

twilio_client = None
if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    twilio_client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

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
    NumMedia: str = Form(default="0"),
    MediaContentType0: str = Form(default=""),
):
    """Webhook que Twilio invoca al recibir un mensaje de WhatsApp."""
    logger.info("WhatsApp entrante de %s (%s): %s [media=%s %s]", From, ProfileName, Body, NumMedia, MediaContentType0)

    session = sessions.setdefault(From, {})
    # Nombre automático desde el perfil de WhatsApp (nunca se pregunta)
    if ProfileName and not session.get("name"):
        session["name"] = ProfileName.split()[0] if ProfileName.split() else ProfileName

    # El cliente respondió → actualizar actividad, cancelar diferidos y reenganche pendientes
    session["last_activity"] = time.time()
    session["reengaged"] = False
    session["pending_delayed"] = False

    # Si el cliente envía un audio/nota de voz → remitir a la asesora
    has_media = NumMedia.isdigit() and int(NumMedia) > 0
    if has_media and MediaContentType0.startswith("audio"):
        messages = [{"text": AUDIO_HANDOFF, "media": [], "delay": 0}]
    else:
        messages = build_reply(Body, session)

    immediate = [m for m in messages if not m.get("delay")]
    delayed = [m for m in messages if m.get("delay")]

    # Los mensajes diferidos (ej. la pregunta tras el video) se envían después vía REST
    if delayed and twilio_client and From.startswith("whatsapp:"):
        session["pending_delayed"] = True
        asyncio.create_task(_send_delayed(From, delayed, session))
    elif delayed:
        immediate = immediate + delayed  # fallback: sin cliente REST, enviar todo junto

    twiml = MessagingResponse()
    for m in immediate:
        msg = twiml.message(m.get("text", ""))
        for url in m.get("media") or []:
            msg.media(url)
    return Response(content=str(twiml), media_type="application/xml")


async def _send_delayed(contact: str, messages: list, session: dict):
    """Envía mensajes diferidos (tras un retraso) por Twilio REST, si el cliente no respondió antes."""
    for m in messages:
        await asyncio.sleep(m.get("delay", 0))
        if not session.get("pending_delayed"):
            return  # el cliente ya escribió; se cancela el envío
        try:
            twilio_client.messages.create(
                from_=f"whatsapp:{TWILIO_WHATSAPP_NUMBER}",
                to=contact,
                body=m.get("text", ""),
                media_url=(m.get("media") or None),
            )
        except Exception as exc:
            logger.error("Error enviando mensaje diferido a %s: %s", contact, exc)
    session["pending_delayed"] = False


@api_router.get("/whatsapp/webhook")
async def whatsapp_webhook_health():
    return PlainTextResponse("Webhook de WhatsApp de Andrea activo ✅")


def _send_reengagement(contact: str, session: dict):
    """Envía un mensaje proactivo para retomar la conversación (Twilio REST)."""
    name = session.get("name", "")
    saludo = f"¡Hola de nuevo, {name}! 👋" if name else "¡Hola de nuevo! 👋"
    body = (
        f"{saludo} Soy Andrea de Alfa Polarizados 🙋‍♀️. Vi que quedó pendiente nuestra "
        "conversación. ¿Continuamos? 😊 Escribe *volver* para ver el menú o cuéntame en qué te ayudo."
    )
    twilio_client.messages.create(
        from_=f"whatsapp:{TWILIO_WHATSAPP_NUMBER}",
        to=contact,
        body=body,
    )


async def _reengagement_loop():
    """Revisa periódicamente y retoma conversaciones inactivas por más de 3 horas."""
    while True:
        await asyncio.sleep(REENGAGE_CHECK_INTERVAL)
        if not twilio_client:
            continue
        now = time.time()
        for contact, s in list(sessions.items()):
            if not contact.startswith("whatsapp:"):
                continue
            la = s.get("last_activity")
            if not la or s.get("reengaged") or not s.get("greeted"):
                continue
            if now - la > REENGAGE_AFTER_SECONDS:
                try:
                    _send_reengagement(contact, s)
                    s["reengaged"] = True
                    logger.info("Reenganche enviado a %s", contact)
                except Exception as exc:
                    logger.error("Error reenganchando %s: %s", contact, exc)


@app.on_event("startup")
async def _start_reengagement():
    asyncio.create_task(_reengagement_loop())


# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)
