# 🎯 Conti Clasificador — el corazón del ejemplo
# Todo lo que la app necesita para hablar con la IA vive aquí.

import json

from openai import OpenAI

# 🚦 Los tres niveles del semáforo y su tiempo de respuesta
SEMAFORO = {
    "rojo": {"emoji": "🔴", "nombre": "Bombero", "sla": "15 minutos"},
    "amarillo": {"emoji": "🟡", "nombre": "Cotidiano", "sla": "mismo día"},
    "verde": {"emoji": "🟢", "nombre": "Consulta", "sla": "24-48 horas"},
}

# 🧠 Aquí le explicamos a la IA cómo queremos que clasifique
SYSTEM_PROMPT = """
Eres Conti, el clasificador de casos de soporte del equipo de Producción.

Clasifica cada caso en uno de estos tres niveles:

🔴 rojo — Bombero: algo está caído, bloqueado o se está perdiendo información.
🟡 amarillo — Cotidiano: una solicitud normal que puede esperar al mismo día.
🟢 verde — Consulta: una duda, una pregunta o una petición de información.

Regla de oro: si dudas entre rojo y amarillo, elige rojo.

Ejemplos:
- "No puedo facturar, el sistema da error" → rojo
- "Necesito agregar un usuario nuevo" → amarillo
- "¿Cómo descargo el reporte mensual?" → verde

Si el texto menciona una empresa o persona, un teléfono o un correo, cópialos en "nombre" y "contacto". Si no aparecen, déjalos vacíos.

Responde SOLO con este JSON, sin markdown:
{
  "semaforo": "rojo | amarillo | verde",
  "nombre": "empresa o persona mencionada, o vacío",
  "contacto": "teléfono o correo mencionado, o vacío",
  "resumen": "una frase corta del caso",
  "motivo": "por qué elegiste ese color",
  "acciones": ["paso 1", "paso 2"]
}
"""


def clasificar(caso: str, api_key: str, base_url: str, modelo: str) -> dict:
    """Le manda el caso a la IA y devuelve el JSON convertido a diccionario."""
    cliente = OpenAI(api_key=api_key, base_url=base_url)
    respuesta = cliente.chat.completions.create(
        model=modelo,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": caso},
        ],
    )
    return json.loads(respuesta.choices[0].message.content)


def notificar(clasificacion: dict) -> str:
    """Arma el mensaje que se 'envía' al equipo de Producción."""
    nivel = SEMAFORO[clasificacion["semaforo"]]
    return f"{nivel['emoji']} Caso {nivel['nombre']} notificado a Producción · SLA: {nivel['sla']}"
