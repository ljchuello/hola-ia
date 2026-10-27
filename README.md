# 🎯 Conti Clasificador

Una muestra mínima de cómo usar un LLM para clasificar casos de soporte y avisar al equipo de Producción con un semáforo.

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

## 🗂️ Gestión de casos

La pestaña **Gestión** permite:

- 🔍 Buscar por nombre de la empresa o persona, teléfono, correo o motivo.
- 🎚️ Filtrar por estado: abiertos, cerrados o todos.
- 🚦 Filtrar por semáforo.
- ✅ Cerrar un caso abierto o 🔓 reabrirlo.
- 📣 Notificar a Producción.

Los casos se guardan en `casos.json`, así que sobreviven a una recarga del navegador. Ese archivo es local y está ignorado por git.

## 🧠 Cómo funciona

1. Escribes un caso en el formulario o pegas un correo completo.
2. `conti.py` le manda el caso al modelo con un prompt que define el semáforo.
3. El modelo responde un JSON con color, nombre, contacto, resumen, motivo y acciones.
4. La app guarda el caso como **abierto** y pinta la tarjeta.
5. En **Gestión** puedes buscarlo, cerrarlo, reabrirlo o notificarlo.

## 📁 Archivos

- `app.py` — interfaz de Streamlit.
- `conti.py` — prompt, llamada al modelo y mensaje de notificación.
- `casos.json` — casos guardados localmente (ignorado por git).
- `.streamlit/secrets.example.toml` — plantilla de secretos.
- `.streamlit/secrets.toml` — tu clave real (ignorado por git).
- `AGENTS.md` — reglas del proyecto (incluida la prohibición de sobreingeniería).
- `requirements.txt` — dependencias.
