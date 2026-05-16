-- 1. Crear la tabla de Ventas (Cabecera)
CREATE TABLE transactional.ventas (
    id SERIAL PRIMARY KEY,
    metodo_pago VARCHAR(50) DEFAULT 'efectivo',
    total NUMERIC(12, 2) DEFAULT 0.0,
    fecha TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    phone_number TEXT NOT NULL
);

-- 2. Crear la tabla de Detalles de Venta (Productos)
CREATE TABLE transactional.detalles_venta (
    id SERIAL PRIMARY KEY,
    venta_id INTEGER NOT NULL,
    producto VARCHAR(255) NOT NULL,
    cantidad INTEGER NOT NULL DEFAULT 1,
    precio_unitario NUMERIC(12, 2) NOT NULL DEFAULT 0.0,
    
    -- Restricción de llave foránea con borrado en cascada
    CONSTRAINT fk_venta
        FOREIGN KEY (venta_id) 
        REFERENCES transactional.ventas(id) 
        ON DELETE CASCADE
);

-- 3. Crear la vista de resumen de ventas
CREATE VIEW transactional.sales_summary AS 
SELECT 
    v.phone_number, 
    SUM(v.total) AS venta_total, 
    SUM(resumen_dv.unidades_por_venta) AS unidades_vendidas, 
    COUNT(v.id) AS num_ventas
FROM transactional.ventas AS v
LEFT JOIN (
    -- Sumamos las unidades por cada venta individualmente
    SELECT venta_id, SUM(cantidad) AS unidades_por_venta
    FROM transactional.detalles_venta
    GROUP BY venta_id
) AS resumen_dv ON v.id = resumen_dv.venta_id
WHERE v.fecha >= DATE(CURRENT_TIMESTAMP AT TIME ZONE 'America/Mexico_City')
GROUP BY v.phone_number
;