CHANNEL_ANALYSIS_PROMPT="""Debes extraer los canales de venta del siguiente mensaje del usuario. Este es el mensaje {mensaje}"""

NEED_ANALYSIS_PROMPT="""Extrae las preocupaciones del usuario relacionadas con su negocio y un breve resumen.
Si no puedes extraer ninguna información, responde con "es_respuesta_vaga": true y "frase_vaga": "la frase que el usuario dijo" y no agregues nada más.
Este es el giro {giro}.
Esta es una breve descripción {descripcion}.
Este es el mensaje {mensaje}"""

MAIN_PAIN_ANALYSIS_PROMPT="""Extrae solamente el principal punto de dolor del siguiente mensaje del usuario {mensaje}."""
AFFECTION_ANALYSIS_PROMPT="""Extrae la afectación del siguiente mensaje del usuario. Los puntos de dolor que puedes inferir son: tiempo, incertidumbre y dinero.
Este es el mensaje {mensaje}"""

OTHER_PAIN_ANALYSIS_PROMPT="""Extrae puntos de dolor adicionales del siguiente mensaje del usuario. Ten en cuenta que su principal punto de dolor ya fue extraído.
Este es el principal punto de dolor: {principal_punto_de_dolor}.
Si no hay puntos de dolor adicionales, responde con "otros": [].
Este es el mensaje {mensaje}"""

EXTRAER_IDIOMA_PROMPT = """Debes extraer el idioma del mensaje del usuario.
El idioma puede ser 'es' o 'en'.
Regresa solamente el idioma y nada más. Este es el mensaje {mensaje}"""