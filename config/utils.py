import logging
import pendulum
import random
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

def fix_past_date_on_remainder(fecha):
    """Cuando una fecha esté codificada para una fecha/hora en el pasado, corrige
    el día para hacerlo en el siguiente día futuro.
    Por ejemplo, si hoy es 22 de junio de 2026 a las 16:00 y un recordatorio se envía
    para el 22 de junio de 2026 a las 15:00, entonces esta función va a agregar 1 día más
    a la fecha para hacerla para el 23 de junio de 2026 a las 15:00.
    Esto ocurre porque el LLM que extrae la información de los recordatorio puede alucinar y,
    para evitar registrar un recordatorio en una fecha pasada que no se pueda ejecutar, esta
    función lo arregla.
    """
    if isinstance(fecha, datetime):
        fecha = pendulum.parse(fecha.isoformat())

    if fecha.is_past():
        return datetime.fromisoformat(fecha.add(days=1).isoformat())
    else:
        return datetime.fromisoformat(fecha.isoformat())

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
        # Encontramos el día objetivo dentro de esa semana
        dia_semana = getattr(res, 'dia_semana')
        if dia_semana is None:
            dia_semana = 0

        # Determinamos la semana base de anclaje
        relacion = getattr(res, 'relacion_semana')
        if relacion is None:
            start_date = ahora
        if relacion == "pasada":
            base_semana = ahora.subtract(weeks=1)
            start_date = base_semana.start_of('week').add(days=dia_semana)
        elif relacion == "siguiente":
            base_semana = ahora.add(weeks=1)
            start_date = base_semana.start_of('week').add(days=dia_semana)
        else:
            base_semana = ahora
            start_date = base_semana.start_of('week').add(days=dia_semana)
        
        # Si se solicita explícitamente forzar un mes específico
        mes_especifico = getattr(res, 'mes_especifico')
        if mes_especifico and relacion is not None:
            start_date = start_date.set(month=mes_especifico)
        elif mes_especifico and relacion is None:
            start_date = start_date.set(month=mes_especifico).start_of('month')
            return start_date.in_timezone("UTC"), start_date.end_of('month').in_timezone("UTC")

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
        # fecha_recordatorio = datetime.strptime(fecha_recordatorio, "%Y-%m-%d %H:%M")
        fecha_recordatorio = pendulum.parse(fecha_recordatorio)
    elif isinstance(fecha_recordatorio, datetime):
        fecha_recordatorio = pendulum.parse(fecha_recordatorio.isoformat())
    elif isinstance(fecha_recordatorio, pendulum.Date):
        fecha_recordatorio = pendulum.datetime(year=fecha_recordatorio.year, month=fecha_recordatorio.month, day=fecha_recordatorio.day)
        
    tiene_hora = hasattr(fecha_recordatorio, 'hour')
    hoy = pendulum.parse(get_current_date().isoformat())
    diferencia = fecha_recordatorio.diff(hoy).in_days()

    # Diccionarios para traducir días y meses a español sin depender del sistema operativo
    # dias_semana = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
    # meses = [
    #     "enero", "febrero", "marzo", "abril", "mayo", "junio",
    #     "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
    # ]

    dia = ""
    # 2. Casos inmediatos
    if fecha_recordatorio.is_same_day(hoy):
        dia = "Hoy"
    elif fecha_recordatorio.is_future() and diferencia == 1:
        dia = "Mañana"
    elif fecha_recordatorio.is_past() and diferencia == 1:
        dia = "Ayer"
    
    if dia != "":
        if tiene_hora:
            fecha_inmediata = "{dia} a las {hora}"
            return fecha_inmediata.format(dia=dia, hora=fecha_recordatorio.strftime("%H:%M"))
        else:
            fecha_inmediata = "{dia}"
            return fecha_inmediata.format(dia=dia)

    # 3. Próximos 7 días (ej. "el martes 16")
    if 1 < diferencia < 7:
        # nombre_dia = dias_semana[fecha_recordatorio.weekday()]
        nombre_dia = fecha_recordatorio.format("dddd", locale="es")
        if tiene_hora:
            return f"el {nombre_dia} {fecha_recordatorio.day} a las {fecha_recordatorio.strftime('%H:%M')}"
        else:
            return f"el {nombre_dia} {fecha_recordatorio.day}"

    # 4. Fechas lejanas: Día + Mes completo en español (ej. "14 de julio")
    # nombre_mes = meses[fecha_recordatorio.month - 1]
    nombre_mes = fecha_recordatorio.format("MMMM", locale="es")
    
    # Si es de un año diferente al actual, añadimos el año para que no haya confusión
    if fecha_recordatorio.year != hoy.year:
        if tiene_hora:
            return f"{fecha_recordatorio.day} de {nombre_mes} a las {fecha_recordatorio.strftime('%H:%M')}"
        else:
            return f"{fecha_recordatorio.day} de {nombre_mes}"
    
    if tiene_hora:
        return f"{fecha_recordatorio.day} de {nombre_mes} a las {fecha_recordatorio.strftime('%H:%M')}"
    else:
        return f"{fecha_recordatorio.day} de {nombre_mes}"
    
def formatear_fecha_humana_intervalo(start_date, end_date):
    """
    Convierte una fecha en una expresión natural en español.
    Si es lejana, devuelve el día y el mes completo (ej. '14 de julio').
    """
    if isinstance(start_date, str):
        start_date = pendulum.parse(start_date, tz="America/Mexico_City")
    elif isinstance(start_date, datetime):
        start_date = pendulum.parse(start_date.isoformat(), tz="America/Mexico_City")
    elif isinstance(start_date, pendulum.Date):
        start_date = pendulum.datetime(year=start_date.year, month=start_date.month, day=start_date.day, tz="America/Mexico_City")
    
    if isinstance(end_date, str):
        end_date = pendulum.parse(end_date, tz="America/Mexico_City")
    elif isinstance(end_date, datetime):
        end_date = pendulum.parse(end_date.isoformat(), tz="America/Mexico_City")
    elif isinstance(end_date, pendulum.Date):
        end_date = pendulum.datetime(year=end_date.year, month=end_date.month, day=end_date.day, tz="America/Mexico_City")
    
    hoy = pendulum.parse(get_current_date().isoformat(), tz="America/Mexico_City")
    diferencia = start_date.diff(hoy).in_days()

    start_month = start_date.format("MMMM", locale="es")
    start_day = start_date.format("D", locale="es")

    end_month = end_date.format("MMMM", locale="es")
    end_day = end_date.format("D", locale="es")

    if start_date.is_same_day(end_date):
        if start_date.is_same_day(hoy):
            return "hoy"
        elif start_date.is_past() and diferencia == 1:
            return "ayer"
        elif start_date.is_future() and diferencia == 1:
            return "mañana"

    if start_month == end_month:
        if start_day == end_day:
            return f"{start_day} de {end_month}"
        else:
            return f"{start_day} al {end_day} de {end_month}"

    else:
        return f"{start_day} de {start_month} al {end_day} de {end_month}"

def pick_random_number(rango1=1, rango2=2):
    return random.randint(rango1, rango2)

def pick_random_text(text_list):
    return random.choice(text_list)

def time_diference(final_datetime, referente_datetime=None):
    """Resta la fecha final con respecto a la fecha de referencia. 
    Si la fecha de referencia es None, entonces compara contra el momento actual
    """

    if referente_datetime is None:
        referente_datetime = pendulum.parse(get_current_date().isoformat(), tz="America/Mexico_City")

    if isinstance(final_datetime, datetime):
        final_datetime = pendulum.parse(final_datetime.isoformat(), tz="America/Mexico_City")

    return (final_datetime - referente_datetime).in_hours()

def remainders_schedule(final_datetime, reference_datetime):
    """Regresa la programación de recordatorios siguiente esta lógica:
    - Si el recordatorio ocurre en más de 24 horas, avisa 12 horas y 1 hora antes
    - Si el recordatorio ocurre en más de 12 horas, avisa 8 horas y 1 hora antes
    - Si falta menos de 1 hora, avisa 5 minutos antes
    - En cualquier otro caso, avisa 1 hora antes y 5 minutos antes
    """

    if reference_datetime is None:
        reference_datetime = pendulum.parse(get_current_date().isoformat(), tz="America/Mexico_City")

    elif isinstance(final_datetime, datetime):
        final_datetime = pendulum.parse(final_datetime.isoformat(), tz="America/Mexico_City")

    diferencia = (final_datetime - reference_datetime).in_hours()

    first_remainder, second_remainder = None, None
    type_first_remainder, type_second_remainder = None, None
    # Si el recordatorio se programó con más de 24 horas
    if diferencia >= 24:
        # El primer recordatorio se programa con 12 horas de anticipación
        first_remainder = final_datetime.subtract(hours=12)

        # Si el recordatorio se programaría después de las 10, corrige el recordatorio para ser a las 10pm
        if first_remainder.hour > 22:
            first_remainder = first_remainder.set(hour=22, minute=0)
        # Pero si el recordatorio se programaría antes de las 6 am, corrige el recordatorio para ser a las 6am
        elif first_remainder.hour < 6:
            first_remainder = first_remainder.set(hour=6, minute=0)

        # Programa el segundo recordatorio 1 hora antes del recordatorio
        second_remainder = final_datetime.subtract(hours=1)
        second_remainder = second_remainder.set(minute=0)

        type_first_remainder = "falta_1_dia"
        type_second_remainder = "falta_1_hora"

    # Si el recordatorio se programa con más de 12 horas
    elif diferencia >= 12:
        # El primer recordatorio se programa con 8 horas de anticipación
        first_remainder = final_datetime.subtract(hours=8, minute=0)

        # Si el recordatorio se programaría después de las 10pm, corrige el recordatorio para ser a las 10pm
        if first_remainder.hour > 22:
            first_remainder = first_remainder.set(hour=22, minute=0)
        # Pero si el recordatorio se programaría antes de las 6am, corrige el recordatorio para ser a las 6am
        elif first_remainder.hour < 6:
            first_remainder = first_remainder.set(hour=6, minute=0)
        
        # Programa el segundo recordatorio 1 hora antes del recordatorio
        second_remainder = final_datetime.subtract(hours=1)
        second_remainder = second_remainder.set(minute=0)

        type_first_remainder = "falta_1_dia"
        type_second_remainder = "falta_1_hora"

    # Para recordatorios con menos de 1 hora de anticipación, programa el recordatorio 5 minutos antes
    elif diferencia <= 1:
        first_remainder = final_datetime.subtract(minutes=5)
        type_first_remainder = "faltan_5_minutos"

    # Para cualquier otro caso, programa el primer recordatorio 1 hora antes y 5 minutos antes
    else:
        first_remainder = final_datetime.subtract(hours=1)
        first_remainder = first_remainder.set(minute=0)

        second_remainder = final_datetime.subtract(minutes=5)
        type_first_remainder = "falta_1_hora"
        type_second_remainder = "faltan_5_minutos"


    returned_first_remainder = datetime.fromtimestamp(first_remainder.timestamp(), pendulum.tz.Timezone("America/Mexico_City"))
    returned_second_remainder = datetime.fromtimestamp(second_remainder.timestamp(), pendulum.tz.Timezone("America/Mexico_City")) if second_remainder is not None else None
    return returned_first_remainder, type_first_remainder, returned_second_remainder, type_second_remainder
