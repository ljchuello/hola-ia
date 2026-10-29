# 🎯 Conti Clasificador

Una muestra mínima de cómo usar un LLM para clasificar casos de soporte **conversando con un chatbot** y avisar al equipo de Producción con un semáforo.

> ⚠️ Proyecto demostrativo. No es para producción: guarda los casos en un JSON local, no valida errores y no envía notificaciones reales.

## 🚦 El semáforo

| Color | Nombre | Qué significa | SLA |
| --- | --- | --- | --- |
| 🔴 | Bombero | Algo está caído, bloqueado o se pierde información | 15 minutos |
| 🟡 | Cotidiano | Solicitud normal de operación | Mismo día |
| 🟢 | Consulta | Duda o petición de información | 24-48 horas |

**Regla de oro:** ante la duda entre 🔴 y 🟡, siempre 🔴.

## ▶️ Cómo correrlo

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 🔐 Secretos (recomendado)

Para que quien use la app no tenga que pegar ninguna clave:

1. Copia la plantilla:
   ```bash
   cp .streamlit/secrets.example.toml .streamlit/secrets.toml
   ```
2. Abre `.streamlit/secrets.toml` y pon tu clave real:
   ```toml
   LLM_API_KEY = "sk-..."
   ```
3. Reinicia Streamlit.

Con la clave configurada, la app la usa directamente: no hay campos de configuración en la barra lateral. El archivo `secrets.toml` está ignorado por git y nunca se sube.

En Streamlit Cloud, pega los mismos valores en **App settings → Secrets**.

## 🔑 Configuración

El orden de prioridad es: `secrets.toml` → variable de entorno. Si no hay clave, la app avisa al intentar clasificar:

| Variable | Por defecto |
| --- | --- |
| `LLM_API_KEY` | vacío |
| `LLM_BASE_URL` | `https://api.openai.com/v1` |
| `LLM_MODEL` | `gpt-4o-mini` |

Funciona con cualquier API compatible con OpenAI 🤝:

- OpenAI: `https://api.openai.com/v1`
- Groq: `https://api.groq.com/openai/v1`
- OpenRouter: `https://openrouter.ai/api/v1`
- Ollama: `http://localhost:11434/v1` (la API key puede ser cualquier texto)

## 💬 Chat agéntico

La pestaña **Chat agéntico** reemplaza al formulario de "Nuevo caso":

1. Conti saluda y te va preguntando de a una cosa: quién sos, cómo contactarte y qué pasó.
2. Le respondés con lenguaje natural, como en un chat normal. Nada de formatos.
3. Cuando Conti cree que ya tiene lo necesario, clasifica el caso con el semáforo.
4. Antes de guardar, te muestra el resumen y pedís confirmación. Si no quedó bien, seguís hablando.
5. Al confirmar, el caso se guarda como abierto y queda en Gestión.

También podés pegar un correo completo en la pestaña **📋 Pegar correo** y Conti lo clasifica al toque.

## 🗂️ Gestión de casos

La pestaña **Gestión** permite:

- 🔍 Buscar por nombre de la empresa o persona, teléfono, correo o motivo.
- 🎚️ Filtrar por estado: abiertos, cerrados o todos.
- 🚦 Filtrar por semáforo.
- ✅ Cerrar un caso abierto o 🔓 reabrirlo.
- 📣 Notificar a Producción.

Los casos se guardan en `casos.json`, así que sobreviven a una recarga del navegador. Ese archivo es local y está ignorado por git.

## 🧠 Cómo funciona

1. Hablás con Conti en el chat (o pegás un correo completo).
2. `conti.py` le manda el historial al modelo con un prompt que define el semáforo.
3. En cada turno el modelo responde un JSON: o hace una pregunta, o entrega la clasificación.
4. Cuando clasifica, la app te muestra el resumen para confirmar antes de guardar.
5. El caso se guarda como **abierto**, aparece un aviso y queda en **Gestión**.
6. En **Gestión** puedes buscarlo, cerrarlo, reabrirlo o notificarlo.

## 📁 Archivos

- `app.py` — interfaz de Streamlit.
- `conti.py` — prompts, llamada al modelo y mensaje de notificación.
- `casos.json` — casos guardados localmente (ignorado por git).
- `.streamlit/secrets.example.toml` — plantilla de secretos.
- `.streamlit/secrets.toml` — tu clave real (ignorado por git).
- `AGENTS.md` — reglas del proyecto (incluida la prohibición de sobreingeniería).
- `requirements.txt` — dependencias.
