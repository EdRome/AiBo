import logging
import pendulum
from datetime import datetime, date
from zoneinfo import ZoneInfo
from typing import Tuple

logger = logging.getLogger(__name__)

dias_semana = {
    0: "Lunes",
    1: "Martes",
    2: "Miércoles",
    3: "Jueves",
    4: "Viernes",
    5: "Sábado",
    6: "Domingo"
}

def get_current_date():
    tz_cdmx = ZoneInfo("America/Mexico_City")
    current_date = datetime.now(tz_cdmx)
    return current_date

def calcular_rango_fechas(rango_solicitado: str, current_date: pendulum.DateTime, res=None) -> Tuple[pendulum.DateTime, pendulum.DateTime]:
    """
    Calcula dinámicamente la fecha inicio (inclusive) y fin (exclusive) 
    basado en un criterio temporal ambiguo.
    """
    # Aseguramos que operamos con un objeto Pendulum
    ahora = pendulum.instance(current_date) if not isinstance(current_date, pendulum.DateTime) else current_date

    # 1. Mapeo para casos directos y estándar
    estrategias_simples = {
        "hoy": lambda dt: (dt.start_of('day'), dt.end_of('day').add(microseconds=1)), # [start_day, start_of_next_day)
        "ayer": lambda dt: (dt.subtract(days=1).start_of('day'), dt.start_of('day')),
        "mañana": lambda dt: (dt.add(days=1).start_of('day'), dt.add(days=2).start_of('day')),
        "esta_semana": lambda dt: (dt.start_of('week'), dt.end_of('week').add(microseconds=1)),
        "semana_pasada": lambda dt: (dt.subtract(weeks=1).start_of('week'), dt.start_of('week')),
        "semana_siguiente": lambda dt: (dt.add(weeks=1).start_of('week'), dt.add(weeks=2).start_of('week')),
        "este_mes": lambda dt: (dt.start_of('month'), dt.end_of('month').add(microseconds=1)),
        "mes_pasado": lambda dt: (dt.subtract(months=1).start_of('month'), dt.start_of('month')),
        "mes_siguiente": lambda dt: (dt.add(months=1).start_of('month'), dt.add(months=2).start_of('month')),
    }

    # Si es una de las estrategias rápidas, la ejecutamos inmediatamente
    if rango_solicitado in estrategias_simples:
        return estrategias_simples[rango_solicitado](ahora)

    # 2. Manejo de Casos Especiales Dinámicos
    if rango_solicitado == "dia_especifico_semana" and res:
        # Pendulum indexa días igual que Python (0=Lunes, 6=Domingo) o texto ('monday', etc.)
        dia_semana = getattr(res, 'dia_semana', res.get('dia_semana') if isinstance(res, dict) else 0)
        start_date = ahora.start_of('week').add(days=dia_semana)
        return start_date, start_date.add(days=1)

    if rango_solicitado == "especifico" and res:
        # Determinamos la semana base de anclaje
        relacion = getattr(res, 'relacion_semana', 'actual')
        if relacion is None:
            relacion = "actual"
    
        if relacion == "pasada":
            base_semana = ahora.subtract(weeks=1)
        elif relacion == "siguiente":
            base_semana = ahora.add(weeks=1)
        else:
            base_semana = ahora

        # Encontramos el día objetivo dentro de esa semana
        dia_semana = getattr(res, 'dia_semana', 1)
        if dia_semana is None:
            dia_semana = 1

        start_date = base_semana.start_of('week').add(days=dia_semana)
        
        # Si se solicita explícitamente forzar un mes específico
        mes_especifico = getattr(res, 'mes_especifico', 1)
        if mes_especifico:
            start_date = start_date.set(month=mes_especifico)

        return start_date.start_of('day').in_timezone("UTC"), start_date.add(days=1).start_of('day').in_timezone("UTC")

    # Fallback por defecto en caso de error o dato no reconocido
    return ahora.set(year=1900, month=12, day=31).start_of('day'), ahora.set(year=1900, month=12, day=31).start_of('day')

def formatear_fecha_humana(fecha_recordatorio):
    """
    Convierte una fecha en una expresión natural en español.
    Si es lejana, devuelve el día y el mes completo (ej. '14 de julio').
    """
    # 1. Convertir a objeto date si viene como string
    if isinstance(fecha_recordatorio, str):
        fecha_recordatorio = datetime.strptime(fecha_recordatorio, "%Y-%m-%d %H:%M")
    elif isinstance(fecha_recordatorio, datetime):
        fecha_recordatorio = fecha_recordatorio
        
    hoy = get_current_date()
    es_hoy = fecha_recordatorio.date() == hoy.date()
    diferencia = (fecha_recordatorio.date() - hoy.date()).days
    after = fecha_recordatorio > hoy
    before = fecha_recordatorio < hoy

    # Diccionarios para traducir días y meses a español sin depender del sistema operativo
    dias_semana = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
    meses = [
        "enero", "febrero", "marzo", "abril", "mayo", "junio",
        "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
    ]

    fecha_inmediata = "{dia} a las {hora}"
    dia = ""
    # 2. Casos inmediatos
    if es_hoy:
        dia = "Hoy"
    elif not es_hoy and after:
        dia = "Mañana"
    elif not es_hoy and before:
        dia = "Ayer"
    
    if dia != "":
        return fecha_inmediata.format(dia=dia, hora=fecha_recordatorio.strftime("%H:%M"))

    # 3. Próximos 7 días (ej. "el martes 16")
    if 1 < diferencia < 7:
        nombre_dia = dias_semana[fecha_recordatorio.weekday()]
        return f"el {nombre_dia} {fecha_recordatorio.day} a las {fecha_recordatorio.strftime('%H:%M')}"

    # 4. Fechas lejanas: Día + Mes completo en español (ej. "14 de julio")
    nombre_mes = meses[fecha_recordatorio.month - 1]
    
    # Si es de un año diferente al actual, añadimos el año para que no haya confusión
    if fecha_recordatorio.year != hoy.year:
        return f"{fecha_recordatorio.day} de {nombre_mes} a las {fecha_recordatorio.strftime('%H:%M')}"
    
    return f"{fecha_recordatorio.day} de {nombre_mes} a las {fecha_recordatorio.strftime('%H:%M')}"