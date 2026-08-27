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

BACK_HINT = "\n\n↩️ Escribe *volver* en cualquier momento para regresar al menú principal."

AGENDAR = (
    "\n\n📅 ¿Agendamos tu cita? Cuéntame qué *día y hora* te quedan mejor y uno de "
    "nuestros asesores confirmará tu cupo. 😊"
)

INVALID_PREFIX = (
    "No entendí tu mensaje 🤔. Con gusto te ayudo, elige una de nuestras opciones 👇\n\n"
)

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
        "Un asesor de Alfa Polarizados preparará tu *cotización personalizada*."
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

OPT1_CHOICE_PROMPT = (
    "😍 ¿Cuál de los *3 planes* te gustó más?\n"
    "1️⃣ Cerámico\n"
    "2️⃣ High Control\n"
    "3️⃣ IRR\n"
    "Responde con el número o el nombre del plan."
)

OPT1_PLAN_NAMES = {"1": "Plan Cerámico", "2": "Plan High Control", "3": "Plan IRR"}


# ---- Opción 2: PPF ----
PPF_PROTECT_MENU = (
    "Ahora indícame qué deseas proteger:\n"
    "1️⃣ Protección Total\n"
    "2️⃣ Pintura Completa\n"
    "3️⃣ Piano Black\n"
    "4️⃣ Partes Acrílicas\n"
    "Responde con el número o el nombre del servicio."
)

PPF_TOTAL = (
    "✨ Full PPF – Protección Total\n"
    "Este servicio protege completamente tu vehículo:\n"
    "🚗 Pintura\n"
    "🖤 Piano Black\n"
    "💡 Partes Acrílicas\n"
    "✅ Película PPF Premium.\n"
    "✅ Corte de precisión en plotter.\n"
    "✅ Garantía de 10 años.\n"
    "✅ Instalación profesional.\n"
    "Uno de nuestros asesores continuará la conversación para enviarte la cotización exacta según tu vehículo. 😊"
)

PPF_PINTURA = (
    "✨ Full PPF – Protección Total ✨\n"
    "🚗 Cobertura completa: pintura, partes acrílicas y detalles en piano black.\n"
    "✂️ Cortes de precisión en plotter.\n"
    "🛡️ Película PPF Premium.\n"
    "✅ Garantía de 10 años.\n"
    "💰 Inversión total: $10.000.000 COP\n"
    "¿Te reservo tu cupo para asegurar precio y disponibilidad?"
)

PPF_ACRILICAS = (
    "¡Gracias por tu interés en proteger las piezas en piano black de tu vehículo con nuestro ✨ PPF Partes Acrílicas ✨ 🖤.\n\n"
    "Incluye protección en:\n"
    "🔹 Espejos\n"
    "🔹 Farolas\n"
    "🔹 Stops\n\n"
    "✅ Corte de precisión en plotter\n"
    "✅ Película premium con 10 años de garantía\n"
    "✅ Instalación profesional.\n\n"
    "Con este servicio tu vehículo queda libre de rayones, manchas y desgaste, manteniendo ese brillo elegante por mucho más tiempo ✨.\n\n"
    "📅 Agenda hoy mismo para asegurar precio y disponibilidad.\n\n"
    "🤝 ¿Te reservo tu cupo para la instalación?"
)


# ---- Opción 3: Película Antiatraco ----
ANTIATRACO_IMG = "https://res.cloudinary.com/dewemwkqf/image/upload/v1785534807/planes_bjx5xb.jpg"
ANTIATRACO_VIDEO = "https://res.cloudinary.com/dewemwkqf/video/upload/v1785534808/pruebaseguridad_qgxt4u.mp4"


# ---- Opción 5: Detailing Profesional ----
DETAILING_LIST = (
    "✨ ¡Dale a tu vehículo el cuidado premium que realmente merece! 🚗✨\n"
    "Nuestro Detailing Profesional va mucho más allá de un lavado común. Es un proceso completo diseñado para restaurar, proteger y resaltar cada detalle de tu vehículo:\n\n"
    "🔹 *Descontaminación y tratamiento de pintura*\n"
    "Eliminamos impurezas profundas y devolvemos el brillo original, dejando la superficie suave, protegida y como nueva.\n\n"
    "🔹 *Limpieza profunda de tapicería, techos y carteras*\n"
    "Removemos manchas, suciedad y olores, devolviendo frescura y elegancia al interior.\n\n"
    "🔹 *Lavado de motor y chasis*\n"
    "Limpieza técnica que mejora la apariencia y ayuda al buen funcionamiento de tu vehículo.\n\n"
    "🔹 *Lavado general detallado*\n"
    "Cada rincón se limpia con precisión, sin dejar espacios olvidados.\n\n"
    "🔹 *Hidratación de partes negras*\n"
    "Recuperamos el color y la vida de plásticos y molduras, logrando un acabado renovado.\n\n"
    "💎 No es solo limpieza… es transformación.\n"
    "Tu carro no solo se verá mejor, se sentirá como nuevo.\n\n"
    "Cuando quieres agendar ?👩‍💻"
)


# ---- Ubicación ----
LOCATION_MSG = (
    "📍 *Alfa Polarizados*\n"
    "Cra. 49 #134A-41 – Barrio Spring, Bogotá.\n"
    "🕗 Horario: Lunes a Sábado de 8:00 a.m. a 5:00 p.m.\n"
    "🗺️ Ubícanos en Google Maps:\n"
    "https://www.google.com/maps/search/Alfa%20polarizados/@4.7206,-74.0554,17z?hl=en"
)

# Catálogo Piano Black (10 modelos)
PB_MODELS = {
    "mazda cx-30": {"nombre": "Mazda CX-30", "precio": "$900.000 COP", "piezas": 17,
        "detalle": "1. Triángulos puertas delanteras — 2\n2. Parales de las puertas — 4\n3. LS de las puertas — 2\n4. LS del spoiler — 2\n5. Spoiler — 1\n6. Pantalla — 1\n7. Consola central — 1\n8. Módulos elevavidrios — 4",
        "img": "https://res.cloudinary.com/dewemwkqf/image/upload/v1785512481/WhatsApp_Image_2026-07-14_at_12.26.06_PM_za2dys.jpg"},
    "mazda cx-5": {"nombre": "Mazda CX-5", "precio": "$800.000 COP", "piezas": 14,
        "detalle": "1. Triángulos puertas delanteras — 2\n2. Parales de las puertas — 6\n3. Pantalla — 1\n4. Consola central — 1\n5. Módulos elevavidrios — 4",
        "img": "https://res.cloudinary.com/dewemwkqf/image/upload/v1785513545/mazdacx5_s7mbkc.jpg"},
    "mazda 3": {"nombre": "Mazda 3", "precio": "$400.000 COP", "piezas": 10,
        "detalle": "1. Triángulos puertas delanteras — 2\n2. Parales de las puertas — 2\n3. Pantalla — 1\n4. Consola central — 1\n5. Módulos elevavidrios — 4",
        "img": "https://res.cloudinary.com/dewemwkqf/image/upload/v1785513545/mazda3_wm6ioy.jpg"},
    "tesla model 3": {"nombre": "Tesla Model 3", "precio": "$850.000 COP", "piezas": None,
        "detalle": "1. Farolas\n2. Triángulos de espejos\n3. Espejos\n4. Parales laterales\n5. Tapa del cargador\n6. Pantallas — 2",
        "img": "https://res.cloudinary.com/dewemwkqf/image/upload/v1785513545/teslamodel3_mlce70.jpg"},
    "tesla model y": {"nombre": "Tesla Model Y", "precio": "$850.000 COP", "piezas": None,
        "detalle": "1. Farolas\n2. Triángulos de espejos\n3. Espejos\n4. Parales laterales\n5. Tapa del cargador\n6. Pantallas — 2",
        "img": "https://res.cloudinary.com/dewemwkqf/image/upload/v1785513545/teslamodely_lugjft.jpg"},
    "ford territory": {"nombre": "Ford Territory", "precio": "$1.100.000 COP", "piezas": 16,
        "detalle": "1. Piano black inferior farolas — 2\n2. Espejos — 2\n3. Parales de las puertas — 8\n4. LS del tapabaúl — 2\n5. Pantalla — 1\n6. Consola central — 1",
        "img": "https://res.cloudinary.com/dewemwkqf/image/upload/v1785513545/fordterritory_vjoyml.jpg"},
    "deepal s05": {"nombre": "Deepal S05", "precio": "$800.000 COP", "piezas": 9,
        "detalle": "1. Triángulo puertas delanteras — 2\n2. Espejos — 2\n3. Parales de las puertas — 2\n4. LS del spoiler — 2\n5. Pantalla — 1",
        "img": "https://res.cloudinary.com/dewemwkqf/image/upload/v1785513544/deepals05_otu2r2.jpg"},
    "deepal s07": {"nombre": "Deepal S07", "precio": "$1.000.000 COP", "piezas": 11,
        "detalle": "1. Triángulo puertas delanteras — 2\n2. Espejos — 2\n3. Parales de las puertas — 2\n4. Ventana lateral trasera — 2\n5. LS del spoiler — 2\n6. Pantalla — 1",
        "img": "https://res.cloudinary.com/dewemwkqf/image/upload/v1785513545/deepals07_cszjav.jpg"},
    "byd yuan up": {"nombre": "BYD Yuan UP", "precio": "$900.000 COP", "piezas": 14,
        "detalle": "1. Parales panorámico — 2\n2. Espejos — 2\n3. Parales de las puertas — 4\n4. LS de las puertas — 2\n5. LS del spoiler — 2\n6. Pantallas — 2",
        "img": "https://res.cloudinary.com/dewemwkqf/image/upload/v1785513544/bydyuanup_p7wh5w.jpg"},
    "byd yuan plus": {"nombre": "BYD Yuan Plus", "precio": "$1.300.000 COP", "piezas": 23,
        "detalle": "1. Triángulos de los espejos — 2\n2. Espejos — 2\n3. Parales de las puertas — 4\n4. LS de las puertas — 2\n5. LS spoiler — 2\n6. Pantallas — 2\n7. Consola central — 1\n8. Módulos elevavidrios — 4\n9. Parales internos en piano black de puertas — 4",
        "img": "https://res.cloudinary.com/dewemwkqf/image/upload/v1785513544/bydyuanplus_z1fi14.jpg"},
}


def _collapse(s: str) -> str:
    return "".join(ch for ch in s.lower() if ch.isalnum())


def find_pb_model(vehicle_text: str):
    if not vehicle_text:
        return None
    n = vehicle_text.lower().strip()
    nc = _collapse(vehicle_text)
    for key, data in PB_MODELS.items():
        if key in n or n in key:
            return data
        kc = _collapse(key)
        if kc in nc or nc in kc:
            return data
    return None


# ---- Opción 4: flujo arquitectónico ----
ARCH_CITY = (
    "Para ayudarte con tu proyecto de Polarizado Arquitectónico, primero indícame:\n"
    "📍 ¿En qué ciudad se encuentra el proyecto?"
)

ARCH_LOCATION = (
    "Ahora cuéntame:\n"
    "🏢 ¿Dónde se realizará la instalación?\n"
    "Por ejemplo:\n"
    "- Casa\n- Apartamento\n- Oficina\n- Local comercial\n- Edificio\n- Otro"
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
        "Un asesor de Alfa Polarizados preparará tu *cotización personalizada*."
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
        "✅ Ideal para Piano Black y superficies acrílicas 🔲"
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
    session["service"] = sid
    name = session.get("name")
    saludo = f"¡Perfecto, {name}! 🙌\n\n" if name else ""
    if sid in VEHICLE_SERVICES:
        session["step"] = "vehicle"
        return [_msg(saludo + SERVICES[sid] + "\n\n" + VEHICLE_PROMPT + BACK_HINT)]
    session["step"] = "arch_city"
    return [_msg(saludo + SERVICES[sid] + "\n\n" + ARCH_CITY + BACK_HINT)]


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
    session["step"] = "opt1_choice"
    msgs.append(_msg(OPT1_CHOICE_PROMPT + BACK_HINT))
    return msgs


def _piano_black(session: dict):
    """Respuesta Piano Black detectando el modelo del vehículo indicado."""
    vehicle = session.get("vehicle", "")
    data = find_pb_model(vehicle)
    if data:
        piezas = f"\n🔩 Piezas: {data['piezas']}" if data.get("piezas") else ""
        text = (
            f"🖤 *Piano Black – {data['nombre']}*\n\n"
            f"💵 Precio: *{data['precio']}*{piezas}\n\n"
            f"*Piezas a cubrir:*\n{data['detalle']}\n\n"
            "✅ Película PPF Premium · ✅ Corte de precisión en plotter · ✅ Garantía de 10 años."
            + AGENDAR
        )
        return [_msg(text, media=[data["img"]])]
    # Modelo no encontrado en el catálogo
    disponibles = ", ".join(d["nombre"] for d in PB_MODELS.values())
    text = (
        f"🖤 *Piano Black*\n"
        f"Aún no tengo el detalle exacto para *{vehicle}* en mi catálogo. "
        "Un asesor te preparará la cotización personalizada según tu vehículo. 😊\n\n"
        f"Modelos con detalle disponible: {disponibles}." + AGENDAR
    )
    return [_msg(text)]


def build_reply(incoming_text: str, session: dict):
    """Devuelve una lista de mensajes [{text, media[]}] y actualiza el estado de la sesión."""
    text = (incoming_text or "").strip()
    normalized = text.lower()

    # Primer mensaje → bienvenida EXACTA
    if not session.get("greeted"):
        session["greeted"] = True
        session["step"] = None
        return [_msg(WELCOME_MESSAGE)]

    # Comando global: volver al menú
    if normalized in ("volver", "atras", "atrás", "menu", "menú", "regresar", "inicio") or any(
        k in normalized for k in ["opciones", "servicios"]
    ):
        session["step"] = None
        return [_msg(WELCOME_MESSAGE)]

    # Comando global: asesor humano
    if any(k in normalized for k in ["asesor", "humano", "agente", "persona"]):
        session["step"] = None
        return [_msg(HANDOFF_ACK)]

    # Intención global: ubicación / dirección / horario (no altera el paso actual)
    if any(k in normalized for k in [
        "ubicad", "ubicac", "direccion", "dirección", "donde estan", "dónde están",
        "donde queda", "dónde queda", "mapa", "gps", "como llego", "cómo llego",
        "horario", "atienden", "ciudad estan", "ubicados"
    ]):
        return [_msg(LOCATION_MSG)]

    step = session.get("step")

    # ----- Manejo de pasos activos (antes de la selección de menú) -----
    if step == "vehicle":
        session["vehicle"] = text
        sid = session.get("service")
        name = session.get("name", "")
        if sid == "1":
            return _option1_plans(session, text)
        if sid == "2":
            session["step"] = "ppf_protect"
            return [_msg(vehicle_ack(name, text) + "\n\n" + PPF_PROTECT_MENU + BACK_HINT)]
        if sid == "3":
            session["step"] = None
            saludo = f"¡Gracias, {name}! 🙌 Registré tu vehículo: *{text}*." if name else f"¡Gracias! 🙌 Registré tu vehículo: *{text}*."
            return [
                _msg(saludo + "\n\nEstos son nuestros *planes de Película Antiatraco* 🚨👇", media=[ANTIATRACO_IMG]),
                _msg("▶️ *Prueba de Seguridad*", media=[ANTIATRACO_VIDEO]),
                _msg("¿Deseas *agendar* tu instalación? Un asesor te ayudará a coordinar la cita. 😊" + AGENDAR + BACK_HINT),
            ]
        if sid == "5":
            session["step"] = None
            return [
                _msg(DETAILING_LIST),
                _msg("Un asesor te ayudará a coordinar tu cita. 😊" + BACK_HINT),
            ]
        session["step"] = None
        return [_msg(vehicle_ack(name, text) + AGENDAR + BACK_HINT)]

    if step == "opt1_choice":
        plan = None
        if normalized in OPT1_PLAN_NAMES:
            plan = OPT1_PLAN_NAMES[normalized]
        elif "ceram" in normalized or "cerám" in normalized:
            plan = "Plan Cerámico"
        elif "high" in normalized or "control" in normalized:
            plan = "Plan High Control"
        elif "irr" in normalized or "infrarroj" in normalized:
            plan = "Plan IRR"
        if not plan:
            return [_msg("Por favor elige un plan válido 🙂\n\n" + OPT1_CHOICE_PROMPT + BACK_HINT)]
        session["opt1_plan"] = plan
        session["step"] = None
        return [_msg(f"¡Excelente elección! 🙌 El *{plan}* es ideal para tu vehículo." + AGENDAR + BACK_HINT)]

    if step == "ppf_protect":
        session["step"] = None
        if normalized in ("1",) or "total" in normalized:
            return [_msg(PPF_TOTAL + AGENDAR + BACK_HINT)]
        if normalized in ("2",) or "pintura" in normalized:
            return [_msg(PPF_PINTURA + BACK_HINT)]
        if normalized in ("3",) or "piano" in normalized:
            msgs = _piano_black(session)
            msgs[-1]["text"] += BACK_HINT
            return msgs
        if normalized in ("4",) or "acril" in normalized or "acríl" in normalized:
            return [_msg(PPF_ACRILICAS + BACK_HINT)]
        session["step"] = "ppf_protect"
        return [_msg("Por favor elige una opción válida 🙂\n\n" + PPF_PROTECT_MENU + BACK_HINT)]

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
        return [_msg(arch_ack(session.get("name", ""), session.get("arch_city", "-"),
                              session.get("arch_location", "-"), text) + AGENDAR + BACK_HINT)]

    # ----- Sin paso activo: selección de servicio en el menú -----
    if text in SERVICES:
        return _deliver_service(session, text)

    if any(k in normalized for k in ["hola", "buenas", "buenos", "hi", "hello", "info", "informacion", "información"]):
        return [_msg(WELCOME_MESSAGE)]

    return [_msg(INVALID_PREFIX + WELCOME_MESSAGE)]
