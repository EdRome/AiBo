import logging
from data.models.venta.RegistroVenta import VentaCreate
from data.models.sqlalchemy.venta import VentaDB, DetalleVentaDB, SalesSummaryDB
from data.db.utils import get_session
from sqlalchemy import and_

logger = logging.getLogger(__name__)

db = get_session()

def crear_venta(venta_data: VentaCreate):

    logger.info(f"Venta: {venta_data.model_dump()}")

    # 1. Crear la instancia de la venta (Cabecera)
    nueva_venta = VentaDB(
        metodo_pago=venta_data.metodo_pago,
        total=venta_data.total,
        phone_number=venta_data.phone_number
    )

    # 2. Crear las instancias de los detalles y asociarlas a la venta
    for d in venta_data.detalles:
        detalle = DetalleVentaDB(
            producto=d.producto,
            cantidad=d.cantidad,
            precio_unitario=d.precio_unitario
        )
        nueva_venta.detalles.append(detalle)

    # 3. Guardar en la DB (SQLAlchemy maneja la transacción)
    try:
        db.add(nueva_venta)
        db.commit()
        db.refresh(nueva_venta) # Esto carga el ID generado por Postgres
        return nueva_venta.id
    except Exception as e:
        db.rollback()
        logger.error(f"Error al insertar la venta {e}")
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