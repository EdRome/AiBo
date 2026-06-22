import logging
from sqlalchemy import and_, func
from sqlalchemy import exc
from typing import List
from datetime import timedelta
from zoneinfo import ZoneInfo
from .schemas import VentaCreate
from .models import VentaDB, DetalleVentaDB, SalesSummaryDB
from data.db.utils import get_session
from config.utils import formatear_fecha_humana_intervalo

logger = logging.getLogger(__name__)

def crear_venta(venta_data: VentaCreate, db_session=None, current_date=None):
    db = db_session or get_session()

    logger.info(f"Venta: {venta_data.model_dump()}")

    nueva_venta = VentaDB(
        metodo_pago=venta_data.metodo_pago,
        total=venta_data.total,
        phone_number=venta_data.phone_number,
        fecha=current_date.astimezone(ZoneInfo('UTC'))
    )

    try:
        db.add(nueva_venta)
        db.flush()
        # db.commit()

        for d in venta_data.detalles:
            detalle = DetalleVentaDB(
                producto=d.producto,
                cantidad=d.cantidad,
                precio_unitario=d.precio_unitario,
                venta_id=nueva_venta.id
            )
            db.add(detalle)
        
        db.commit()
        db.refresh(nueva_venta)
        logger.info(f"Nueva detalle de venta registrado con id {nueva_venta.id}")
        
        return nueva_venta.id
    except exc.IntegrityError as e:
        db.rollback()
        logger.error(f"Error de integridad: {e.orig}")  # Error original de Postgres
        logger.error(f"Detalles: {e.params}")
        return None
    except Exception as e:
        db.rollback()
        logger.error(f"Error general: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()  # Imprime el stacktrace completo
        return None

def borrar_venta(venta_id: int, phone_number: str, db_session=None):
    db = db_session or get_session()
    venta = db.query(
        VentaDB
    ).filter(
        and_(
            VentaDB.id == venta_id,
            VentaDB.phone_number == phone_number
        )
    ).first()
    
    if venta:
        try:
            db.delete(venta) # Esto borra automáticamente sus detalles en cascada
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error al borrar la venta {e}")
    return False

def consulta_ventas_dia_actual(phone_number: str, db_session=None):
    db = db_session or get_session()
    venta = db.query(
        SalesSummaryDB
    ).filter(
        SalesSummaryDB.phone_number == phone_number
    ).first()
    return venta

def get_sales_count(user_id: str, db_session=None) -> int:
    try:
        db = db_session or get_session()
        count = db.query(
            func.count(VentaDB.id)
        ).where(
            VentaDB.phone_number == user_id
        ).scalar()
        return count or 0
    except Exception as e:
        logger.error(f"Error al recuperar todas las ventas: {e}")
        return 0

def get_sales_summary(start_date, end_date, phone_number: str, db_session=None):
    try:
        db = db_session or get_session()
        query_objeto = db.query(
            func.sum(VentaDB.total), func.count(VentaDB.id)
        ).filter(
            func.timezone("America/Mexico_City",VentaDB.fecha) >= start_date,
            func.timezone("America/Mexico_City",VentaDB.fecha) < end_date,
            VentaDB.phone_number == phone_number
        )

        total_neto = query_objeto.first()

        intervalo_humano = formatear_fecha_humana_intervalo(start_date, end_date - timedelta(days=1))

        return {
            "periodo_solicitado": intervalo_humano,
            "total": float(total_neto[0] or 0),
            "cantidad_transacciones": total_neto[1] or 0
        }
    except Exception as e:
        logger.error(f"Error al consultas las ventas: {e}")
        return None
    
def get_sales_by_flexible_criteria(user_id: str, start_date, end_date, search_query: str = None, db_session=None) -> VentaDB | None:
    try:
        db = db_session or get_session()
        query = db.query(
            VentaDB, DetalleVentaDB
        ).join(
            DetalleVentaDB, VentaDB.id == DetalleVentaDB.venta_id
        ).filter(
            VentaDB.user_id == user_id
        )
        
        if start_date and end_date:
            query = query.filter(VentaDB.fecha.between(start_date, end_date))
        
        if search_query:
            query = query.filter(DetalleVentaDB.producto.ilike(f"%{search_query}"))

        return query.order_by(VentaDB.fecha.asc()).all()
    except Exception as e:
        logger.error(f"Error al consultar ventas por criterio flexible {e}")
        return None

def delete_sales_by_ids(user_id: str, sales_ids: List[str], db_session=None) -> bool:
    try:
        db = db_session or get_session()
        db.query(VentaDB).filter(
            and_(
                VentaDB.phone_number == user_id,
                VentaDB.id.in_(sales_ids)
            )
        ).delete(
            synchronize_session=False
        )
        db.commit()
        return True
    except Exception as e:
        logger.error(f"Error al eliminar ventas por id {e}")
        return False
