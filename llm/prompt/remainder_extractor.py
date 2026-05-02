REMAINDER_EXTRACTOR_PROMPT = """Debes extraer la información del recordatorio del mensaje. 
Solo debes extraer la fecha y hora de cuando el mensaje indica que quiere recibir el recordatorio y el mensaje del recordatorio.
En caso de que no pudiera extraer la fecha y hora, debes dejar el campo vacío.
Mensaje: {message}
"""