DATOS_NEGOCIO_EXTRACTION_PROMPT = """Debes extraer el nombre de la persona y el nombre del negocio.
Extrae únicamente la información que te solicito y nada más. Si no es posible extraer algún dato, deja el campo vacío. Tu nombre como agente es AiBo.
Este es el mensaje del usuario {mensaje}"""

EXTRAER_INTENCION_PROMPT = """Debes extraer la intención del mensaje del usuario.
La intención puede ser 'registrar_venta', 'registrar_inventario', 'borrar_venta', 'borrar_inventario' o 'menu'. 
Por defecto, la intención es 'menu'.
Regresa solamente la intención y nada más. Este es el mensaje {mensaje}"""