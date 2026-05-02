EXPENSES_EXTRACTOR_PROMPT = """Debes extraer la información de gastos del mensaje, deglosando el mensaje en detalles de gastos.
Si no pudieras completar algun campo, regresa el campo vacío "".
NO hagas cálculos matemáticos, el campo total dejalo vacío.
NO inventes información que no se mencione en el mensaje.
El método de pago solo puede ser "efectivo", "tarjeta" o "transferencia". Si no se menciona ninguno, regresa el campo vacío.
Siempre asume que el precio es total, a menos que el mensaje indique explicitamente lo contrario.
El precio unitario o total NO pueden ser menor o igual a cero, excepto si el usuario lo indica explícitamente.
Mensaje: {mensaje}"""