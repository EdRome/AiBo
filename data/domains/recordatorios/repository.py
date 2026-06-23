import logging
from sqlalchemy import update, func, and_
from datetime import timedelta
from zoneinfo import ZoneInfo
from data.db.utils import get_session
from .models import Recordatorio as RecordatorioSQL
from .schemas import RecordatorioBase
from config.utils import formatear_fecha_humana_intervalo, get_current_date

logger = logging.getLogger(__name__)

def insert_remainder(recordatorio: RecordatorioBase, db_session=None):
    try:
        db = db_session or get_session()
        new_remainder = RecordatorioSQL(
            phone_number = recordatorio.phone_number,
            task_id = recordatorio.task_id,
            fecha_recordatorio = recordatorio.fecha_recordatorio,
            mensaje = recordatorio.recordatorio,
            time_delta = recordatorio.time_delta,
            status = recordatorio.status
        )
        db.add(new_remainder)
        db.commit()
        return new_remainder.id
    except Exception as e:
        logger.error(f"Error al guardar recordatorio: {e}")
        return None

def update_remainder(recordatorio: RecordatorioBase, db_session=None):
    try:
        db = db_session or get_session()
        stmt = update(
            RecordatorioSQL
        ).where(
            RecordatorioSQL.task_id == recordatorio.task_id
        ).values(
            status = recordatorio.status
        )

        db.execute(stmt)
        db.commit()
        return True
    except Exception as e:
        logger.error(f"Error al actualizar recordatorio: {e}")
        return None

def get_remainder_count(user_id: str, db_session=None) -> int:
    try:
        db = db_session or get_session()
        count = db.query(
            func.count(RecordatorioSQL.id)
        ).where(
            RecordatorioSQL.phone_number == user_id
        ).scalar()
        return count or 0
    except Exception as e:
        logger.error(f"Error al recuperar todos los recordatorios: {e}")
        return 0
    
def get_remainder_by_criteria(user_id: str, start_date=None, end_date=None, search_query=None, db_session=None):
    DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    MESES = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]
    try:
        db = db_session or get_session()
        query = db.query(RecordatorioSQL)
        filters = []

        filters.append(RecordatorioSQL.phone_number == user_id)

        if start_date and end_date:
            filters.append(
                func.timezone("America/Mexico_City", RecordatorioSQL.fecha_recordatorio) >= start_date
            )
            filters.append(
                func.timezone("America/Mexico_City", RecordatorioSQL.fecha_recordatorio) < end_date
            )
        elif start_date:
            filters.append(
                func.timezone("America/Mexico_City", RecordatorioSQL.fecha_recordatorio) >= start_date
            )
        
        if search_query:
            filters.append(RecordatorioSQL.mensaje.ilike(f"%{search_query}"))
        
        if filters:
            query = query.filter(and_(*filters))

        recordatorios = query.order_by(RecordatorioSQL.fecha_recordatorio.asc()).all()
    
        if not recordatorios:
            intervalo_humano = formatear_fecha_humana_intervalo(start_date, end_date - timedelta(days=1))
            return {
                "periodo_solicitado": intervalo_humano,
                "lista_recordatorios": []
            }

        # Construimos la lista con el nuevo formato requerido
        lista_formateada = []
        for r in recordatorios:
            # Extraemos la fecha del recordatorio
            fecha = r.fecha_recordatorio.astimezone(ZoneInfo("America/Mexico_City"))

            # Obtenemos el nombre del día y del mes en español usando el índice
            dia_semana = DIAS[fecha.weekday()]
            dia = fecha.day
            mes = MESES[fecha.month - 1]  # Restamos 1 porque los meses van de 1 a 12 y la lista de 0 a 11
            hora = fecha.hour
            minutos = str(fecha.minute).zfill(2)

            icono = "⏲️"
            if fecha < get_current_date():
                icono = "✅"
            
            # Creamos la línea con el formato
            linea = f"{icono} El {dia_semana} {dia} de {mes}: {r.mensaje} a las {hora}:{minutos}\n"
            lista_formateada.append(linea)
        

        intervalo_humano = formatear_fecha_humana_intervalo(start_date, end_date - timedelta(days=1))

        return {
            "periodo_solicitado": intervalo_humano,
            "lista_recordatorios": "".join(lista_formateada)
        }
    except Exception as e:
        logger.error(f"Error al recuperar los recordatorios por criterio de búsqueda: {e}")
        return None