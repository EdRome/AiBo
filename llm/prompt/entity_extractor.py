DATOS_NEGOCIO_EXTRACTION_PROMPT = """Debes extraer el nombre de la persona, el nombre del negocio y la ubicación del negocio.
Extrae únicamente la información que te solicito y nada más. Si no es posible extraer algún dato, deja el campo vacío.
Este es el mensaje del usuario {mensaje}"""

EXTRAER_INTENCION_PROMPT = """Debes extraer la intención del mensaje del usuario.
La intención puede ser 'registrar_venta','consultar_venta','registrar_recordatorio','consultar_recordatorio' o 'menu'. 
Por defecto, la intención es 'menu'.
Regresa solamente la intención y nada más. Este es el mensaje {mensaje}"""

ROUTER_PROMPT = """
Eres el procesador lógico. Tu misión es desglosar el mensaje del usuario en acciones técnicas ejecutables.

REGLAS DE ORO:
1. MULTI-ACCIÓN: Si el usuario pide varias cosas (ej: "registra venta y ponme un recordatorio"), extrae TODAS las acciones en una lista.
2. EXTRACCIÓN DE DATOS: No solo identifiques la acción, extrae los datos necesarios (montos, fechas, nombres, descripciones).
3. INFERENCIA TEMPORAL: Usa la fecha actual para convertir términos como "mañana", "lunes" o "en 2 horas" en fechas/horas reales.
4. ESTADO POR DEFECTO: Si el mensaje es una charla trivial o no detectas una acción clara, usa 'charla_narrativa'.

ACCIONES DISPONIBLES:
- VENTAS: 'registrar_venta', 'consultar_venta' (requiere: monto, concepto opcional).
- RECORDATORIOS: 'registrar_recordatorio', 'consultar_recordatorio' (requiere: mensaje_recordatorio, fecha_hora_iso).
- MENU: 'menu' (solo si no es posible inferir la acción que quiere hacer el usuario)

MENSAJE DEL USUARIO: {mensaje}
"""