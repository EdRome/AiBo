import logging
from data.config.database import get_session
from .schemas import GastoCreate
from .models import GastoDB, DetalleGastoDB, ExpenseSummaryDB
from sqlalchemy import and_

logger = logging.getLogger(__name__)

db = get_session()

def create_gasto(gasto_data: GastoCreate):

    logger.info(f"Gasto: {gasto_data.model_dump()}")

    # 1. Crear la instancia del gasto (Cabecera)
    nuevo_gasto = GastoDB(
        metodo_pago=gasto_data.metodo_pago,
        total=gasto_data.total,
        phone_number=gasto_data.phone_number
    )

    # 2. Crear las instnancias de los detalles y asociarlos al gasto
    for d in gasto_data.detalles:
        detalle = DetalleGastoDB(
            producto=d.producto,
            cantidad=d.cantidad,
            precio_unitario=d.precio_unitario,
        )
        nuevo_gasto.detalles.append(detalle)

    # 3. Guardar en la DB (SQLAlchemy maneja la transacción)
    try:
        db.add(nuevo_gasto)
        db.commit()
        db.refresh(nuevo_gasto) # Esto carga el ID generado por Postgres
        return nuevo_gasto.id
    except Exception as e:
        db.rollback()
        logger.error(f"Error al insertar el gasto {e}")
        return None

def borrar_gasto(gasto_id: int, phone_number: str):
    gasto = db.query(
        GastoDB
    ).filter(
        and_(
            GastoDB.id == gasto_id,
            GastoDB.phone_number == phone_number
        )
    ).first()
    
    if gasto:
        try:
            db.delete(gasto) # Esto borra automáticamente sus detalles en cascada
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error al borrar el gasto {e}")
    return False

def consulta_gastos_dia_actual(phone_number: str):
    gasto = db.query(
        ExpenseSummaryDB
    ).filter(
        ExpenseSummaryDB.phone_number == phone_number
    ).first()
    return gasto