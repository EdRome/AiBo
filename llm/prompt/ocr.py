EXTRAER_DATOS_VENTA = """Analiza la imagen de este cuaderno de ventas y extrae cada transacción siguiendo estas reglas:
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

EXTRAER_DATOS_GASTO = """Analiza la imagen de este cuaderno de gastos y extrae cada transacción siguiendo estas reglas:
Fecha: Busca una fecha en cualquier parte de la página. Úsala para todos los registros de esa página en el formato "YYYY-MM-DD". Si no existe, usa "1900-12-31".
Método de Pago: Identifica si se menciona el método (Efectivo, Transferencia, Tarjeta). Si no se menciona explícitamente, coloca "No especificado".
Legibilidad: Usa "Ilegible" para texto y -1 para números si no son claros. No adivines.
Limpieza: Ignora notas que no sean gastos, dibujos o tachaduras.
{'gasto': [{'metodo_pago': 'efectivo',
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
     'precio_unitario': 180.0}]}]}
"""