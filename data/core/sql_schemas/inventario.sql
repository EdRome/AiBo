-- 1. Habilitar extensión para UUIDs (opcional, pero recomendado para sistemas modernos)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. Tabla Maestra de Productos (La Identidad)
CREATE TABLE productos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    phone_number VARCHAR(20) NOT NULL,
    marca VARCHAR(100),
    nombre_base VARCHAR(255) NOT NULL, -- Ej: "Bolso Louis Vuitton LVX" o "Aretes de Acero"
    descripcion TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Tabla de Alias para Búsqueda (Variantes de nombres)
CREATE TABLE productos_alias (
    id SERIAL PRIMARY KEY,
    producto_id UUID REFERENCES productos(id) ON DELETE CASCADE,
    nombre_alias VARCHAR(255) NOT NULL,
    UNIQUE(product_id, alias_name)
);

-- Creamos un índice GIN para búsquedas de texto parcial ultra rápidas
CREATE INDEX idx_aliases_name_trgm ON product_aliases USING gin (alias_name gin_trgm_ops);

-- 4. Tabla de SKUs (Variantes Reales: Tallas, Grados de uso, Baños de oro)
CREATE TABLE productos_sku (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    producto_id UUID REFERENCES productos(id) ON DELETE CASCADE,
    precio_venta DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    sku VARCHAR(100) UNIQUE NOT NULL, -- Tu código único (Ej: LV-X-2024-A)
    costo DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    -- Aquí vive la magia: {"grado": "A", "año": 2024} o {"material": "Acero", "baño": "Oro"}
    atributos JSONB NOT NULL DEFAULT '{}', 
    stock_actual INT NOT NULL DEFAULT 0,
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índice para búsquedas rápidas dentro del JSONB
CREATE INDEX idx_skus_attributes ON productos_sku USING gin (attributes);

-- 5. Tabla de Trazabilidad (Movimientos de Inventario)
CREATE TABLE trazabilidad (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sku_id UUID REFERENCES productos_sku(id) ON DELETE CASCADE,
    tipo VARCHAR(20) CHECK (movement_type IN ('IN', 'OUT', 'ADJUSTMENT', 'RETURN')),
    cantidad INT NOT NULL, -- Positivo para entrada, negativo para salida
    whatsapp_msg_id VARCHAR(100), -- ID de factura o número de venta
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ---
-- --- EJEMPLOS DE USO (DML)
-- ---

-- -- Insertar un producto
-- INSERT INTO products (id, brand, base_name) 
-- VALUES ('550e8400-e29b-41d4-a716-446655440000', 'Louis Vuitton', 'Bolso Modelo LVX');

-- -- Insertar sus alias
-- INSERT INTO product_aliases (product_id, alias_name) VALUES 
-- ('550e8400-e29b-41d4-a716-446655440000', 'LVX 2024'),
-- ('550e8400-e29b-41d4-a716-446655440000', 'Bolso LV Pequeño');

-- -- Crear variantes (SKUs) con diferentes grados de uso
-- INSERT INTO product_skus (product_id, sku_code, price, attributes) VALUES 
-- ('550e8400-e29b-41d4-a716-446655440000', 'LVX-24-A', 2500.00, '{"año": 2024, "grado": "A"}'),
-- ('550e8400-e29b-41d4-a716-446655440000', 'LVX-24-B', 1800.00, '{"año": 2024, "grado": "B"}');