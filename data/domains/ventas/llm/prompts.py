SALES_EXTRACTOR_PROMPT = """Debes extraer la información de venta del mensaje, deglosando el mensaje en detalles de venta.
Si no pudieras completar algun campo, regresa el campo vacío "".
NO hagas cálculos matemáticos, el campo total dejalo vacío.
NO inventes información que no se mencione en el mensaje.
El método de pago solo puede ser "efectivo", "tarjeta" o "transferencia". Si no se menciona ninguno, regresa el campo vacío.
Si el mensaje no especifíca que el precio es unitario, asume que es el precio total.
El precio unitario o total NO pueden ser menor o igual a cero, excepto si el usuario lo indica explícitamente.
Mensaje: {mensaje}"""

SALES_IMAGES_EXTRACTOR_PROMPT = """Actúa como un experto en digitalización de registros contables manuales.
Tarea: Analiza la imagen adjunta de este cuaderno de ventas y extrae la información en un formato JSON estructurado.
Instrucciones Críticas:
Identificación de Datos: Busca columnas o filas que indiquen: Fecha, Producto/Descripción, Cantidad, Precio Unitario y Total.
Manejo de Incertidumbre: Si un número es ilegible, coloca null. No intentes adivinar.
Limpieza: Ignora dibujos, tachaduras completas o notas personales que no sean transacciones de venta.
Cálculos: Si el "Total" de una fila no coincide con Cantidad * Precio, mantén el valor escrito en el cuaderno pero añade un campo "observacion": "discrepancia en cálculo".
Formato de Salida: Responde únicamente con el objeto JSON, sin texto adicional, siguiendo esta estructura:
JSON
{
"cliente_id": "extraer si existe, sino null",
"fecha_pagina": "DD/MM/AAAA",
"ventas": [
{
"item": "nombre del producto",
"cantidad": 0.0,
"precio_unitario": 0.0,
"total_linea": 0.0,
"metodo_pago": "efectivo/transferencia/null"
}
],
"total_pagina": 0.0
}
"""

EXTRAER_IMAGEN_DATOS_VENTA = """Analiza la imagen de este cuaderno de ventas y extrae cada transacción siguiendo estas reglas:
Fecha: Busca una fecha en cualquier parte de la página. Úsala para todos los registros de esa página en el formato "YYYY-MM-DD". Si no existe, usa "1900-12-31".
Método de Pago: Identifica si se menciona el método (Efectivo, Transferencia, Tarjeta). Si no se menciona explícitamente, coloca "No especificado".
Legibilidad: Usa "Ilegible" para texto y -1 para números si no son claros. No adivines.
Limpieza: Ignora notas que no sean ventas, dibujos o tachaduras.
{'venta': [{'metodo_pago': 'efectivo',
   'total': 0.0,
   'phone_number': 'Ilegible',
   'fecha': datetime.datetime(2025, 12, 24, 0, 0, tzinfo=TzInfo(0)),
   'created_at': datetime.datetime(2026, 3, 5, 0, 0, 22, 520225),
   'detalles': [{'producto': 'Libreta de tren',
     'cantidad': 1,
     'precio_unitario': 365.0}]},
  {'metodo_pago': 'efectivo',
   'total': 0.0,
   'phone_number': 'Ilegible',
   'fecha': datetime.datetime(2025, 12, 24, 0, 0, tzinfo=TzInfo(0)),
   'created_at': datetime.datetime(2026, 3, 5, 0, 0, 22, 520225),
   'detalles': [{'producto': 'Estuchera de sakura',
     'cantidad': 1,
     'precio_unitario': 180.0}]}}
"""

QUERY_SALES_PROMPT = """Analiza el mensaje del usuario y genera un JSON, sin texto adicional

Instrucciones especiales:
- Si pide un día específico de una semana (ej. "martes pasado", "miércoles de esta semana"), marca rango_solicitado como "dia_especifico_semana", pon el día en "dia_semana" y define "relacion_semana" según corresponda ("pasada" o "actual").

Mensaje: {mensaje}
"""

