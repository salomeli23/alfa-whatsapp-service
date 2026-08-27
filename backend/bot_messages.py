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

INVALID_PREFIX = (
    "No entendí tu mensaje 🤔. Con gusto te ayudo, elige una de nuestras opciones 👇\n\n"
)

# Pregunta de continuación para servicios vehiculares (opciones 1, 2, 3 y 5)
VEHICLE_PROMPT = (
    "🚙 Para continuar con tu cotización:\n"
    "Por favor indícame la marca y modelo de tu vehículo.\n"
    "Ejemplo:\n"
    "Toyota Corolla\n"
    "o Mazda CX-5"
)

# Confirmación tras recibir la marca/modelo del vehículo
def vehicle_ack(model: str) -> str:
    return (
        f"¡Gracias! 🙌 Registré tu vehículo: *{model}*.\n"
        "Un asesor de Alfa Polarizados preparará tu *cotización personalizada* y te contactará muy pronto. 📞\n\n"
        "Si deseas atención inmediata escribe *ASESOR*, o escribe *MENÚ* para ver otros servicios. 🙂"
    )

# Cierre para el servicio arquitectónico (no vehicular)
ARCH_HANDOFF = (
    "\n\n────────────\n"
    "¿Deseas una cotización personalizada o hablar con un asesor humano? 👨‍🔧\n"
    "Responde *ASESOR* y déjame tu *nombre*, tu *ciudad* y una breve descripción del espacio "
    "(ventanas / fachada / m² aprox.), y un miembro de nuestro equipo te contactará. 📞\n"
    "Escribe *MENÚ* para volver a ver los servicios. 🙌"
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

# Servicios que continúan con la pregunta de vehículo
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


def build_reply(incoming_text: str, session: dict) -> str:
    """Devuelve la respuesta del bot Andrea y actualiza el estado de la sesión (dict)."""
    text = (incoming_text or "").strip()
    normalized = text.lower()

    # Primer mensaje de un contacto → mensaje de bienvenida EXACTO
    if not session.get("greeted"):
        session["greeted"] = True
        session["awaiting_vehicle"] = False
        return WELCOME_MESSAGE

    # Comandos globales
    if any(k in normalized for k in ["asesor", "humano", "agente", "persona"]):
        session["awaiting_vehicle"] = False
        return HANDOFF_ACK

    if any(k in normalized for k in ["menu", "menú", "opciones", "servicios"]):
        session["awaiting_vehicle"] = False
        return WELCOME_MESSAGE

    # Selección de servicio
    if text in SERVICES:
        if text in VEHICLE_SERVICES:
            session["awaiting_vehicle"] = True
            session["service"] = text
            return SERVICES[text] + "\n\n" + VEHICLE_PROMPT
        # Servicio arquitectónico → contacto directo con asesor
        session["awaiting_vehicle"] = False
        return SERVICES[text] + ARCH_HANDOFF

    # Si estamos esperando la marca/modelo del vehículo, tomar el texto como respuesta
    if session.get("awaiting_vehicle"):
        session["awaiting_vehicle"] = False
        session["vehicle"] = text
        return vehicle_ack(text)

    # Saludo → bienvenida
    if any(k in normalized for k in ["hola", "buenas", "buenos", "hi", "hello", "info", "informacion", "información"]):
        return WELCOME_MESSAGE

    # Cualquier otra cosa: repetir el menú amablemente
    return INVALID_PREFIX + WELCOME_MESSAGE
