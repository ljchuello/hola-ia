# Conti Clasificador

## 1. Problema y usuario

- **Quién tiene el problema:** El personal de soporte técnico de primera línea en **Sermatick Cia Ltda**, empresa de desarrollo de software que comercializa un sistema de facturación electrónica como servicio.
- **Cómo lo resuelve hoy:** Leyendo correos y mensajes de clientes de manera manual y desordenada, clasificando según la intuición de cada operador y escalando incidentes directamente a Producción sin un criterio de urgencia unificado.
- **Qué le molesta de cómo lo hace hoy:** Se pierde tiempo valioso extrayendo los datos esenciales del contacto; se satura al equipo de desarrollo con dudas operativas cotidianas; y los casos críticos donde hay clientes esperando en caja sufren demoras innecesarias.
- **Qué parte resuelve la IA:** Captura interactivamente o extrae los datos clave del caso (nombre, contacto y motivo), clasifica el nivel de prioridad según el semáforo operativo (🔴 Bombero, 🟡 Cotidiano, 🟢 Consulta) y estima el tiempo máximo de atención (SLA).
- **Qué parte se queda fuera:** La resolución del fallo técnico en el código de facturación, la respuesta final redactada al cliente y la integración directa con bases de datos transaccionales de producción.

## 2. Qué hace el producto

1. **Captura conversacional y extracción rápida:** Conversación guiada mediante chat (haciendo una pregunta a la vez) o lectura de correos copiados para identificar quién reporta, sus datos de contacto y el motivo del incidente.
2. **Clasificación automática con semáforo y SLA:** Evaluación objetiva del caso asignando prioridad (🔴 Bombero: 15 minutos, 🟡 Cotidiano: mismo día, 🟢 Consulta: 24-48 horas), aplicando la regla de oro: ante la duda entre 🔴 y 🟡, siempre 🔴.
3. **Gestión y aviso a Producción:** Panel de casos con búsqueda por texto, filtros por estado (abierto/cerrado) o semáforo, actualización de estado y generación del mensaje de notificación formateado para el equipo técnico.

## 3. Entradas y salidas

| El usuario da… | La app devuelve… | Ejemplo |
|---|---|---|
| Mensajes en lenguaje natural respondiendo a las preguntas de Conti en el chat | Pregunta de seguimiento para completar datos faltantes o tarjeta de clasificación final para confirmar | Usuario: *"Soy Carlos de Farmacia Central (0991234567). No puedo emitir facturas y tengo clientes en mostrador"* → Conti clasifica directamente como 🔴 Bombero (SLA 15 min), resume el caso y sugiere revisar la cola de comprobantes. |
| Un correo completo pegado en un área de texto | Resumen estructurado con semáforo, motivo de la elección, datos de contacto identificados y sugerencias de acción | Correo: *"Estimados, ¿podrían confirmarme si el reporte contable de retenciones incluye las del mes anterior? Saludos, Laura."* → Clasificación 🟢 Consulta (SLA 24-48 h), motivo: duda informativa que no detiene la operación. |
| Clic en notificar caso en la pestaña de Gestión | Texto listo para copiar o enviar al equipo de Producción con los detalles clave del incidente | Mensaje: *"🔴 [Bombero] Farmacia Central · No puede emitir facturas con clientes en caja · Contacto: 0991234567 · SLA: 15 minutos"* |

## 4. La pieza de IA

- **Opción elegida:** API de un LLM compatible con el SDK de OpenAI (por defecto, modelo `deepseek/deepseek-v4.1-flash-1017` servido mediante OpenRouter, adaptable a OpenAI, Groq u Ollama).
- **Por qué:** Permite cambiar de proveedor o modelo modificando únicamente la clave y la URL base en los secretos sin tocar el código. Además, garantiza respuestas rápidas, de bajo coste y estructuradas estrictamente en formato JSON.
- **Instrucciones para el modelo (system prompt):**

El sistema utiliza dos instrucciones especializadas según el modo de entrada:

**A. Clasificación directa (correos pegados):**
```text
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
```

**B. Chat interactivo (agéntico):**
```text
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

[Reglas de semáforo idénticas a la opción A]
```

## 5. Flujo del usuario

1. **El usuario entra y ve:** La interfaz de Streamlit con un saludo inicial de Conti en la pestaña principal de chat y pestañas alternativas para pegar correos o consultar la gestión de casos guardados.
2. **Escribe o sube:** Describe la incidencia en lenguaje natural conversando con Conti (respondiendo a sus preguntas una a una) o pega el texto completo de un correo en la pestaña correspondiente.
3. **Recibe:** Una ficha de clasificación con el color del semáforo, el SLA estimado, los datos de contacto identificados, el resumen y el motivo de la decisión.
4. **Confirma y guarda:** El usuario revisa los datos y pulsa el botón para guardar el caso como abierto.
5. **Gestiona:** En la pestaña de Gestión puede localizar el ticket, filtrar por estado o urgencia, marcarlo como cerrado o generar la notificación para Producción.

## 6. Restricciones

- **Coste cero:** Se emplea la capa gratuita de proveedores compatibles con OpenAI (OpenRouter, Groq) y despliegue gratuito en la nube.
- **Gestión de secretos:** La clave de API se almacena exclusivamente en `.streamlit/secrets.toml` o variables de entorno; nunca se expone en el código ni se incluye en el control de versiones.
- **Sin datos personales reales:** Todos los ejemplos de prueba utilizan datos ficticios para proteger la privacidad.
- **Lenguaje y tono:** Español, redactado de forma clara para personal no técnico.
- **Prohibida la sobreingeniería:** Sin bases de datos complejas, sin autenticación ni arquitecturas multicapa. Los datos se almacenan de manera sencilla y transparente en un archivo `casos.json` local.

## 7. Criterios de aceptación

| Entrada | Resultado esperado |
|---|---|
| *"No puedo timbrar una factura de venta y el comprador está en caja"* (Caso normal 🔴) | Clasifica como 🔴 Bombero, SLA de 15 minutos, identifica la urgencia y resume el bloqueo operativo. |
| *"La pantalla de reportes tarda en cargar, pero podemos emitir documentos"* (Caso normal 🟡) | Clasifica como 🟡 Cotidiano, SLA para el mismo día, motivo: el sistema opera con lentitud pero no está detenido. |
| *"¿Cómo cambio el logotipo de mi empresa en las facturas?"* (Caso normal 🟢) | Clasifica como 🟢 Consulta, SLA de 24-48 horas, motivo: solicitud de información sin afectación operativa. |
| Caso con duda entre detención total y lentitud parcial | Aplica la regla de oro clasificando preventivamente como 🔴 Bombero para no minimizar posibles incidentes graves. |
| Campo de texto vacío o mensaje sin información suficiente | En el chat, Conti solicita cordialmente los datos faltantes; en la pestaña de correo, muestra una advertencia pidiendo ingresar texto antes de procesar. |
| Clave de API no configurada o cuota agotada | La app muestra un mensaje claro y amigable indicando configurar la clave en `.streamlit/secrets.toml` sin interrumpir la ejecución ni generar excepciones no controladas. |

## 8. Fuera de alcance

- Autenticación de usuarios y perfiles con permisos diferenciados.
- Base de datos relacional externa (PostgreSQL, MySQL) o almacenamiento en la nube.
- Envío automatizado de notificaciones reales (Webhooks de Slack/Discord, correos electrónicos o mensajes de WhatsApp).
- Reintentos automáticos avanzados, cachés en memoria y métricas de rendimiento.
- Solución automatizada de incidencias en el sistema de facturación.

## 9. Despliegue

- **Aplicación web:** https://ljchuello-ia.streamlit.app/
- **Repositorio en GitHub:** https://github.com/ljchuello/hola-ia

