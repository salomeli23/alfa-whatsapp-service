"""Backend tests for panel admin: auth, persistence, conversations, messages, toggle-bot, reply."""
import os
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
API = f"{BASE_URL}/api"


@pytest.fixture(scope="module")
def client():
    return requests.Session()


@pytest.fixture(scope="module")
def token(client):
    r = client.post(f"{API}/auth/login", json={"username": "alfa", "password": "Andrea2026*"}, timeout=15)
    assert r.status_code == 200, r.text
    return r.json()["token"]


@pytest.fixture(scope="module")
def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


# ---------- Auth ----------
class TestAuth:
    def test_login_success(self, client):
        r = client.post(f"{API}/auth/login", json={"username": "alfa", "password": "Andrea2026*"}, timeout=15)
        assert r.status_code == 200
        data = r.json()
        assert data["username"] == "alfa"
        assert isinstance(data["token"], str) and len(data["token"]) > 20

    def test_login_bad_credentials(self, client):
        r = client.post(f"{API}/auth/login", json={"username": "alfa", "password": "wrong"}, timeout=15)
        assert r.status_code == 401
        assert "incorrect" in r.json()["detail"].lower() or "incorrecto" in r.json()["detail"].lower()

    def test_me_with_token(self, client, auth_headers):
        r = client.get(f"{API}/auth/me", headers=auth_headers, timeout=15)
        assert r.status_code == 200
        assert r.json()["username"] == "alfa"

    def test_me_without_token(self, client):
        r = client.get(f"{API}/auth/me", timeout=15)
        assert r.status_code == 401

    def test_admin_endpoints_require_auth(self, client):
        r = client.get(f"{API}/admin/conversations", timeout=15)
        assert r.status_code == 401


# ---------- Persistence via webhook ----------
class TestPersistence:
    def test_webhook_persists_in_and_out(self, client, auth_headers):
        contact = f"whatsapp:+57300{uuid.uuid4().hex[:7]}"
        r = client.post(
            f"{API}/whatsapp/webhook",
            data={"Body": "hola", "From": contact, "To": "whatsapp:+14155238886", "ProfileName": "Cliente Test"},
            timeout=15,
        )
        assert r.status_code == 200
        # Check conversations
        r2 = client.get(f"{API}/admin/conversations", headers=auth_headers, timeout=15)
        assert r2.status_code == 200
        convs = r2.json()
        conv = next((c for c in convs if c["contact"] == contact), None)
        assert conv is not None, f"conv for {contact} not found"
        assert conv.get("name")
        assert conv.get("last_body")
        assert conv.get("bot_paused") is False
        # Check messages
        r3 = client.get(f"{API}/admin/messages", headers=auth_headers, params={"contact": contact}, timeout=15)
        assert r3.status_code == 200
        msgs = r3.json()
        directions = [m["direction"] for m in msgs]
        assert "in" in directions
        assert "out" in directions
        # First message = in
        assert msgs[0]["direction"] == "in"
        assert msgs[0]["body"] == "hola"


# ---------- Toggle bot / human handoff ----------
class TestToggleBot:
    def test_toggle_pauses_bot_and_webhook_returns_empty(self, client, auth_headers):
        contact = f"whatsapp:+57301{uuid.uuid4().hex[:7]}"
        # seed
        client.post(f"{API}/whatsapp/webhook", data={"Body": "hola", "From": contact, "To": "whatsapp:+14155238886"}, timeout=15)
        # pause
        r = client.post(f"{API}/admin/toggle-bot", headers=auth_headers, json={"contact": contact, "paused": True}, timeout=15)
        assert r.status_code == 200
        assert r.json()["bot_paused"] is True
        # incoming should not respond
        r2 = client.post(f"{API}/whatsapp/webhook", data={"Body": "1", "From": contact, "To": "whatsapp:+14155238886"}, timeout=15)
        assert r2.status_code == 200
        body = r2.text.strip()
        # Empty TwiML — no <Message>
        assert "<Message>" not in body
        assert "<Response" in body

    def test_reactivate_bot_resumes_replies(self, client, auth_headers):
        contact = f"whatsapp:+57302{uuid.uuid4().hex[:7]}"
        client.post(f"{API}/whatsapp/webhook", data={"Body": "hola", "From": contact, "To": "whatsapp:+14155238886"}, timeout=15)
        client.post(f"{API}/admin/toggle-bot", headers=auth_headers, json={"contact": contact, "paused": True}, timeout=15)
        # confirm paused: no message
        r_p = client.post(f"{API}/whatsapp/webhook", data={"Body": "hola", "From": contact, "To": "whatsapp:+14155238886"}, timeout=15)
        assert "<Message>" not in r_p.text
        # reactivate
        r = client.post(f"{API}/admin/toggle-bot", headers=auth_headers, json={"contact": contact, "paused": False}, timeout=15)
        assert r.status_code == 200
        assert r.json()["bot_paused"] is False
        # incoming replies again
        r2 = client.post(f"{API}/whatsapp/webhook", data={"Body": "hola", "From": contact, "To": "whatsapp:+14155238886"}, timeout=15)
        assert "<Message>" in r2.text


# ---------- Admin reply (Twilio KYC blocked -> 200 con ok:false) ----------
class TestAdminReply:
    def test_reply_returns_ok_false_when_twilio_rejects(self, client, auth_headers):
        contact = f"whatsapp:+57303{uuid.uuid4().hex[:7]}"
        client.post(f"{API}/whatsapp/webhook", data={"Body": "hola", "From": contact, "To": "whatsapp:+14155238886"}, timeout=15)
        r = client.post(f"{API}/admin/reply", headers=auth_headers, json={"contact": contact, "body": "Hola desde el panel"}, timeout=30)
        # Twilio KYC no aprobado -> el endpoint responde 200 con ok:false (no crashea)
        assert r.status_code == 200, f"expected 200, got {r.status_code}: {r.text}"
        data = r.json()
        assert data.get("ok") is False
        assert "twilio" in (data.get("error") or "").lower()
        # Si el envío falla, el bot NO debe quedar pausado (para no dejar al cliente sin respuesta)
        r2 = client.get(f"{API}/admin/conversations", headers=auth_headers, timeout=15)
        conv = next((c for c in r2.json() if c["contact"] == contact), None)
        assert conv is not None
        assert conv.get("bot_paused") is not True

    def test_reply_missing_fields_400(self, client, auth_headers):
        r = client.post(f"{API}/admin/reply", headers=auth_headers, json={"contact": "", "body": ""}, timeout=15)
        assert r.status_code == 400
