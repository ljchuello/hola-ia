# 🎯 Conti Clasificador

Una muestra mínima de cómo usar un LLM para clasificar casos de soporte y avisar al equipo de Producción con un semáforo.

> ⚠️ Proyecto demostrativo. No es para producción: no guarda datos, no valida errores y no envía notificaciones reales.

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

## 🔑 Configuración

En la barra lateral ⚙️ pega tu API key y ajusta el modelo. También puedes usar variables de entorno:

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

## 🧠 Cómo funciona

1. Escribes un caso en el formulario o pegas un correo completo.
2. `conti.py` le manda el caso al modelo con un prompt que define el semáforo.
3. El modelo responde un JSON con color, resumen, motivo y acciones.
4. La app pinta la tarjeta y, si quieres, "notifica" a Producción.

## 📁 Archivos

- `app.py` — interfaz de Streamlit.
- `conti.py` — prompt, llamada al modelo y mensaje de notificación.
- `AGENTS.md` — reglas del proyecto (incluida la prohibición de sobreingeniería).
- `requirements.txt` — dependencias.
