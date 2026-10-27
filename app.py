# 🎯 Conti Clasificador — una app mínima para mostrar IA clasificando casos

import json
import os
from datetime import datetime

import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError

from conti import SEMAFORO, clasificar, notificar

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


if "casos" not in st.session_state:
    st.session_state.casos = cargar_casos()

api_key = leer_secreto("LLM_API_KEY") or os.getenv("LLM_API_KEY", "")
base_url = leer_secreto("LLM_BASE_URL") or os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
modelo = leer_secreto("LLM_MODEL") or os.getenv("LLM_MODEL", "gpt-4o-mini")

st.title("🎯 Conti Clasificador")
st.write("Pega un caso de soporte y Conti le pone semáforo 🚦 para que Producción sepa qué atender primero.")

# ✅ Aviso de la última notificación
if "aviso" in st.session_state:
    st.success(st.session_state.pop("aviso"))

# 📥 Tres pestañas: crear, pegar y gestionar
tab_nuevo, tab_texto, tab_gestion = st.tabs(["📝 Nuevo caso", "📋 Pegar texto", "🗂️ Gestión"])

with tab_nuevo:
    with st.form("formulario_caso"):
        nombre = st.text_input("🏢 Empresa o persona")
        contacto = st.text_input("📞 Teléfono o correo")
        motivo_contacto = st.text_area("📝 Motivo del contacto")
        enviar_formulario = st.form_submit_button("🚦 Clasificar caso")

with tab_texto:
    with st.form("formulario_texto"):
        texto = st.text_area("Pega aquí el correo o mensaje completo", height=200)
        enviar_texto = st.form_submit_button("🚦 Clasificar texto")

with tab_gestion:
    if not st.session_state.casos:
        st.info("Todavía no hay casos. Clasifica uno en la pestaña 📝 Nuevo caso.")
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
if enviar_formulario or enviar_texto:
    if not api_key:
        st.warning("Falta configurar LLM_API_KEY en .streamlit/secrets.toml 🔑")
        st.stop()

# 🚦 Clasificamos y guardamos el caso como abierto
if enviar_formulario:
    caso_texto = f"Empresa o persona: {nombre}\nContacto: {contacto}\nMotivo: {motivo_contacto}"
    resultado = clasificar(caso_texto, api_key, base_url, modelo)
    resultado["nombre"] = nombre or resultado.get("nombre", "")
    resultado["contacto"] = contacto or resultado.get("contacto", "")
    resultado["motivo_contacto"] = motivo_contacto

    st.session_state.ultimo = {
        "id": max((caso["id"] for caso in st.session_state.casos), default=0) + 1,
        "nombre": resultado["nombre"],
        "contacto": resultado["contacto"],
        "motivo_contacto": resultado["motivo_contacto"],
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

if enviar_texto:
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

# ❤️ Firma del proyecto
st.divider()
st.caption("Realizado por 99% robot 🤖, 1% humano 🧑 y 100% amor ❤️")
