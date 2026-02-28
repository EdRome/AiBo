SUMMARY_CREATION_PROMPT = """Crea un resumen de lo que dijo el usuario sobre sus productos/servicios, infiere el giro del negocio y crea una breve descripción del negocio.
Extrae únicamente la información que te solicito y nada más. Si no es posible extraer algún dato, deja el campo vacío. Tu nombre como agente es AiBo.
Este es el mensaje del usuario {mensaje}"""

AFFECTION_SUMMARY_PROMPT="""Crea un resumen de lo que está afectando el negocio del usuario utilizando el siguiente mensaje del usuario {mensaje}. Extrae únicamente la información que te solicito y nada más."""

PAIN_POINT_SUMMARY_CREATION_PROMPT="""Extrae un resumen del punto de dolor del usuario, la causa raíz y el objetivo general opuesto al punto de dolor del mensaje del usuario {mensaje}."""