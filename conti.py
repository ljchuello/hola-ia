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
Escribe en español neutro, sin voseo ni regionalismos.

Clasifica cada caso en uno de estos tres niveles:

🔴 rojo — Bombero: un proceso crítico está detenido y hay un cliente esperando.
No puede guardar una factura o una nota de crédito, no puede cerrar una venta,
el sistema no responde o se está perdiendo información. El trabajo se detuvo.

🟡 amarillo — Cotidiano: el sistema funciona, pero algo lo traba y hay que
resolverlo hoy. La impresora no imprime, el sistema va lento, una pantalla da
error, pero se puede seguir trabajando por otro lado. Nada crítico se detiene.

🟢 verde — Consulta: no hay nada roto de tu lado. Es una duda, una solicitud
de información o un tema con un tercero (proveedor, banco, internet) que no
frena la operación.

La frontera entre rojo y amarillo es simple: si el trabajo se detiene, es rojo;
si solo se hace más lento, es amarillo. Si el problema es de un tercero y no
frena la operación, es verde.

Regla de oro: si dudas entre rojo y amarillo, elige rojo.

Ejemplos:
- "No puedo guardar la factura, el sistema da error y el cliente está esperando" → rojo
- "Soy Ana de Ferretería López, ana@lopez.com, no puedo guardar la nota de crédito y el cliente está en el mostrador" → rojo
- "La impresora no imprime, pero puedo seguir cargando pedidos" → amarillo
- "El sistema está lento, pero sigue funcionando" → amarillo
- "Necesito agregar un usuario nuevo" → amarillo
- "¿Cómo descargo el reporte mensual?" → verde
- "¿Me confirman si el convenio con el banco sigue activo?" → verde

Identifica siempre al usuario: nombre (empresa o persona) y un contacto (teléfono o
correo; con uno alcanza). Si no aparecen, déjalos vacíos.

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

# 🗣️ El prompt del chat: Conti pregunta y decide cuándo ya puede clasificar
CHAT_PROMPT = """
Eres Conti, el asistente de soporte del equipo de Producción.
Escribe en español neutro, sin voseo ni regionalismos.

Tu trabajo es conversar con la persona para entender su caso y, cuando tengas
lo necesario, clasificarlo con el semáforo. Habla natural, como un humano:
saluda, haz UNA pregunta a la vez y espera la respuesta.

Pregunta lo que falte, pero sin molestar: con saber quién es (empresa o
persona), cómo contactarlo (teléfono o correo) y qué pasó (motivo) ya puedes
clasificar. No pidas nada más ni repitas preguntas ya respondidas.

Siempre responde SOLO con JSON, sin markdown, en uno de estos dos formatos:

1. Si te falta información, sigues preguntando:
{"tipo": "pregunta", "mensaje": "tu pregunta aquí"}

2. Si ya puedes clasificar, entregas el caso:
{"tipo": "clasificacion", "semaforo": "rojo | amarillo | verde", "nombre": "empresa o persona, o vacío", "contacto": "teléfono o correo, o vacío", "resumen": "una frase corta del caso", "motivo": "por qué elegiste ese color", "acciones": ["paso 1", "paso 2"]}

El semáforo:
🔴 rojo — Bombero: un proceso crítico está detenido y el cliente está esperando
   (no puede guardar una factura o nota de crédito, no puede cerrar una venta,
   el sistema no responde o se pierde información).
🟡 amarillo — Cotidiano: el sistema funciona pero algo lo traba; la impresora no
   imprime, va lento o una pantalla da error, y se puede seguir trabajando.
🟢 verde — Consulta: una duda, una solicitud de información o un tema con un
   tercero que no frena la operación.

Frontera: si el trabajo se detiene es rojo; si solo se hace más lento es amarillo;
si es de un tercero y no frena la operación es verde.

Regla de oro: si dudas entre rojo y amarillo, elige rojo.
"""


def clasificar(caso: str, api_key: str, base_url: str, modelo: str) -> dict:
    """Clasifica un caso de soporte con la IA y devuelve el semáforo ya interpretado.

    Le entrega el texto al modelo junto con el prompt del semáforo y convierte la
    respuesta en un diccionario listo para usar en la app.

    Argumentos:
        caso: El texto del caso tal como lo cuenta la persona.
        api_key: La clave con la que se autentica el proveedor.
        base_url: La dirección del proveedor compatible con OpenAI.
        modelo: El modelo que hace la clasificación.

    Devuelve:
        El caso clasificado como diccionario, o un diccionario vacío si la IA
        responde algo que no se puede leer.
    """
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
    try:
        return json.loads(respuesta.choices[0].message.content)
    except Exception:
        return {}


def conversar(mensajes: list, api_key: str, base_url: str, modelo: str) -> dict:
    """Continúa la conversación con Conti y devuelve su próxima respuesta.

    Le pasa al modelo el historial completo para que decida si necesita preguntar
    algo más o si ya puede clasificar el caso.

    Argumentos:
        mensajes: El historial de la charla, con el rol y el contenido de cada turno.
        api_key: La clave con la que se autentica el proveedor.
        base_url: La dirección del proveedor compatible con OpenAI.
        modelo: El modelo que responde la conversación.

    Devuelve:
        La respuesta de Conti como diccionario, o un diccionario vacío si el modelo
        devuelve algo que no se puede leer.
    """
    cliente = OpenAI(api_key=api_key, base_url=base_url)
    respuesta = cliente.chat.completions.create(
        model=modelo,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": CHAT_PROMPT},
            *mensajes,
        ],
    )
    try:
        return json.loads(respuesta.choices[0].message.content)
    except Exception:
        return {}


def notificar(clasificacion: dict) -> str:
    """Arma el aviso que se muestra al equipo de Producción.

    Toma el nivel del semáforo del caso y lo convierte en un mensaje con el emoji,
    el nombre del nivel y su tiempo de respuesta.

    Argumentos:
        clasificacion: El caso clasificado, del que se lee el campo semaforo.

    Devuelve:
        El mensaje de notificación listo para mostrar, o uno genérico si el nivel
        no se reconoce.
    """
    nivel = SEMAFORO.get(clasificacion.get("semaforo"))
    if not nivel:
        return "📣 Caso notificado a Producción · SLA: a definir"
    return f"{nivel['emoji']} Caso {nivel['nombre']} notificado a Producción · SLA: {nivel['sla']}"
