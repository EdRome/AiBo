from data.domains.ventas import crear_venta, DetalleVentaCreate, VentaCreate, VentaDB

def test_insert_venta_exitosamente(db_session):
    """Valida que la lógica migrada persista una venta correctamente."""
    
    datos_venta = VentaCreate(
        metodo_pago="efectivo",
        total=150.60,
        phone_number="5512341234",
        detalles=[DetalleVentaCreate(
            producto="galletas",
            cantidad=1,
            precio_unitario=150.60,
        )]
    )

    venta_id = crear_venta(datos_venta, db_session)
    assert venta_id is not None 

    # Verificar directamente en la base de datos temporal que exista el registro
    venta_en_bd = db_session.query(VentaDB).filter(VentaDB.id == venta_id).first()

    assert venta_en_bd is not None
    assert venta_en_bd.metodo_pago == "efectivo"
    assert venta_en_bd.total == 150.60
    assert venta_en_bd.phone_number == "5512341234"
    assert venta_en_bd.detalles.producto == "galletas"
    assert venta_en_bd.detalles.cantidad == 1
    assert venta_en_bd.precio_unitario == 150.60