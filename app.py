# 🎯 Conti Clasificador — una app mínima para mostrar IA clasificando casos

import json
import os
from datetime import datetime

import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError

from conti import SEMAFORO, clasificar, conversar, notificar

RUTA_CASOS = "casos.json"

st.set_page_config(page_title="Conti Clasificador", page_icon="🎯")


# 💾 Guardamos los casos en un JSON para que sobrevivan a la recarga
def cargar_casos():
    if not os.path.exists(RUTA_CASOS):
        return []
    with open(RUTA_CASOS, encoding="utf-8") as archivo:
        return json.load(archivo)


def guardar_casos(casos):
    with open(RUTA_CASOS, "w", encoding="utf-8") as archivo:
        json.dump(casos, archivo, ensure_ascii=False, indent=2)


# 🔐 Leemos la clave desde secrets.toml o desde una variable de entorno
def leer_secreto(clave, defecto=""):
    try:
        return st.secrets.get(clave, defecto)
    except StreamlitSecretNotFoundError:
        return defecto


# 💬 Cada conversación con Conti arranca con un saludo y una primera pregunta
def chat_nuevo():
    return [
        {
            "role": "assistant",
            "content": "¡Hola! Soy Conti 🎯 Contame qué pasó y yo lo clasifico. ¿Quién sos o de qué empresa escribís?",
        }
    ]


if "casos" not in st.session_state:
    st.session_state.casos = cargar_casos()

if "mensajes" not in st.session_state:
    st.session_state.mensajes = chat_nuevo()

if "pendiente" not in st.session_state:
    st.session_state.pendiente = None

api_key = leer_secreto("LLM_API_KEY") or os.getenv("LLM_API_KEY", "")
base_url = leer_secreto("LLM_BASE_URL") or os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
modelo = leer_secreto("LLM_MODEL") or os.getenv("LLM_MODEL", "gpt-4o-mini")

# 🌗 Los colores de cada tema, en un solo lugar
TEMAS = {
    "oscuro": {"fondo": "#0e1117", "panel": "#262730", "texto": "#fafafa", "suave": "#a3a8b8", "borde": "#3a3d4a"},
    "claro": {"fondo": "#ffffff", "panel": "#f0f2f6", "texto": "#31333f", "suave": "#6b7280", "borde": "#d5d8e0"},
}


# 🎨 Repintamos la app con los colores del tema elegido
def pintar_tema(nombre):
    c = TEMAS[nombre]
    st.html(
        f"""<style>
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{ background: {c['fondo']} !important; }}
        [data-testid="stMarkdownContainer"] :is(p, h1, h2, h3, h4, h5, h6, li, span, strong, em) {{ color: {c['texto']} !important; }}
        [data-testid="stCaptionContainer"] :is(p, span, small) {{ color: {c['suave']} !important; }}
        [data-testid="stWidgetLabel"] :is(label, p), [data-testid="stMetricLabel"], [data-testid="stMetricValue"],
        [data-testid="stToolbar"] button {{ color: {c['texto']} !important; }}
        [data-testid="stTabs"] button {{ color: {c['suave']} !important; }}
        [data-testid="stTabs"] button[aria-selected="true"] {{ color: {c['texto']} !important; }}
        [data-testid="stChatInput"], [data-testid="stChatInput"] div {{ background: transparent !important; }}
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
        [data-testid="stVerticalBlockBorderWrapper"] {{ background: {c['panel']} !important; border-color: {c['borde']} !important; }}
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
    "Sin formularios eternos ni planillas a mano: contás tu caso en tus palabras y Conti devuelve "
    "un resumen, el motivo de la clasificación y los próximos pasos, listo para confirmar y guardar."
)

col_conversa, col_clasifica, col_gestion = st.columns(3)
with col_conversa:
    st.markdown("#### 💬 Conversá")
    st.caption("Describí tu caso en lenguaje natural. Conti pregunta lo justo, una cosa a la vez, y nada más.")
with col_clasifica:
    st.markdown("#### 🚦 Clasificá")
    st.caption("Semáforo de urgencia con SLA: 🔴 15 minutos · 🟡 mismo día · 🟢 24-48 horas.")
with col_gestion:
    st.markdown("#### 🗂️ Gestioná")
    st.caption("Buscá, filtrá, cerrá y notificá casos desde un solo lugar, sin salir de la app.")

st.caption("🎓 Demo didáctica · ⚙️ Funciona con cualquier API compatible con OpenAI · 🔐 La clave vive en secrets.toml")

# 🧠 El detalle técnico queda a un clic, sin ocupar lugar
with st.expander("🧠 ¿Cómo funciona?"):
    st.write("**1. 💬 Hablás con Conti.** Describís tu caso como se lo contarías a un compañero. También podés pegar un correo entero.")
    st.write("**2. 🧠 Conti lo interpreta.** El modelo recibe tu mensaje con un prompt que define el semáforo y devuelve un JSON con el nivel, un resumen, el motivo y las acciones sugeridas.")
    st.write("**3. ✅ Confirmás y se guarda.** Revisás la clasificación, la corregís si hace falta y el caso queda abierto en **Gestión**, listo para cerrar o notificar a Producción.")
    st.caption("🎓 Todo el contenido vive en `conti.py`: un prompt, dos funciones y cero magia.")

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

    # Conti ya clasificó: pedimos confirmación antes de guardar
    if st.session_state.pendiente:
        caso = st.session_state.pendiente
        nivel = SEMAFORO[caso["semaforo"]]

        with st.container(border=True):
            st.subheader("🚦 ¿Confirmás esta clasificación?")
            st.write(f"{nivel['emoji']} **{nivel['nombre']}** · {caso['resumen']}")
            st.write(f"🏢 **{caso['nombre'] or 'Sin nombre'}** · 📞 {caso['contacto'] or 'Sin contacto'}")
            st.write(f"💡 **Por qué:** {caso['motivo']}")
            st.write("✅ **Acciones sugeridas:**")
            for accion in caso["acciones"]:
                st.write(f"- {accion}")

            col_si, col_no = st.columns(2)
            if col_si.button("✅ Confirmar y guardar", use_container_width=True):
                st.session_state.ultimo = {
                    "id": max((c["id"] for c in st.session_state.casos), default=0) + 1,
                    "nombre": caso.get("nombre", ""),
                    "contacto": caso.get("contacto", ""),
                    "motivo_contacto": caso.get("resumen", ""),
                    "semaforo": caso["semaforo"],
                    "resumen": caso.get("resumen", ""),
                    "explicacion": caso.get("motivo", ""),
                    "acciones": caso.get("acciones", []),
                    "estado": "abierto",
                    "notificado": False,
                    "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
                }
                st.session_state.casos.append(st.session_state.ultimo)
                guardar_casos(st.session_state.casos)
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
            st.warning("Falta configurar LLM_API_KEY en .streamlit/secrets.toml 🔑")
        else:
            entrada = st.chat_input("Escribí tu mensaje...")
            if entrada:
                st.session_state.mensajes.append({"role": "user", "content": entrada})
                with st.chat_message("user"):
                    st.write(entrada)
                with st.chat_message("assistant"):
                    with st.spinner("Conti está pensando..."):
                        respuesta = conversar(st.session_state.mensajes, api_key, base_url, modelo)
                if respuesta.get("tipo") == "clasificacion":
                    st.session_state.pendiente = respuesta
                    nivel = SEMAFORO[respuesta["semaforo"]]
                    st.session_state.mensajes.append(
                        {
                            "role": "assistant",
                            "content": f"{nivel['emoji']} ¡Listo! Clasifiqué tu caso como **{nivel['nombre']}**. Revisá el detalle y confirmalo para guardarlo.",
                        }
                    )
                else:
                    st.session_state.mensajes.append({"role": "assistant", "content": respuesta.get("mensaje", "")})
                st.rerun()

# 📋 Pestaña 2: pegar un correo completo
with tab_texto:
    with st.form("formulario_texto"):
        texto = st.text_area("Pega aquí el correo o mensaje completo", height=200)
        enviar_texto = st.form_submit_button("🚦 Clasificar correo")

with tab_gestion:
    if not st.session_state.casos:
        st.info("Todavía no hay casos. Chateá con Conti o pegá un correo para crear el primero.")
    else:
        abiertos = sum(1 for caso in st.session_state.casos if caso["estado"] == "abierto")
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
            texto_busqueda = f"{caso['nombre']} {caso['contacto']} {caso['motivo_contacto']}".lower()
            if busqueda.lower() not in texto_busqueda:
                continue
            if filtro_estado == "Abiertos" and caso["estado"] != "abierto":
                continue
            if filtro_estado == "Cerrados" and caso["estado"] != "cerrado":
                continue
            if color_elegido and caso["semaforo"] != color_elegido:
                continue

            encontrados += 1
            nivel = SEMAFORO[caso["semaforo"]]

            with st.container(border=True):
                col_nombre, col_estado_caso = st.columns([3, 1])
                col_nombre.write(f"{nivel['emoji']} **{nivel['nombre']}** · {caso['nombre'] or 'Sin nombre'}")
                col_estado_caso.caption(f"**{caso['estado'].capitalize()}**")
                st.caption(f"📞 {caso['contacto'] or 'Sin contacto'} · 🕒 {caso['fecha']}")
                st.write(caso["motivo_contacto"])
                st.caption(f"💡 {caso['explicacion']}")

                with st.expander("✅ Acciones sugeridas"):
                    for accion in caso["acciones"]:
                        st.write(f"- {accion}")

                col_cerrar, col_notificar = st.columns(2)
                if caso["estado"] == "abierto":
                    if col_cerrar.button("✅ Cerrar", key=f"cerrar_{caso['id']}"):
                        caso["estado"] = "cerrado"
                        guardar_casos(st.session_state.casos)
                        st.rerun()
                else:
                    if col_cerrar.button("🔓 Reabrir", key=f"reabrir_{caso['id']}"):
                        caso["estado"] = "abierto"
                        guardar_casos(st.session_state.casos)
                        st.rerun()

                if caso["notificado"]:
                    col_notificar.caption("📣 Notificado")
                else:
                    if col_notificar.button("📣 Notificar", key=f"notificar_{caso['id']}"):
                        st.session_state.aviso = notificar(caso)
                        caso["notificado"] = True
                        guardar_casos(st.session_state.casos)
                        st.rerun()

        if encontrados == 0:
            st.info("No hay casos que coincidan con la búsqueda 🔍")

# 🔑 Sin llave no hay magia
if enviar_texto and not api_key:
    st.warning("Falta configurar LLM_API_KEY en .streamlit/secrets.toml 🔑")
    st.stop()

# 🚦 Clasificamos el correo pegado y lo guardamos como abierto
if enviar_texto:
    with st.spinner("Clasificando el correo..."):
        resultado = clasificar(texto, api_key, base_url, modelo)
    st.session_state.ultimo = {
        "id": max((caso["id"] for caso in st.session_state.casos), default=0) + 1,
        "nombre": resultado.get("nombre", ""),
        "contacto": resultado.get("contacto", ""),
        "motivo_contacto": texto,
        "semaforo": resultado["semaforo"],
        "resumen": resultado["resumen"],
        "explicacion": resultado["motivo"],
        "acciones": resultado["acciones"],
        "estado": "abierto",
        "notificado": False,
        "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
    }
    st.session_state.casos.append(st.session_state.ultimo)
    guardar_casos(st.session_state.casos)
    st.rerun()

# 🚦 Tarjeta con el último caso clasificado
if "ultimo" in st.session_state:
    caso = st.session_state.ultimo
    nivel = SEMAFORO[caso["semaforo"]]
    mensaje = f"{nivel['emoji']} **{nivel['nombre']}** · {caso['resumen']}"

    st.subheader("🚦 Último caso clasificado")
    if caso["semaforo"] == "rojo":
        st.error(mensaje)
    elif caso["semaforo"] == "amarillo":
        st.warning(mensaje)
    else:
        st.success(mensaje)

    st.write(f"🏢 **{caso['nombre'] or 'Sin nombre'}** · 📞 {caso['contacto'] or 'Sin contacto'}")
    st.write(f"💡 **Por qué:** {caso['explicacion']}")
    st.write(f"⏱️ **SLA:** {nivel['sla']}")
    st.write("✅ **Acciones sugeridas:**")
    for accion in caso["acciones"]:
        st.write(f"- {accion}")

    if caso["notificado"]:
        st.caption("📣 Ya notificado a Producción")
    else:
        if st.button("📣 Notificar a Producción"):
            st.session_state.aviso = notificar(caso)
            caso["notificado"] = True
            guardar_casos(st.session_state.casos)
            st.rerun()

# ❤️ Firma del proyecto (el span fuerza la fuente de emojis a color)
st.divider()
st.caption(
    "Realizado por 99% robot <span style=\"font-family:'Segoe UI Emoji','Apple Color Emoji','Noto Color Emoji'\">🤖</span>, "
    "1% humano 🧑 y 100% amor ❤️",
    unsafe_allow_html=True,
)
