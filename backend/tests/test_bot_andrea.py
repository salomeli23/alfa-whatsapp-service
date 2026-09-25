"""Backend tests para el bot Andrea de Alfa Polarizados (v2).

Cubre:
- Health/info endpoints
- Webhook TwiML con ProfileName y flujos completos
- /api/bot/preview (nuevo formato messages[{text, media[]}])
- Opción 1 (planes + videos + selección)
- Opción 2 PPF (submenú Total/Pintura/Piano Black/Acrílicas + catálogo)
- Comando global 'volver'
- Opción 4 arquitectónico (ciudad -> lugar -> medidas)
"""
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
assert BASE_URL, "REACT_APP_BACKEND_URL debe estar configurado"
API = f"{BASE_URL}/api"


@pytest.fixture(scope="module")
def client():
    return requests.Session()


def _preview(client, contact, message, reset=False, name=None):
    payload = {"message": message, "contact": contact, "reset": reset}
    if name is not None:
        payload["name"] = name
    r = client.post(f"{API}/bot/preview", json=payload, timeout=15)
    assert r.status_code == 200, r.text
    return r.json()["messages"]


def _texts(messages):
    return "\n".join(m["text"] for m in messages)


def _all_media(messages):
    urls = []
    for m in messages:
        urls.extend(m.get("media") or [])
    return urls


# ---------- Health / info ----------
class TestHealth:
    def test_root(self, client):
        r = client.get(f"{API}/")
        assert r.status_code == 200
        data = r.json()
        assert data.get("status") == "ok"
        assert "Andrea" in data.get("message", "")

    def test_bot_info(self, client):
        r = client.get(f"{API}/bot/info")
        assert r.status_code == 200
        data = r.json()
        assert data["name"] == "Andrea"
        assert "Cra. 49 #134A-41" in data["location"]
        assert len(data["services"]) == 5
        # PPF service NO debe contener 'Desde $900.000 COP'
        opt2 = next(s for s in data["services"] if s["id"] == "2")
        assert "Desde $900.000" not in opt2["detail"]


# ---------- Webhook TwiML ----------
class TestWebhook:
    def _post(self, client, body, frm, profile_name=""):
        return client.post(
            f"{API}/whatsapp/webhook",
            data={"Body": body, "From": frm, "ProfileName": profile_name},
            timeout=15,
        )

    def test_first_message_returns_welcome_twiml_and_never_asks_name(self, client):
        frm = f"whatsapp:+57300{uuid.uuid4().hex[:7]}"
        r = self._post(client, "hola", frm, profile_name="Camila Perez")
        assert r.status_code == 200
        assert "xml" in r.headers.get("content-type", "").lower()
        body = r.text
        assert "<Response>" in body and "<Message>" in body
        assert "Soy Andrea" in body
        # No debe pedir nombre en ningun paso
        assert "tu nombre" not in body.lower()
        assert "cual es tu nombre" not in body.lower()

    def test_greets_with_profile_name_after_choosing_option(self, client):
        frm = f"whatsapp:+57301{uuid.uuid4().hex[:7]}"
        # primer mensaje: welcome (guarda ProfileName=Camila)
        self._post(client, "hola", frm, profile_name="Camila Perez")
        # elegir opcion 1
        r = self._post(client, "1", frm, profile_name="Camila Perez")
        body = r.text
        assert "Camila" in body, f"Debe saludar con el primer nombre. Body: {body[:400]}"
        # no debe volver a preguntar nombre
        assert "tu nombre" not in body.lower()


# ---------- Preview: welcome / menu ----------
class TestPreviewBasics:
    def test_preview_new_contact_returns_welcome(self, client):
        c = f"prev-{uuid.uuid4().hex}"
        msgs = _preview(client, c, "hi", reset=True, name="Camila")
        assert len(msgs) == 1
        assert "Soy Andrea" in msgs[0]["text"]

    def test_volver_command_returns_menu(self, client):
        c = f"prev-{uuid.uuid4().hex}"
        _preview(client, c, "hi", reset=True, name="Camila")
        _preview(client, c, "1", name="Camila")  # entra al flujo
        msgs = _preview(client, c, "volver", name="Camila")
        assert "Soy Andrea" in _texts(msgs)


# ---------- Opción 1: polarizado ----------
class TestOption1:
    def test_option1_shows_plans_videos_and_asks_choice(self, client):
        c = f"prev-{uuid.uuid4().hex}"
        _preview(client, c, "hi", reset=True, name="Camila")
        opt = _preview(client, c, "1", name="Camila")
        # tras elegir opcion 1, debe saludar con Camila y pedir vehiculo
        assert "Camila" in _texts(opt)
        assert "marca y modelo" in _texts(opt).lower()

        msgs = _preview(client, c, "Toyota Corolla", name="Camila")
        media = _all_media(msgs)
        # 3 imagenes + 3 videos (incluye prueba de seguridad)
        images = [u for u in media if u.endswith((".jpg", ".jpeg", ".png"))]
        videos = [u for u in media if u.endswith((".mp4", ".mov", ".webm"))]
        assert len(images) >= 3, f"Esperaba 3+ imágenes, hallé {len(images)}: {images}"
        assert len(videos) == 3, f"Esperaba 3 videos, hallé {len(videos)}: {videos}"
        assert any("peliculaseguridad" in u for u in videos), "Debe incluir el video de prueba de seguridad"
        # pregunta cual plan gustó
        assert "¿Cuál" in _texts(msgs) or "planes" in _texts(msgs).lower()

    def test_option1_choice_by_number(self, client):
        c = f"prev-{uuid.uuid4().hex}"
        _preview(client, c, "hi", reset=True, name="Camila")
        _preview(client, c, "1", name="Camila")
        _preview(client, c, "Mazda 3", name="Camila")
        msgs = _preview(client, c, "3", name="Camila")  # IRR
        text = _texts(msgs)
        assert "IRR" in text
        assert "Agendamos" in text or "agendar" in text.lower()

    def test_option1_choice_by_name(self, client):
        c = f"prev-{uuid.uuid4().hex}"
        _preview(client, c, "hi", reset=True, name="Camila")
        _preview(client, c, "1", name="Camila")
        _preview(client, c, "Kia Rio", name="Camila")
        msgs = _preview(client, c, "cerámico", name="Camila")
        text = _texts(msgs)
        assert "Cerámico" in text


# ---------- Opción 2: PPF ----------
class TestOption2PPF:
    def _enter_ppf(self, client, vehicle="Mazda CX-5"):
        c = f"prev-{uuid.uuid4().hex}"
        _preview(client, c, "hi", reset=True, name="Ana")
        opt = _preview(client, c, "2", name="Ana")
        # sin precio en la descripcion
        assert "Desde $900.000 COP" not in _texts(opt)
        _preview(client, c, vehicle, name="Ana")
        return c

    def test_ppf_intro_no_price_line(self, client):
        c = f"prev-{uuid.uuid4().hex}"
        _preview(client, c, "hi", reset=True, name="Ana")
        msgs = _preview(client, c, "2", name="Ana")
        text = _texts(msgs)
        assert "Desde $900.000 COP" not in text
        assert "marca y modelo" in text.lower()

    def test_ppf_submenu_after_vehicle(self, client):
        c = self._enter_ppf(client)
        # submenu aparece en el mismo mensaje del vehicle_ack
        # (buscar el prompt)
        msgs = _preview(client, c, "volver", name="Ana")  # solo para no ensuciar, pero verifiquemos
        # mejor: hacer un flujo fresco
        c2 = f"prev-{uuid.uuid4().hex}"
        _preview(client, c2, "hi", reset=True, name="Ana")
        _preview(client, c2, "2", name="Ana")
        msgs = _preview(client, c2, "Mazda CX-5", name="Ana")
        text = _texts(msgs)
        assert "Piezas Piano Black" in text
        assert "Piezas Acrílicas" in text
        assert "Full Front" in text
        assert "Full PPF" in text

    def test_ppf_full_ppf(self, client):
        c = self._enter_ppf(client)
        msgs = _preview(client, c, "4", name="Ana")
        text = _texts(msgs)
        assert "Protección Completa" in text or "Full PPF" in text
        assert "asesor" in text.lower()
        # No debe hablar de cita/agendar en Full PPF
        assert "Agendamos" not in text and "agendar" not in text.lower()

    def test_ppf_full_front(self, client):
        c = self._enter_ppf(client)
        msgs = _preview(client, c, "3", name="Ana")
        text = _texts(msgs)
        assert "Frontal" in text or "Full Front" in text
        assert "asesor" in text.lower()
        assert "Agendamos" not in text and "agendar" not in text.lower()

    @pytest.mark.parametrize("vehicle,expected_name,expected_price", [
        ("Mazda CX-5", "Mazda CX-5", "$800.000"),
        ("Tesla Model Y", "Tesla Model Y", "$850.000"),
        ("Ford Territory", "Ford Territory", "$1.300.000"),
        ("BYD Yuan Plus", "BYD Yuan Plus", "$1.300.000"),
    ])
    def test_ppf_piano_black_catalog(self, client, vehicle, expected_name, expected_price):
        c = self._enter_ppf(client, vehicle=vehicle)
        msgs = _preview(client, c, "1", name="Ana")
        text = _texts(msgs)
        media = _all_media(msgs)
        assert expected_name in text
        assert expected_price in text
        # las piezas a cubrir van entre paréntesis, no con guion
        assert "(" in text
        assert any("cloudinary" in u for u in media), f"Se esperaba imagen del catalogo, media={media}"

    def test_ppf_piano_black_not_in_catalog(self, client):
        c = self._enter_ppf(client, vehicle="Renault Duster")
        msgs = _preview(client, c, "1", name="Ana")
        text = _texts(msgs)
        assert "Renault Duster" in text
        # no imagen
        assert not _all_media(msgs)
        # menciona algunos modelos disponibles
        assert "Mazda" in text or "Tesla" in text

    def test_ppf_acrilicas(self, client):
        c = self._enter_ppf(client)
        msgs = _preview(client, c, "2", name="Ana")
        text = _texts(msgs)
        assert "Acrílicas" in text or "acríl" in text.lower()


# ---------- Opción 4 arquitectónico ----------
class TestOption4Arch:
    def test_arch_flow(self, client):
        c = f"prev-{uuid.uuid4().hex}"
        _preview(client, c, "hi", reset=True, name="Luis")
        msgs = _preview(client, c, "4", name="Luis")
        assert "ciudad" in _texts(msgs).lower()
        msgs = _preview(client, c, "Bogotá", name="Luis")
        assert "instalación" in _texts(msgs).lower() or "instalacion" in _texts(msgs).lower()
        msgs = _preview(client, c, "Oficina", name="Luis")
        assert "medidas" in _texts(msgs).lower()
        msgs = _preview(client, c, "3 m x 2 m", name="Luis")
        text = _texts(msgs)
        assert "Bogotá" in text and "Oficina" in text and "3 m x 2 m" in text


# ---------- Volver global ----------
class TestVolver:
    @pytest.mark.parametrize("step_setup", [
        ["1"],                               # step vehicle (opt1)
        ["1", "Mazda 3"],                    # step opt1_choice
        ["2", "Mazda CX-5"],                 # step ppf_protect
        ["4"],                               # step arch_city
        ["4", "Bogotá"],                     # step arch_location
        ["4", "Bogotá", "Casa"],             # step arch_measures
    ])
    def test_volver_from_any_step(self, client, step_setup):
        c = f"prev-{uuid.uuid4().hex}"
        _preview(client, c, "hi", reset=True, name="Test")
        for m in step_setup:
            _preview(client, c, m, name="Test")
        msgs = _preview(client, c, "volver", name="Test")
        assert "Soy Andrea" in _texts(msgs)
