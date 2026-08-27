WELCOME_MESSAGE = (
    "¡Hola! 👋 Soy Andrea 🙋‍♀️, asesora de Alfa Polarizados.\n"
    "📍 Estamos ubicados en la Cra. 49 #134A-41 – Barrio Spring, Bogotá.\n"
    "Estoy lista para ayudarte a elegir el mejor servicio para tu vehículo. 😊\n"
    "Trabajamos con materiales de alta calidad y procesos profesionales, diseñados para clientes que realmente valoran la calidad y el detalle. 🛡️\n"
    "💬 Indícame qué servicio deseas:\n"
    "1️⃣ Polarizado y seguridad vehicular 🚗\n"
    "2️⃣ PPF (Protección de pintura, Piano Black y partes acrílicas)\n"
    "3️⃣ Película Antiatraco 🚨\n"
    "4️⃣ Polarizado Arquitectónico 🏢\n"
    "5️⃣ Detailing Profesional ✨\n"
    "📌 Responde con el número de la opción."
)

# Se muestra en cualquier parte de la conversación
BACK_HINT = "\n\n↩️ Escribe *volver* en cualquier momento para regresar al menú principal."

INVALID_PREFIX = (
    "No entendí tu mensaje 🤔. Con gusto te ayudo, elige una de nuestras opciones 👇\n\n"
)

ASK_NAME = "Antes de darte la información, ¿me regalas tu *nombre*? 🙂"

# Pregunta de continuación para servicios vehiculares (opciones 1, 2, 3 y 5)
VEHICLE_PROMPT = (
    "🚙 Para continuar con tu cotización:\n"
    "Por favor indícame la marca y modelo de tu vehículo.\n"
    "Ejemplo:\n"
    "Toyota Corolla\n"
    "o Mazda CX-5"
)


def vehicle_ack(name: str, model: str) -> str:
    saludo = f"¡Gracias, {name}! 🙌" if name else "¡Gracias! 🙌"
    return (
        f"{saludo} Registré tu vehículo: *{model}*.\n"
        "Un asesor de Alfa Polarizados preparará tu *cotización personalizada* y te contactará muy pronto. 📞\n\n"
        "Si deseas atención inmediata escribe *ASESOR*."
    )


# ---- Opción 1: planes y videos ----
PLANS_OPT1 = [
    {
        "name": "Plan Cerámico 🧊",
        "img": "https://res.cloudinary.com/dewemwkqf/image/upload/v1787153675/alfaceramico_qilg67.jpg",
        "desc": (
            "Tecnología 100% cerámica. Máximo rechazo de calor sin oscurecer de más y "
            "sin interferencia en señal de celular/GPS. Ideal si buscas confort y calidad premium."
        ),
    },
    {
        "name": "Plan High Control 🎛️",
        "img": "https://res.cloudinary.com/dewemwkqf/image/upload/v1787153675/alfahighcontrol_mrfsyh.jpg",
        "desc": (
            "Excelente control solar y privacidad a un gran precio. Buen rechazo de calor y "
            "protección UV para el uso diario de tu vehículo."
        ),
    },
    {
        "name": "Plan IRR (Rechazo Infrarrojo) 🔆",
        "img": "https://res.cloudinary.com/dewemwkqf/image/upload/v1787153675/alfa_irr_ghcrjt.jpg",
        "desc": (
            "Máximo rechazo de rayos infrarrojos para la mayor sensación de frescura y una "
            "claridad excepcional. La opción de más alto desempeño."
        ),
    },
]

VIDEOS_OPT1 = [
    {"title": "🔧 Instalación profesional", "url": "https://res.cloudinary.com/dewemwkqf/video/upload/v1787154076/instalacion_seecyr.mp4"},
    {"title": "🛡️ Prueba de seguridad", "url": "https://res.cloudinary.com/dewemwkqf/video/upload/v1787154076/peliculaseguridad_i8zope.mp4"},
    {"title": "👀 Visibilidad", "url": "https://res.cloudinary.com/dewemwkqf/video/upload/v1787154083/visibilidad_il08yd.mp4"},
]


# ---- Opción 4: flujo arquitectónico ----
ARCH_CITY = (
    "Para ayudarte con tu proyecto de Polarizado Arquitectónico, primero indícame:\n"
    "📍 ¿En qué ciudad se encuentra el proyecto?"
)

ARCH_LOCATION = (
    "Ahora cuéntame:\n"
    "🏢 ¿Dónde se realizará la instalación?\n"
    "Por ejemplo:\n"
    "- Casa\n"
    "- Apartamento\n"
    "- Oficina\n"
    "- Local comercial\n"
    "- Edificio\n"
    "- Otro"
)

ARCH_MEASURES = (
    "Ahora indícame las medidas aproximadas del vidrio.\n"
    "Ejemplos:\n"
    "📏 2 m x 1.50 m\n"
    "📏 3 m x 2 m\n"
    "Si son varias ventanas puedes escribirlas todas."
)


def arch_ack(name: str, city: str, location: str, measures: str) -> str:
    saludo = f"¡Perfecto, {name}! 🙌" if name else "¡Perfecto! 🙌"
    return (
        f"{saludo} Resumen de tu proyecto de *Polarizado Arquitectónico*:\n"
        f"📍 Ciudad: *{city}*\n"
        f"🏢 Lugar: *{location}*\n"
        f"📏 Medidas: *{measures}*\n\n"
        "Un asesor de Alfa Polarizados preparará tu *cotización personalizada* y te contactará muy pronto. 📞\n\n"
        "Si deseas atención inmediata escribe *ASESOR*."
    )


HANDOFF_ACK = (
    "¡Perfecto! 🙌 Un asesor de Alfa Polarizados revisará tu solicitud y te contactará muy pronto. 📞\n"
    "Para agilizar tu atención, envíame en un solo mensaje: 👇\n"
    "• Tu *nombre* 🧑\n"
    "• *Marca y modelo* de tu vehículo (o descripción del espacio) 🚗\n"
    "• Tu *ciudad* 📍\n"
    "• El *servicio* que te interesa ✨\n\n"
    "¡Gracias por confiar en Alfa Polarizados! 💙"
)

VEHICLE_SERVICES = {"1", "2", "3", "5"}

SERVICES = {
    "1": (
        "🚗 *Polarizado y Seguridad Vehicular*\n\n"
        "Protege tu vehículo y a tus ocupantes con nuestras láminas de alta gama:\n\n"
        "✅ Rechazo de calor hasta del 85% para un manejo más fresco 🌡️\n"
        "✅ Bloqueo del 99% de rayos UV (protege tu piel y el interior) ☀️\n"
        "✅ Mayor privacidad y seguridad ante robos 🔒\n"
        "✅ Reduce el deslumbramiento y mejora la visibilidad 👀\n"
        "✅ Garantía y instalación profesional certificada 🛡️\n\n"
        "💵 Desde *$250.000 COP* (varía según el modelo del vehículo y el tipo de lámina)."
    ),
    "2": (
        "🛡️ *PPF – Protección de Pintura (Paint Protection Film)*\n\n"
        "La máxima protección para la pintura de tu auto, Piano Black y partes acrílicas:\n\n"
        "✅ Película transparente autorreparable ante rayones ligeros ♻️\n"
        "✅ Protección contra piedras, insectos, arañazos y químicos 🪨\n"
        "✅ Conserva el brillo de fábrica y el valor de reventa ✨\n"
        "✅ Acabado brillante o mate, invisible al ojo 👌\n"
        "✅ Ideal para Piano Black y superficies acrílicas 🔲\n\n"
        "💵 Desde *$900.000 COP* (según piezas y cobertura: parcial o total)."
    ),
    "3": (
        "🚨 *Película Antiatraco (Película de Seguridad)*\n\n"
        "Una capa extra de seguridad que puede marcar la diferencia:\n\n"
        "✅ Vidrio de mayor resistencia ante impactos y roturas 💥\n"
        "✅ Dificulta y retrasa los intentos de robo 🔐\n"
        "✅ Los fragmentos se mantienen unidos, evitando lesiones 🩹\n"
        "✅ Combinable con polarizado para privacidad total 🕶️\n"
        "✅ Instalación profesional con garantía 🛡️\n\n"
        "💵 Desde *$450.000 COP* (según el grosor de la película y el vehículo)."
    ),
    "4": (
        "🏢 *Polarizado Arquitectónico*\n\n"
        "Confort y eficiencia para hogares, oficinas y locales:\n\n"
        "✅ Reduce el calor y el consumo de aire acondicionado ❄️\n"
        "✅ Bloqueo de rayos UV que protege muebles y pisos 🛋️\n"
        "✅ Mayor privacidad sin perder iluminación natural 🌤️\n"
        "✅ Películas de seguridad y decorativas disponibles 🪟\n"
        "✅ Instalación para ventanas y fachadas de vidrio 🏗️\n\n"
        "💵 Cotización *por m²* según el tipo de película y la superficie a cubrir."
    ),
    "5": (
        "✨ *Detailing Profesional*\n\n"
        "Devuélvele a tu vehículo el brillo de concesionario:\n\n"
        "✅ Lavado premium y descontaminación de pintura 🧼\n"
        "✅ Pulido y corrección de rayones y micro-marcas 💎\n"
        "✅ Recubrimiento cerámico de larga duración 🛡️\n"
        "✅ Detallado profundo de interiores 🧽\n"
        "✅ Restauración de faros y plásticos 💡\n\n"
        "💵 Desde *$180.000 COP* (según el paquete y el estado del vehículo)."
    ),
}


def _msg(text: str, media=None):
    return {"text": text, "media": media or []}


def _deliver_service(session: dict, sid: str):
    """Entrega la información de un servicio e inicia su flujo de seguimiento."""
    session["service"] = sid
    if sid in VEHICLE_SERVICES:
        session["step"] = "vehicle"
        return [_msg(SERVICES[sid] + "\n\n" + VEHICLE_PROMPT + BACK_HINT)]
    # Opción 4 (arquitectónico)
    session["step"] = "arch_city"
    return [_msg(SERVICES[sid] + "\n\n" + ARCH_CITY + BACK_HINT)]


def _option1_plans(session: dict, model: str):
    name = session.get("name", "")
    saludo = f"¡Gracias, {name}! 🙌" if name else "¡Gracias! 🙌"
    msgs = [
        _msg(
            f"{saludo} Registré tu vehículo: *{model}*.\n\n"
            "Estos son nuestros *3 planes de Polarizado y Seguridad Vehicular* 👇"
        )
    ]
    for p in PLANS_OPT1:
        msgs.append(_msg(f"*{p['name']}*\n{p['desc']}", media=[p["img"]]))
    msgs.append(_msg("🎥 Mira nuestros resultados en video:"))
    for v in VIDEOS_OPT1:
        msgs.append(_msg(f"▶️ {v['title']}", media=[v["url"]]))
    msgs.append(
        _msg(
            "Un asesor de Alfa Polarizados preparará tu *cotización personalizada* y te contactará muy pronto. 📞\n\n"
            "Si deseas atención inmediata escribe *ASESOR*." + BACK_HINT
        )
    )
    return msgs


def build_reply(incoming_text: str, session: dict):
    """Devuelve una lista de mensajes [{text, media[]}] y actualiza el estado de la sesión."""
    text = (incoming_text or "").strip()
    normalized = text.lower()

    # Primer mensaje de un contacto → mensaje de bienvenida EXACTO
    if not session.get("greeted"):
        session["greeted"] = True
        session["step"] = None
        return [_msg(WELCOME_MESSAGE)]

    # Comando global: volver al menú principal
    if normalized in ("volver", "atras", "atrás", "menu", "menú", "regresar", "inicio") or any(
        k in normalized for k in ["opciones", "servicios"]
    ):
        session["step"] = None
        return [_msg(WELCOME_MESSAGE)]

    # Comando global: asesor humano
    if any(k in normalized for k in ["asesor", "humano", "agente", "persona"]):
        session["step"] = None
        return [_msg(HANDOFF_ACK)]

    step = session.get("step")

    # Capturar el nombre y saludar, luego entregar el servicio elegido
    if step == "ask_name":
        session["name"] = text
        sid = session.pop("pending_service", None)
        greeting = _msg(f"¡Mucho gusto, {text}! 😊 Con gusto te ayudo. 🙌")
        if sid:
            return [greeting] + _deliver_service(session, sid)
        session["step"] = None
        return [greeting, _msg(WELCOME_MESSAGE)]

    # Selección de servicio en el menú
    if text in SERVICES:
        # Si aún no tenemos el nombre, lo pedimos primero
        if not session.get("name"):
            session["pending_service"] = text
            session["step"] = "ask_name"
            return [_msg(ASK_NAME + BACK_HINT)]
        return _deliver_service(session, text)

    # Flujo vehicular: esperando la marca/modelo del vehículo
    if step == "vehicle":
        session["step"] = None
        session["vehicle"] = text
        if session.get("service") == "1":
            return _option1_plans(session, text)
        return [_msg(vehicle_ack(session.get("name", ""), text) + BACK_HINT)]

    # Flujo arquitectónico: ciudad → lugar → medidas → asesor
    if step == "arch_city":
        session["arch_city"] = text
        session["step"] = "arch_location"
        return [_msg(ARCH_LOCATION + BACK_HINT)]

    if step == "arch_location":
        session["arch_location"] = text
        session["step"] = "arch_measures"
        return [_msg(ARCH_MEASURES + BACK_HINT)]

    if step == "arch_measures":
        session["arch_measures"] = text
        session["step"] = None
        return [
            _msg(
                arch_ack(
                    session.get("name", ""),
                    session.get("arch_city", "-"),
                    session.get("arch_location", "-"),
                    text,
                )
                + BACK_HINT
            )
        ]

    # Saludo → bienvenida
    if any(k in normalized for k in ["hola", "buenas", "buenos", "hi", "hello", "info", "informacion", "información"]):
        return [_msg(WELCOME_MESSAGE)]

    # Cualquier otra cosa: repetir el menú amablemente
    return [_msg(INVALID_PREFIX + WELCOME_MESSAGE)]
