"""Tests for the defensive guard in POST /api/whatsapp/webhook.

Verifica:
 1) Evento sin From -> TwiML vacío <Response /> (o similar), NO crea conversación.
 2) Evento con From pero Body vacío y sin media -> TwiML vacío, NO crea conversación
    para ese From (evita eco de salientes / status callbacks basura).
 3) Evento con From y Body vacío pero con media (audio) -> NO es ignorado; responde
    con el handoff de audio a la asesora (AUDIO_HANDOFF) y SÍ registra la conversación.
"""
import os
import re
import uuid
import pytest
import requests


def _load_frontend_url():
    path = "/app/frontend/.env"
    if os.path.exists(path):
        for line in open(path):
            if line.startswith("REACT_APP_BACKEND_URL="):
                return line.split("=", 1)[1].strip()
    return ""


BASE_URL = (os.environ.get("REACT_APP_BACKEND_URL") or _load_frontend_url()).rstrip("/")
assert BASE_URL, "REACT_APP_BACKEND_URL debe estar configurado"
API = f"{BASE_URL}/api"

ADMIN_USER = "alfa"
ADMIN_PASS = "Andrea2026*"
BUSINESS_TO = "whatsapp:+15553784942"


@pytest.fixture(scope="module")
def client():
    return requests.Session()


@pytest.fixture(scope="module")
def admin_headers(client):
    r = client.post(f"{API}/auth/login", json={"username": ADMIN_USER, "password": ADMIN_PASS}, timeout=15)
    assert r.status_code == 200, f"login fallo: {r.status_code} {r.text}"
    return {"Authorization": f"Bearer {r.json()['token']}"}


def _get_conversations(client, headers):
    r = client.get(f"{API}/admin/conversations", headers=headers, timeout=15)
    assert r.status_code == 200
    data = r.json()
    return data.get("conversations") if isinstance(data, dict) else data


def _contacts(convs):
    return {c.get("contact") for c in convs}


class TestGuardIgnoresEmptyEvents:
    def test_empty_from_returns_empty_twiml(self, client):
        r = client.post(
            f"{API}/whatsapp/webhook",
            data={"Body": "", "From": "", "To": BUSINESS_TO, "NumMedia": "0"},
            timeout=15,
        )
        assert r.status_code == 200
        assert "xml" in r.headers.get("content-type", "").lower()
        # TwiML vacío: <Response /> o <Response></Response>, sin <Message>
        assert "<Message>" not in r.text, f"No debe generar Message: {r.text}"
        assert "<Response" in r.text

    def test_empty_body_no_media_does_not_create_conversation(self, client, admin_headers):
        """Simula un eco (Twilio callback) donde el negocio aparece como From con Body vacío."""
        # Usar From único que jamás debe aparecer en conversaciones porque será ignorado
        ghost_from = f"whatsapp:+15553784942"  # el propio número negocio, típico de ecos
        # Registrar contactos existentes antes
        before = _contacts(_get_conversations(client, admin_headers))

        r = client.post(
            f"{API}/whatsapp/webhook",
            data={
                "Body": "",
                "From": ghost_from,
                "To": "whatsapp:+573000000000",
                "NumMedia": "0",
                "ProfileName": "",
            },
            timeout=15,
        )
        assert r.status_code == 200
        assert "<Message>" not in r.text, f"No debe generar Message: {r.text}"
        assert "<Response" in r.text

        # Verificar que NO se creó/actualizó conversación (o al menos no se creó si no existía).
        after = _contacts(_get_conversations(client, admin_headers))
        newly_added = after - before
        assert ghost_from not in newly_added, (
            f"El From={ghost_from} no debía crear conversación por ser evento vacío. "
            f"Nuevos: {newly_added}"
        )

    def test_empty_body_no_media_unique_from_never_registered(self, client, admin_headers):
        """From único e inexistente con Body vacío y sin media: nunca debe aparecer."""
        unique_from = f"whatsapp:+57309{uuid.uuid4().hex[:7]}"
        r = client.post(
            f"{API}/whatsapp/webhook",
            data={
                "Body": "   ",  # solo whitespace -> también debe ser ignorado
                "From": unique_from,
                "To": BUSINESS_TO,
                "NumMedia": "0",
            },
            timeout=15,
        )
        assert r.status_code == 200
        assert "<Message>" not in r.text
        convs = _get_conversations(client, admin_headers)
        assert unique_from not in _contacts(convs), (
            f"From vacío no debe aparecer en conversations: {unique_from}"
        )


class TestGuardDoesNotIgnoreAudio:
    def test_audio_media_without_body_triggers_handoff(self, client, admin_headers):
        unique_from = f"whatsapp:+57308{uuid.uuid4().hex[:7]}"
        r = client.post(
            f"{API}/whatsapp/webhook",
            data={
                "Body": "",
                "From": unique_from,
                "To": BUSINESS_TO,
                "NumMedia": "1",
                "MediaContentType0": "audio/ogg",
                "MediaUrl0": "https://api.twilio.com/fake-audio.ogg",
                "ProfileName": "Test Audio",
            },
            timeout=15,
        )
        assert r.status_code == 200
        body = r.text
        assert "<Response>" in body and "<Message>" in body, f"Debe responder handoff: {body}"
        # Handoff típicamente menciona a la asesora / no puedo escuchar audio
        low = body.lower()
        assert (
            "audio" in low
            or "asesora" in low
            or "no puedo" in low
            or "escuchar" in low
        ), f"Se esperaba texto de handoff de audio en TwiML: {body[:400]}"

        # Debe haber registrado la conversación
        convs = _get_conversations(client, admin_headers)
        assert unique_from in _contacts(convs), (
            f"El evento con media audio SÍ debe crear conversación: {unique_from}"
        )


class TestNormalFlowIntact:
    """Regresion mínima para asegurar que el guard no rompe el flujo real."""

    def test_real_message_returns_welcome(self, client, admin_headers):
        unique_from = f"whatsapp:+57307{uuid.uuid4().hex[:7]}"
        r = client.post(
            f"{API}/whatsapp/webhook",
            data={
                "Body": "hola",
                "From": unique_from,
                "To": BUSINESS_TO,
                "NumMedia": "0",
                "ProfileName": "Carlos Prueba",
            },
            timeout=15,
        )
        assert r.status_code == 200
        assert "<Message>" in r.text
        assert "Soy Andrea" in r.text
        assert "Alfa Polarizados" in r.text

        convs = _get_conversations(client, admin_headers)
        assert unique_from in _contacts(convs)

    def test_option_1_polarizado(self, client):
        unique_from = f"whatsapp:+57306{uuid.uuid4().hex[:7]}"
        client.post(
            f"{API}/whatsapp/webhook",
            data={"Body": "hola", "From": unique_from, "To": BUSINESS_TO, "ProfileName": "Luis"},
            timeout=15,
        )
        r = client.post(
            f"{API}/whatsapp/webhook",
            data={"Body": "1", "From": unique_from, "To": BUSINESS_TO, "ProfileName": "Luis"},
            timeout=15,
        )
        assert r.status_code == 200
        assert "Polarizado" in r.text
        assert "marca y modelo" in r.text.lower()

    def test_option_3_antiatraco_media(self, client):
        unique_from = f"whatsapp:+57305{uuid.uuid4().hex[:7]}"
        client.post(
            f"{API}/whatsapp/webhook",
            data={"Body": "hola", "From": unique_from, "To": BUSINESS_TO, "ProfileName": "Ana"},
            timeout=15,
        )
        client.post(
            f"{API}/whatsapp/webhook",
            data={"Body": "3", "From": unique_from, "To": BUSINESS_TO, "ProfileName": "Ana"},
            timeout=15,
        )
        r = client.post(
            f"{API}/whatsapp/webhook",
            data={"Body": "Mazda 3", "From": unique_from, "To": BUSINESS_TO, "ProfileName": "Ana"},
            timeout=15,
        )
        assert r.status_code == 200
        assert "<Media>" in r.text, f"Esperaba <Media> en TwiML: {r.text[:400]}"
        media_urls = re.findall(r"<Media>([^<]+)</Media>", r.text)
        assert any("planes" in u.lower() or "cloudinary" in u.lower() for u in media_urls)


class TestHealth:
    def test_get_webhook_health(self, client):
        r = client.get(f"{API}/whatsapp/webhook", timeout=15)
        assert r.status_code == 200
        assert "Andrea" in r.text
