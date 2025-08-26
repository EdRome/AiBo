import sys
import os
import pandas as pd
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.data.validators.date import validate_date_2
from src.utils.db_handler import engine

# Configurar logging
logger = logging.getLogger(__name__)

def optimize_dataframe_for_db(df: pd.DataFrame) -> pd.DataFrame:
    """
    Optimizar el DataFrame para guardar en la base de datos
    
    Args:
        df: DataFrame a optimizar
        
    Returns:
        pd.DataFrame: DataFrame optimizado
    """
    df_optimized = df.copy()
    
    # Convertir columnas de fecha
    date_columns = validate_date_2(df_optimized)
    for col in date_columns:
        try:
            df_optimized[col] = pd.to_datetime(df_optimized[col], errors='coerce')
            logger.info(f"Columna de fecha convertida: {col}")
        except Exception as e:
            logger.warning(f"No se pudo convertir columna {col} a fecha: {e}")
    
    # Optimizar tipos de datos
    for col in df_optimized.columns:
        if df_optimized[col].dtype == 'object':
            # Intentar convertir a numérico si es posible
            try:
                pd.to_numeric(df_optimized[col], errors='raise')
                df_optimized[col] = pd.to_numeric(df_optimized[col], errors='coerce')
                logger.info(f"Columna convertida a numérico: {col}")
            except:
                # Si no es numérico, mantener como objeto pero limpiar
                df_optimized[col] = df_optimized[col].astype(str).str.strip()
    
    return df_optimized

def save_db(data: pd.DataFrame, table_name: str, chunk_size: int = 10000) -> bool:
    """
    Guardar DataFrame en la base de datos con optimizaciones
    
    Args:
        data: DataFrame a guardar
        table_name: Nombre de la tabla
        chunk_size: Tamaño de chunks para guardar grandes datasets
        
    Returns:
        bool: True si se guardó exitosamente
    """
    try:
        logger.info(f"💾 Iniciando guardado de {table_name}")
        logger.info(f"📊 Datos: {len(data)} filas, {len(data.columns)} columnas")
        
        # Optimizar DataFrame
        data_optimized = optimize_dataframe_for_db(data)
        
        # Detectar columnas de fecha
        date_columns = validate_date_2(data_optimized)
        if date_columns:
            logger.info(f"📅 Columnas de fecha detectadas: {date_columns}")
        
        # Guardar en chunks si el dataset es muy grande
        if len(data_optimized) > chunk_size:
            logger.info(f"📦 Guardando en chunks de {chunk_size} filas...")
            
            # Eliminar tabla existente si existe
            with engine.connect() as conn:
                conn.execute(f"DROP TABLE IF EXISTS {table_name}")
                conn.commit()
            
            # Guardar en chunks
            for i in range(0, len(data_optimized), chunk_size):
                chunk = data_optimized.iloc[i:i+chunk_size]
                if_exists = 'replace' if i == 0 else 'append'
                
                chunk.to_sql(
                    table_name, 
                    engine, 
                    if_exists=if_exists, 
                    index=False,
                    method='multi'  # Método más rápido para grandes datasets
                )
                
                logger.info(f"✅ Chunk {i//chunk_size + 1} guardado ({len(chunk)} filas)")
        else:
            # Guardar todo de una vez para datasets pequeños
            data_optimized.to_sql(
                table_name, 
                engine, 
                if_exists='replace', 
                index=False
            )
            logger.info(f"✅ {table_name} guardado exitosamente")
        
        # Verificar que se guardó correctamente
        with engine.connect() as conn:
            result = conn.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = result.fetchone()[0]
            logger.info(f"✅ Verificación: {count} filas en {table_name}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error guardando {table_name}: {e}")
        return False

def save_single_file(file_path: str, table_name: str) -> bool:
    """
    Guardar un archivo CSV individual en la base de datos
    
    Args:
        file_path: Ruta al archivo CSV
        table_name: Nombre de la tabla
        
    Returns:
        bool: True si se guardó exitosamente
    """
    try:
        logger.info(f"📁 Leyendo archivo: {file_path}")
        
        # Leer el archivo CSV
        if table_name in ['item_dim', 'customer_dim']:
            df = pd.read_csv(file_path, encoding='latin')
        else:
            df = pd.read_csv(file_path)
        
        # Guardar en la base de datos
        return save_db(df, table_name)
        
    except Exception as e:
        logger.error(f"❌ Error procesando {file_path}: {e}")
        return False


