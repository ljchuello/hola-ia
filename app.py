# 🎯 Conti Clasificador — una app mínima para mostrar IA clasificando casos

import os

import streamlit as st

from conti import SEMAFORO, clasificar, notificar

st.set_page_config(page_title="Conti Clasificador", page_icon="🎯")

# 📚 El historial vive solo mientras la pestaña esté abierta
if "historial" not in st.session_state:
    st.session_state.historial = []

# ⚙️ Barra lateral: configuración de la IA
with st.sidebar:
    st.header("⚙️ Configuración")
    api_key = st.text_input("🔑 API key", value=os.getenv("LLM_API_KEY", ""), type="password")
    base_url = st.text_input("🌐 Base URL", value=os.getenv("LLM_BASE_URL", "https://api.openai.com/v1"))
    modelo = st.text_input("🧠 Modelo", value=os.getenv("LLM_MODEL", "gpt-4o-mini"))
    st.caption("Funciona con OpenAI, Groq, OpenRouter u Ollama 😉")

st.title("🎯 Conti Clasificador")
st.write("Pega un caso de soporte y Conti le pone semáforo 🚦 para que Producción sepa qué atender primero.")

# 📥 Dos formas de entrada
tab_formulario, tab_texto = st.tabs(["📝 Caso estructurado", "📋 Pegar texto"])

with tab_formulario:
    with st.form("formulario_caso"):
        titulo = st.text_input("Título del caso")
        area = st.text_input("Área o persona que reporta")
        descripcion = st.text_area("¿Qué está pasando?")
        enviar_formulario = st.form_submit_button("🚦 Clasificar caso")

with tab_texto:
    with st.form("formulario_texto"):
        texto = st.text_area("Pega aquí el correo o mensaje completo", height=200)
        enviar_texto = st.form_submit_button("🚦 Clasificar texto")

# 🔑 Sin llave no hay magia
if enviar_formulario or enviar_texto:
    if not api_key:
        st.warning("Pega tu API key en la barra lateral para que Conti pueda pensar 🔑")
        st.stop()

if enviar_formulario:
    caso = f"Título: {titulo}\nReporta: {area}\nDescripción: {descripcion}"
    st.session_state.resultado = clasificar(caso, api_key, base_url, modelo)

if enviar_texto:
    st.session_state.resultado = clasificar(texto, api_key, base_url, modelo)

# 🚦 Tarjeta con el resultado
if "resultado" in st.session_state:
    resultado = st.session_state.resultado
    nivel = SEMAFORO[resultado["semaforo"]]
    mensaje = f"{nivel['emoji']} **{nivel['nombre']}** · {resultado['resumen']}"

    if resultado["semaforo"] == "rojo":
        st.error(mensaje)
    elif resultado["semaforo"] == "amarillo":
        st.warning(mensaje)
    else:
        st.success(mensaje)

    st.write(f"💡 **Motivo:** {resultado['motivo']}")
    st.write(f"⏱️ **SLA:** {nivel['sla']}")
    st.write("✅ **Acciones sugeridas:**")
    for accion in resultado["acciones"]:
        st.write(f"- {accion}")

    if st.button("📣 Notificar a Producción"):
        aviso = notificar(resultado)
        st.toast(aviso)
        st.session_state.historial.append(
            {"emoji": nivel["emoji"], "tipo": nivel["nombre"], "resumen": resultado["resumen"], "aviso": aviso}
        )

# 📚 Historial de la sesión
if st.session_state.historial:
    with st.expander("📚 Historial de esta sesión"):
        for caso in reversed(st.session_state.historial):
            st.write(f"{caso['emoji']} **{caso['tipo']}** · {caso['resumen']}")
            st.caption(caso["aviso"])
