import logging
from .schemas import VentaCreate
from .models import VentaDB, DetalleVentaDB, SalesSummaryDB
from data.db.utils import get_session
from sqlalchemy import and_, func
from sqlalchemy import exc

logger = logging.getLogger(__name__)

db = get_session()

def crear_venta(venta_data: VentaCreate, db_session=None):
    if db_session is not None:
        db = db_session

    logger.info(f"Venta: {venta_data.model_dump()}")

    nueva_venta = VentaDB(
        metodo_pago=venta_data.metodo_pago,
        total=venta_data.total,
        phone_number=venta_data.phone_number
    )

    try:
        db.add(nueva_venta)
        db.commit()
        db.refresh(nueva_venta)

        for d in venta_data.detalles:
            detalle = DetalleVentaDB(
                producto=d.producto,
                cantidad=d.cantidad,
                precio_unitario=d.precio_unitario,
                venta_id=nueva_venta.id
            )
            db.add(detalle)
        
        db.commit()
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

def borrar_venta(venta_id: int, phone_number: str):
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

def consulta_ventas_dia_actual(phone_number: str):
    venta = db.query(
        SalesSummaryDB
    ).filter(
        SalesSummaryDB.phone_number == phone_number
    ).first()
    return venta

def get_sales_count(user_id: str) -> int:
    try:
        count = db.query(
            func.count(VentaDB.id)
        ).where(
            VentaDB.phone_number == user_id
        ).scalar()
        return count or 0
    except Exception as e:
        logger.error(f"Error al recuperar todas las ventas: {e}")
        return 0