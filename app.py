# 🎯 Conti Clasificador — una app mínima para mostrar IA clasificando casos

import json
import os
from datetime import datetime

import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError

from conti import SEMAFORO, clasificar, conversar, notificar

RUTA_CASOS = "casos.json"
FALTA_LLAVE = "Falta configurar LLM_API_KEY en .streamlit/secrets.toml 🔑"

st.set_page_config(page_title="Conti Clasificador", page_icon="🎯")


# 💾 Guardamos los casos en un JSON para que sobrevivan a la recarga
def cargar_casos() -> list:
    """Recupera los casos guardados en disco.

    Lee el JSON donde vive el historial para que los casos sobrevivan a la recarga
    de la página.

    Devuelve:
        La lista de casos guardados, o una lista vacía si el archivo no existe o
        está dañado.
    """
    if not os.path.exists(RUTA_CASOS):
        return []
    try:
        with open(RUTA_CASOS, encoding="utf-8") as archivo:
            datos = json.load(archivo)
            return datos if isinstance(datos, list) else []
    except Exception:
        return []


def guardar_casos(casos: list) -> None:
    """Guarda en disco la lista completa de casos.

    Escribe el historial en el JSON para que no se pierda al recargar la página.

    Argumentos:
        casos: La lista de casos que vive en la sesión.

    Devuelve:
        Nada.
    """
    try:
        with open(RUTA_CASOS, "w", encoding="utf-8") as archivo:
            json.dump(casos, archivo, ensure_ascii=False, indent=2)
    except Exception:
        st.error("No se pudo guardar el archivo de casos 💾")


# 💾 Armamos el caso, lo guardamos y lo devolvemos
def guardar_caso(nombre: str, contacto: str, motivo_contacto: str, resultado: dict) -> dict:
    """Crea un caso nuevo a partir de la clasificación y lo deja guardado.

    Junta los datos de contacto con lo que devolvió la IA, le asigna un id y una
    fecha, lo agrega a la sesión y lo escribe en el JSON.

    Argumentos:
        nombre: Quién reporta el caso, sea empresa o persona.
        contacto: Cómo responderle, sea teléfono o correo.
        motivo_contacto: El texto original con el que se abrió el caso.
        resultado: La clasificación que devolvió la IA.

    Devuelve:
        El caso ya armado como diccionario, tal como quedó guardado.
    """
    caso = {
        "id": max((c.get("id", 0) for c in st.session_state.casos if isinstance(c, dict)), default=0) + 1,
        "nombre": nombre,
        "contacto": contacto,
        "motivo_contacto": motivo_contacto,
        "semaforo": resultado.get("semaforo", "rojo"),
        "explicacion": resultado.get("motivo", ""),
        "acciones": resultado.get("acciones", []) if isinstance(resultado.get("acciones"), list) else [],
        "estado": "abierto",
        "notificado": False,
        "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
    }
    st.session_state.casos.append(caso)
    guardar_casos(st.session_state.casos)
    return caso


# 🔐 Leemos la clave desde secrets.toml sin rompernos si el archivo no existe
def leer_secreto(clave: str) -> str:
    """Busca un secreto en la configuración sin tumbar la app.

    Lee el valor desde secrets.toml y, si el archivo no existe o la clave no está,
    sigue adelante con un valor vacío.

    Argumentos:
        clave: El nombre del secreto que se quiere leer.

    Devuelve:
        El valor encontrado, o una cadena vacía si no está disponible.
    """
    try:
        return st.secrets.get(clave, "")
    except Exception:
        return ""


# 💬 Cada conversación con Conti arranca con un saludo y una primera pregunta
def chat_nuevo() -> list:
    """Abre una conversación nueva con el saludo inicial de Conti.

    El historial arranca con una sola intervención del asistente que saluda y
    pregunta quién escribe.

    Devuelve:
        El historial con un único mensaje del asistente.
    """
    return [
        {
            "role": "assistant",
            "content": "¡Hola! Soy Conti 🎯 Cuéntame qué pasó y yo lo clasifico. ¿Quién eres o de qué empresa escribes?",
        }
    ]


# 🎯 Cada mensaje nuevo lleva la vista y el cursor al campo de texto
def enfocar_campo() -> None:
    """Lleva la vista y el cursor al campo de texto del chat.

    Se ejecuta después de cada mensaje para que la persona pueda seguir escribiendo
    sin tener que buscar el campo con el mouse.

    Devuelve:
        Nada.
    """
    st.iframe(
        f"""<script>
        setTimeout(() => {{
            const campo = window.parent.document.querySelector('[data-testid="stChatInputTextArea"]');
            if (campo) {{ campo.scrollIntoView({{behavior:"smooth", block:"center"}}); campo.focus(); }}
        }}, 300);
        </script><!-- {len(st.session_state.mensajes)} -->""",
        height=1,
    )


if "casos" not in st.session_state:
    st.session_state.casos = cargar_casos()

if "mensajes" not in st.session_state:
    st.session_state.mensajes = chat_nuevo()

if "pendiente" not in st.session_state:
    st.session_state.pendiente = None

api_key = leer_secreto("LLM_API_KEY") or os.getenv("LLM_API_KEY", "")
base_url = leer_secreto("LLM_BASE_URL") or os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1")
modelo = leer_secreto("LLM_MODEL") or os.getenv("LLM_MODEL", "deepseek/deepseek-v4.1-flash-1017")

# 🌗 Los colores de cada tema, en un solo lugar
TEMAS = {
    "oscuro": {"fondo": "#0e1117", "panel": "#262730", "texto": "#fafafa", "suave": "#a3a8b8", "borde": "#3a3d4a"},
    "claro": {"fondo": "#ffffff", "panel": "#f0f2f6", "texto": "#31333f", "suave": "#6b7280", "borde": "#d5d8e0"},
}


# 🎨 Repintamos la app con los colores del tema elegido
def pintar_tema(nombre: str) -> None:
    """Aplica a la app los colores del tema elegido.

    Inyecta el CSS que define fondos, textos y bordes según la paleta clara u
    oscura.

    Argumentos:
        nombre: El tema que se quiere pintar, "oscuro" o "claro".

    Devuelve:
        Nada.
    """
    c = TEMAS[nombre]
    st.html(
        f"""<style>
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{ background: {c['fondo']} !important; }}
        [data-testid="stMainBlockContainer"], .block-container {{ max-width: 1000px !important; }}
        [data-testid="stMarkdownContainer"] :is(p, h1, h2, h3, h4, h5, h6, li, span, strong, em) {{ color: {c['texto']} !important; }}
        [data-testid="stTab"] p {{ color: {c['suave']} !important; }}
        [data-testid="stTab"][aria-selected="true"] p {{ color: {c['texto']} !important; }}
        [data-testid="stCaptionContainer"] :is(p, span, small) {{ color: {c['suave']} !important; }}
        [data-testid="stWidgetLabel"] :is(label, p), [data-testid="stMetricLabel"], [data-testid="stMetricValue"],
        [data-testid="stToolbar"] button {{ color: {c['texto']} !important; }}
        [data-testid="stChatInput"] div {{ background: transparent !important; }}
        [data-testid="stChatInput"] {{ background: {c['panel']} !important; border: 1px solid {c['borde']} !important; border-radius: 12px; }}
        [data-testid="stChatInputTextArea"] {{ color: {c['texto']} !important; }}
        [data-testid="stChatInputTextArea"]::placeholder {{ color: {c['suave']} !important; opacity: 1; }}
        [data-testid="stTextArea"] textarea::placeholder, [data-testid="stTextInput"] input::placeholder {{ color: {c['suave']} !important; }}
        [data-testid="stTextAreaRootElement"], [data-testid="stTextInputRootElement"],
        [data-testid="stSelectbox"] div {{
            background: {c['panel']} !important; border-color: {c['borde']} !important; color: {c['texto']} !important;
        }}
        [data-testid="stSelectbox"] :is(input, button) {{ color: {c['texto']} !important; }}
        [data-baseweb="popover"] :is(ul, li) {{ background: {c['panel']} !important; color: {c['texto']} !important; }}
        [data-testid="stTextArea"] textarea, [data-testid="stTextInput"] input {{ color: {c['texto']} !important; }}
        [data-testid="stExpander"] details {{
            background: {c['panel']} !important; border: 1px solid {c['borde']} !important; border-radius: 8px;
        }}
        [data-testid="stExpander"] summary {{ background: transparent !important; }}
        [data-testid="stChatMessage"] {{ background: {c['panel']} !important; border-radius: 12px; }}
        [data-testid="stBaseButton-secondary"], [data-testid="stBaseButton-secondaryFormSubmit"] {{
            background: {c['panel']} !important; color: {c['texto']} !important; border: 1px solid {c['borde']} !important;
        }}
        [data-testid="stBaseButton-secondary"] :is(p, span), [data-testid="stBaseButton-secondaryFormSubmit"] :is(p, span) {{
            color: {c['texto']} !important;
        }}
        [data-testid="stAlert"] :is(p, span) {{ color: #fafafa !important; }}
        </style>""",
    )


# 🕹️ El interruptor vive arriba a la derecha, junto al título
col_titulo, col_tema = st.columns([5, 1], vertical_alignment="center")
with col_titulo:
    st.title("🎯 Conti Clasificador")
with col_tema:
    oscuro = st.toggle("🌙 Oscuro", value=True, key="modo_oscuro")

pintar_tema("oscuro" if oscuro else "claro")

# 📖 Qué es y qué hace, para que cualquiera entienda el proyecto de entrada
st.write(
    "**Conti Clasificador** es un asistente de IA que pone orden en el caos del soporte 🚦 "
    "Recibe cada pedido —por chat o pegando un correo completo—, entiende qué está pasando y lo "
    "clasifica en un semáforo de urgencia para que Producción sepa **qué atender primero y qué puede esperar**."
)
st.write(
    "Sin formularios eternos ni hojas de cálculo a mano: cuentas tu caso en tus palabras y Conti devuelve "
    "un resumen, el motivo de la clasificación y los próximos pasos, listo para confirmar y guardar."
)

col_conversa, col_clasifica, col_gestion = st.columns(3)
with col_conversa:
    st.markdown("#### 💬 Conversa")
    st.caption("Describe tu caso en lenguaje natural. Conti pregunta lo justo, una cosa a la vez, y nada más.")
with col_clasifica:
    st.markdown("#### 🚦 Clasifica")
    st.caption("Semáforo de urgencia con SLA: 🔴 15 minutos · 🟡 mismo día · 🟢 24-48 horas.")
with col_gestion:
    st.markdown("#### 🗂️ Gestiona")
    st.caption("Busca, filtra, cierra y notifica casos desde un solo lugar, sin salir de la app.")

# 🧠 Los tres desplegables: qué hace, para quién es y cómo está hecho
with st.expander("🧠 ¿Cómo funciona?"):
    st.write("**1. 💬 Hablas con Conti.** Describes tu caso como se lo contarías a un compañero. También puedes pegar un correo entero.")
    st.write("**2. 🧠 Conti lo interpreta.** El modelo recibe tu mensaje con un prompt que define el semáforo y devuelve un JSON con el nivel, un resumen, el motivo y las acciones sugeridas.")
    st.write("**3. ✅ Confirmas y se guarda.** Revisas la clasificación, la corriges si hace falta y el caso queda abierto en **Gestión**, listo para cerrar o notificar a Producción.")
    st.caption("🎓 Todo el contenido vive en `conti.py`: un prompt, dos funciones y cero magia.")

with st.expander("🏢 ¿Para quién es?"):
    st.write(
        "Conti Clasificador es la demo de una propuesta para **Sermatick Cia Ltda**, empresa de desarrollo de "
        "software que ofrece un sistema de facturación electrónica como servicio. La usa el personal de soporte, "
        "la primera línea frente al cliente, para ordenar y priorizar cada caso; lo que escala llega al "
        "**departamento de Producción** ya clasificado. El objetivo es servir de MVP para presentar la propuesta "
        "e implementarla después en producción."
    )

with st.expander("🛠️ ¿Cómo está construido?"):
    st.write("**🧠 El prompt.** Un texto en `conti.py` define el semáforo; no hay reglas escondidas en el código.")
    st.write("**🤝 El SDK.** Las llamadas usan el **SDK de OpenAI**, así que sirve cualquier API compatible.")
    st.write("**🌐 El modelo.** El proveedor es **OpenRouter** con el modelo **DeepSeek V4 Flash**.")
    st.write("**🔐 Los secretos.** La API key y la URL viven en `.streamlit/secrets.toml`, ignorado por git; la plantilla pública es `secrets.example.toml`.")

# ✅ Aviso que se desvanece solo a los 5 segundos
if "aviso" in st.session_state:
    st.toast(st.session_state.pop("aviso"), duration=5)

# 📥 Tres pestañas: charlar, pegar correo y gestionar
tab_chat, tab_texto, tab_gestion = st.tabs(["💬 Chat agéntico", "📋 Pegar correo", "🗂️ Gestión"])

# 💬 Pestaña 1: la conversación con Conti
with tab_chat:
    # 🗨️ Dibujamos toda la conversación
    for mensaje in st.session_state.mensajes:
        with st.chat_message(mensaje["role"]):
            st.write(mensaje["content"])
            if mensaje.get("detalle_error"):
                with st.expander("🔍 Detalle técnico"):
                    st.code(mensaje["detalle_error"], language="text")

    # Conti ya clasificó: pedimos confirmación antes de guardar
    if st.session_state.pendiente:
        caso = st.session_state.pendiente
        nivel = SEMAFORO.get(caso.get("semaforo"), SEMAFORO["rojo"])

        with st.container(border=True):
            st.subheader("🚦 ¿Confirmas esta clasificación?")
            st.write(f"{nivel['emoji']} **{nivel['nombre']}** · {caso.get('resumen', '')}")
            st.write(f"🏢 **{caso.get('nombre') or 'Sin nombre'}** · 📞 {caso.get('contacto') or 'Sin contacto'}")
            st.write(f"💡 **Por qué:** {caso.get('motivo', '')}")
            st.write("✅ **Acciones sugeridas:**")
            for accion in caso.get("acciones", []):
                st.write(f"- {accion}")

            col_si, col_no = st.columns(2)
            if col_si.button("✅ Confirmar y guardar", use_container_width=True):
                guardar_caso(caso.get("nombre", ""), caso.get("contacto", ""), caso.get("resumen", ""), caso)
                st.session_state.aviso = "¡Caso guardado! 🎉"
                st.session_state.mensajes = chat_nuevo()
                st.session_state.pendiente = None
                st.rerun()

            if col_no.button("🔁 Seguir hablando", use_container_width=True):
                # Sacamos la clasificación del historial y seguimos la charla
                if st.session_state.mensajes and st.session_state.mensajes[-1]["role"] == "assistant":
                    st.session_state.mensajes.pop()
                st.session_state.pendiente = None
                st.rerun()
    else:
        # 🔑 Sin llave no hay magia
        if not api_key:
            st.warning(FALTA_LLAVE)
        else:
            entrada = st.chat_input("Escribe tu mensaje...")
            if entrada:
                st.session_state.mensajes.append({"role": "user", "content": entrada})
                with st.chat_message("user"):
                    st.write(entrada)
                with st.chat_message("assistant"):
                    with st.spinner("Conti está pensando..."):
                        respuesta = conversar(st.session_state.mensajes, api_key, base_url, modelo)
                if respuesta.get("error"):
                    st.session_state.mensajes.append(
                        {
                            "role": "assistant",
                            "content": (
                                "⚠️ **Servicio no disponible temporalmente**\n\n"
                                "En este momento no puedo conectarme con el motor de inteligencia artificial. "
                                "Esto suele ocurrir por un inconveniente con las credenciales de acceso o una intermitencia del proveedor.\n\n"
                                "Por favor, intenta nuevamente en unos minutos o contacta al administrador del sistema."
                            ),
                            "detalle_error": respuesta.get("detalle", ""),
                        }
                    )
                elif respuesta.get("tipo") == "clasificacion":
                    st.session_state.pendiente = respuesta
                    nivel = SEMAFORO.get(respuesta.get("semaforo"), SEMAFORO["rojo"])
                    st.session_state.mensajes.append(
                        {
                            "role": "assistant",
                            "content": f"{nivel['emoji']} ¡Listo! Clasifiqué tu caso como **{nivel['nombre']}**. Revisa el detalle y confírmalo para guardarlo.",
                        }
                    )
                else:
                    st.session_state.mensajes.append({"role": "assistant", "content": respuesta.get("mensaje", "")})
                st.rerun()

    # 🎯 Cada mensaje nuevo lleva la vista y el cursor al campo de texto
    enfocar_campo()

# 📋 Pestaña 2: pegar un correo completo
with tab_texto:
    with st.form("formulario_texto"):
        texto = st.text_area("Pega aquí el correo o mensaje completo", height=200)
        enviar_texto = st.form_submit_button("🚦 Clasificar correo")

with tab_gestion:
    if not st.session_state.casos:
        st.info("Todavía no hay casos. Chatea con Conti o pega un correo para crear el primero.")
    else:
        abiertos = sum(1 for caso in st.session_state.casos if isinstance(caso, dict) and caso.get("estado") == "abierto")
        col_abiertos, col_cerrados, col_total = st.columns(3)
        col_abiertos.metric("📂 Abiertos", abiertos)
        col_cerrados.metric("✅ Cerrados", len(st.session_state.casos) - abiertos)
        col_total.metric("🗂️ Total", len(st.session_state.casos))

        busqueda = st.text_input("🔍 Buscar por nombre, contacto o motivo")
        col_estado, col_color = st.columns(2)
        filtro_estado = col_estado.selectbox("Estado", ["Todos", "Abiertos", "Cerrados"])
        filtro_color = col_color.selectbox("Semáforo", ["Todos", "🔴 Bombero", "🟡 Cotidiano", "🟢 Consulta"])

        color_elegido = {
            "Todos": None,
            "🔴 Bombero": "rojo",
            "🟡 Cotidiano": "amarillo",
            "🟢 Consulta": "verde",
        }[filtro_color]

        encontrados = 0
        for caso in reversed(st.session_state.casos):
            if not isinstance(caso, dict):
                continue
            texto_busqueda = f"{caso.get('nombre', '')} {caso.get('contacto', '')} {caso.get('motivo_contacto', '')}".lower()
            if busqueda.lower() not in texto_busqueda:
                continue
            if filtro_estado == "Abiertos" and caso.get("estado") != "abierto":
                continue
            if filtro_estado == "Cerrados" and caso.get("estado") != "cerrado":
                continue
            if color_elegido and caso.get("semaforo") != color_elegido:
                continue

            encontrados += 1
            nivel = SEMAFORO.get(caso.get("semaforo"), SEMAFORO["rojo"])

            with st.container(border=True):
                col_nombre, col_estado_caso = st.columns([3, 1])
                col_nombre.write(f"{nivel['emoji']} **{nivel['nombre']}** · {caso.get('nombre') or 'Sin nombre'}")
                col_estado_caso.caption(f"**{str(caso.get('estado', 'abierto')).capitalize()}**")
                st.caption(f"📞 {caso.get('contacto') or 'Sin contacto'} · 🕒 {caso.get('fecha', '')}")
                st.write(caso.get("motivo_contacto", ""))
                st.caption(f"💡 {caso.get('explicacion', '')}")

                with st.expander("✅ Acciones sugeridas"):
                    for accion in caso.get("acciones", []):
                        st.write(f"- {accion}")

                col_cerrar, col_notificar = st.columns(2)
                id_caso = caso.get("id", encontrados)
                if caso.get("estado") == "abierto":
                    if col_cerrar.button("✅ Cerrar", key=f"cerrar_{id_caso}"):
                        caso["estado"] = "cerrado"
                        guardar_casos(st.session_state.casos)
                        st.rerun()
                else:
                    if col_cerrar.button("🔓 Reabrir", key=f"reabrir_{id_caso}"):
                        caso["estado"] = "abierto"
                        guardar_casos(st.session_state.casos)
                        st.rerun()

                if caso.get("notificado"):
                    col_notificar.caption("📣 Notificado")
                else:
                    if col_notificar.button("📣 Notificar", key=f"notificar_{id_caso}"):
                        st.session_state.aviso = notificar(caso)
                        caso["notificado"] = True
                        guardar_casos(st.session_state.casos)
                        st.rerun()

        if encontrados == 0:
            st.info("No hay casos que coincidan con la búsqueda 🔍")

# 🔑 Sin llave no hay magia
if enviar_texto and not api_key:
    st.warning(FALTA_LLAVE)
    st.stop()

# 🚦 Clasificamos el correo pegado y lo guardamos como abierto
if enviar_texto:
    with st.spinner("Clasificando el correo..."):
        resultado = clasificar(texto, api_key, base_url, modelo)
    if resultado.get("error"):
        st.error("⚠️ El servicio de IA no está disponible en este momento. Por favor verifica las credenciales o intenta más tarde.")
        with st.expander("🔍 Detalle técnico"):
            st.code(resultado.get("detalle", "Error desconocido"), language="text")
    else:
        guardar_caso(resultado.get("nombre", ""), resultado.get("contacto", ""), texto, resultado)
        st.session_state.aviso = "🚦 Correo clasificado y guardado"
        st.rerun()

# ❤️ Firma del proyecto (el span fuerza la fuente de emojis a color)
st.divider()
st.caption(
    "Realizado por 99% robot <span style=\"font-family:'Segoe UI Emoji','Apple Color Emoji','Noto Color Emoji'\">🤖</span>, "
    "1% humano 🧑 y 100% amor ❤️",
    unsafe_allow_html=True,
)
