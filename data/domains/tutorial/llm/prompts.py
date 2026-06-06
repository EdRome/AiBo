ONBOARDING_EXTRACTOR_PROMPT = """Debes extraer el nombre del emprendedor.
Solo retorna el texto que te solicito y nada más.

Instrucciones:
- Si falta algún dato, debes retornar `null` para el campo faltante.

Mensaje: {mensaje}
"""