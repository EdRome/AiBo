-- 1. Crear la tabla de Gastos (Cabecera)
CREATE TABLE transactional.gastos (
    id SERIAL PRIMARY KEY,
    metodo_pago VARCHAR(50) DEFAULT 'efectivo',
    total NUMERIC(12, 2) DEFAULT 0.0,
    fecha TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    phone_number TEXT NOT NULL
);

-- 2. Crear la tabla de Detalles de Gasto (Productos)
CREATE TABLE transactional.detalles_gasto (
    id SERIAL PRIMARY KEY,
    gasto_id INTEGER NOT NULL,
    producto VARCHAR(255) NOT NULL,
    cantidad INTEGER NOT NULL DEFAULT 1,
    precio_unitario NUMERIC(12, 2) NOT NULL DEFAULT 0.0,
    
    -- Restricción de llave foránea con borrado en cascada
    CONSTRAINT fk_gasto
        FOREIGN KEY (gasto_id) 
        REFERENCES transactional.gastos(id) 
        ON DELETE CASCADE
);

-- 3. Crear la vista de resumen de gastos
CREATE VIEW transactional.expense_summary AS 
SELECT 
    v.phone_number, 
    SUM(v.total) AS gasto_total, 
    SUM(resumen_dg.unidades_por_gasto) AS unidades_gastadas, 
    COUNT(v.id) AS num_gastos
FROM dev.gastos AS v
LEFT JOIN (
    -- Sumamos las unidades por cada venta individualmente
    SELECT gasto_id, SUM(cantidad) AS unidades_por_gasto
    FROM dev.detalles_gasto
    GROUP BY gasto_id
) AS resumen_dg ON v.id = resumen_dg.gasto_id
WHERE v.fecha >= DATE(CURRENT_TIMESTAMP AT TIME ZONE 'America/Mexico_City')
GROUP BY v.phone_number
;