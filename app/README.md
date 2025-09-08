# Ecommerce Data Analysis

Análisis de datos de ecommerce con pipeline automatizado para cargar datos a Supabase.

## 🚀 Características

- **Pipeline de Datos Automatizado**: Carga automática de archivos CSV a Supabase
- **Validación de Datos**: Verificación de calidad y limpieza automática
- **Interfaz Web**: Dashboard interactivo con Streamlit
- **Análisis de Negocio**: Métricas y visualizaciones de KPIs

## 📁 Estructura del Proyecto

```
mockup/
├── app/
│   ├── data/                    # Archivos CSV de datos
│   │   ├── customer_dim.csv
│   │   ├── fact_table.csv
│   │   ├── item_dim.csv
│   │   ├── store_dim.csv
│   │   ├── time_dim.csv
│   │   └── Trans_dim.csv
│   ├── src/
│   │   ├── pipelines/           # Pipeline de datos
│   │   │   └── data_pipeline.py
│   │   ├── data/
│   │   │   ├── readers/         # Lectura de archivos
│   │   │   ├── writers/         # Escritura a BD
│   │   │   └── validators/      # Validación de datos
│   │   ├── utils/               # Utilidades (conexión BD)
│   │   └── app/                 # Aplicación Streamlit
│   ├── run_pipeline.py          # Script principal del pipeline
│   ├── run_pipeline_simple.py   # Script simple del pipeline
│   └── test_pipeline.py         # Script de pruebas
├── requirements.txt
└── README.md
```

## 🛠️ Instalación

1. **Clonar el repositorio**:
   ```bash
   git clone <repository-url>
   cd mockup
   ```

2. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar variables de entorno**:
   - Crear archivo `app/dev.env` con las credenciales de Supabase:
   ```
   USER=tu_usuario
   PASSWORD=tu_password
   HOST=tu_host.supabase.com
   PORT=6543
   DBNAME=postgres
   ```

## 📊 Uso del Pipeline

### Opción 1: Desde la línea de comandos

**Ejecutar pipeline completo**:
```bash
cd app
python run_pipeline_simple.py
```

**Ejecutar con logging detallado**:
```bash
cd app
python run_pipeline.py
```

### Opción 2: Desde la aplicación web

1. **Iniciar la aplicación**:
   ```bash
   cd app
   streamlit run src/app/main.py
   ```

2. **Usar el sidebar**:
   - Expandir "📊 Pipeline de Datos"
   - Hacer clic en "🚀 Ejecutar Pipeline Completo"
   - O seleccionar archivo individual para cargar

### Opción 3: Cargar archivos individuales

```python
from src.data.writers.save_db import save_single_file

# Cargar un archivo específico
success = save_single_file("path/to/file.csv", "table_name")
```

## 🔧 Funcionalidades del Pipeline

### ✅ Validación de Datos
- Verificación de archivos vacíos
- Detección de columnas vacías
- Identificación de duplicados
- Validación de tipos de datos

### 🧹 Limpieza Automática
- Eliminación de filas completamente vacías
- Limpieza de espacios en blanco
- Conversión automática de fechas
- Optimización de tipos de datos

### 📦 Carga Optimizada
- Carga en chunks para archivos grandes
- Manejo de errores robusto
- Logging detallado
- Verificación post-carga

## 📈 Archivos Procesados

| Archivo | Tabla | Descripción |
|---------|-------|-------------|
| `time_dim.csv` | `time_dim` | Dimensiones de tiempo |
| `fact_table.csv` | `fact_table` | Tabla de hechos principal |
| `Trans_dim.csv` | `trans_dim` | Dimensiones de transacciones |
| `item_dim.csv` | `item_dim` | Dimensiones de productos |
| `store_dim.csv` | `store_dim` | Dimensiones de tiendas |
| `customer_dim.csv` | `customer_dim` | Dimensiones de clientes |

## 🔍 Monitoreo

### Verificar estado de la BD
```python
from src.utils.db_handler import engine

with engine.connect() as conn:
    result = conn.execute("""
        SELECT table_name, COUNT(*) as rows
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        GROUP BY table_name
    """)
    tables = result.fetchall()
    print(tables)
```

### Logs del Pipeline
- Los logs se guardan en `data_pipeline.log`
- Incluye información detallada de cada paso
- Errores y advertencias claramente identificados

## 🚨 Solución de Problemas

### Error de conexión a Supabase
1. Verificar credenciales en `app/dev.env`
2. Comprobar conectividad de red
3. Verificar que Supabase esté activo

### Error de archivos no encontrados
1. Verificar que los archivos CSV estén en `app/data/`
2. Comprobar nombres de archivos (case-sensitive)
3. Verificar permisos de lectura

### Error de memoria
- Para archivos muy grandes, el pipeline usa chunks automáticamente
- Si persiste, reducir `chunk_size` en `save_db.py`

## 📝 Logs de Ejemplo

```
🚀 Iniciando pipeline de datos...
📁 Buscando archivos en: /path/to/data
📊 Archivos CSV encontrados: 6
   - time_dim.csv
   - fact_table.csv
   - Trans_dim.csv
   - item_dim.csv
   - store_dim.csv
   - customer_dim.csv

📁 Procesando: /path/to/data/time_dim.csv
✅ time_dim guardado exitosamente en Supabase
📁 Procesando: /path/to/data/fact_table.csv
✅ fact_table guardado exitosamente en Supabase
...

🎉 Pipeline completado!
✅ Tablas creadas: 6
❌ Errores: 0
⏱️  Tiempo total: 0:02:15
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crear una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abrir un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. # AiBo
