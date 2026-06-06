import logging
import json
import os
from typing import Dict, Optional

logger = logging.getLogger(__name__)

_cached_messages = {}

def load_language(lang: str):
    if lang not in _cached_messages:
        base_path = os.path.dirname(__file__)
        file_path = os.path.join(base_path, "locales", f"{lang}.json")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                _cached_messages[lang] = json.load(f)
        except FileNotFoundError:
            logger.error(f"Archivo de idioma no encontrado: {file_path}")
            if lang != "es":
                return load_language("es")
            _cached_messages[lang] = {}
    return _cached_messages.get(lang, {})

# def get_text_by_lang(message_key, lang="es", transition=None, **kwargs):
def get_text_by_lang(active_context, message_key, lang="es", **kwargs):
    messages = load_language(lang)
    text = "Ocurrió un error al procesar la solicitud"

    try:
        if message_key is not None:
            transiciones = messages["RESPUESTAS"][active_context]
            text = transiciones.get(message_key, f"Missing key: {message_key}")
        else:
            text = messages["RESPUESTAS"][active_context]

        if kwargs and isinstance(text, str):
            return text.format(**kwargs)
    except Exception as e:
        logger.error(f"Error al recuperar el texto: {e}")
    return text

class MultiIdioma:
    """
    Clase para gestionar mensajes en múltiples idiomas.
    
    Args:
        idioma_predeterminado (str): Código del idioma predeterminado (ej: 'es', 'en')
        ruta_traducciones (str): Ruta a la carpeta con archivos de traducción
    """
    
    def __init__(self, idioma_predeterminado: str = 'es', 
                 ruta_traducciones: str = './whatsapp/messages'):
        self.idioma_actual = idioma_predeterminado
        self.idioma_predeterminado = idioma_predeterminado
        self.ruta_traducciones = ruta_traducciones
        self.traducciones: Dict[str, Dict[str, str]] = {}
        
        # Cargar traducciones al inicializar
        self._cargar_traducciones()
    
    def _cargar_traducciones(self):
        """Carga todos los archivos de traducción de la carpeta especificada."""
        try:
            if not os.path.exists(self.ruta_traducciones):
                logger.error(f"La carpeta '{self.ruta_traducciones}' no existe.")
                return
            
            for archivo in os.listdir(self.ruta_traducciones):
                if archivo.endswith('.json'):
                    idioma = archivo.split('.')[0].split('_')[1]
                    ruta_completa = os.path.join(self.ruta_traducciones, archivo)
                    
                    with open(ruta_completa, 'r', encoding='utf-8') as f:
                        self.traducciones[idioma] = json.load(f)
            
            if self.idioma_actual not in self.traducciones:
                logger.error(f"No se encontró el idioma '{self.idioma_actual}'")
        
        except Exception as e:
            logger.error(f"Error al cargar traducciones: {e}")
    
    def cambiar_idioma(self, nuevo_idioma: str) -> bool:
        """
        Cambia el idioma actual.
        
        Args:
            nuevo_idioma (str): Código del nuevo idioma
        
        Returns:
            bool: True si el cambio fue exitoso, False en caso contrario
        """
        if nuevo_idioma in self.traducciones:
            self.idioma_actual = nuevo_idioma
            return True
        else:
            logger.error(f"Error: Idioma '{nuevo_idioma}' no disponible")
            return False
    
    def obtener(self, clave: str, datos: dict = None) -> str:
        """
        Obtiene un mensaje traducido.
        
        Args:
            clave (str): Clave del mensaje a obtener
            **kwargs: Valores para formatear en el mensaje (si es necesario)
        
        Returns:
            str: Mensaje traducido o clave si no se encuentra
        """
        # Intentar obtener del idioma actual
        mensaje = self._obtener_mensaje_idioma(self.idioma_actual, clave)
        
        # Si no existe, intentar con el idioma predeterminado
        if mensaje is None and self.idioma_actual != self.idioma_predeterminado:
            mensaje = self._obtener_mensaje_idioma(self.idioma_predeterminado, clave)
        
        # Si todavía no existe, devolver la clave
        if mensaje is None:
            return clave
        
        # Formatear el mensaje si hay parámetros
        if datos:
            try:
                return mensaje.format(**datos)
            except KeyError as e:
                logger.error(f"Error al formatear mensaje '{clave}': {e}")
                return mensaje
        
        return mensaje
    
    def _obtener_mensaje_idioma(self, idioma: str, clave: str) -> Optional[str]:
        """Obtiene un mensaje específico de un idioma."""
        if idioma in self.traducciones:
            return self.traducciones[idioma].get(clave)
        return None
    
    def agregar_traduccion(self, idioma: str, clave: str, mensaje: str):
        """
        Agrega o modifica una traducción.
        
        Args:
            idioma (str): Código del idioma
            clave (str): Clave del mensaje
            mensaje (str): Mensaje traducido
        """
        if idioma not in self.traducciones:
            self.traducciones[idioma] = {}
        
        self.traducciones[idioma][clave] = mensaje
    
    def guardar_traducciones(self, idioma: str = None):
        """
        Guarda las traducciones en archivos JSON.
        
        Args:
            idioma (str, optional): Idioma específico a guardar. 
                                   Si es None, guarda todos.
        """
        try:
            os.makedirs(self.ruta_traducciones, exist_ok=True)
            
            if idioma:
                idiomas = [idioma]
            else:
                idiomas = self.traducciones.keys()
            
            for idioma in idiomas:
                if idioma in self.traducciones:
                    ruta_archivo = os.path.join(
                        self.ruta_traducciones, 
                        f"{idioma}.json"
                    )
                    
                    with open(ruta_archivo, 'w', encoding='utf-8') as f:
                        json.dump(
                            self.traducciones[idioma], 
                            f, 
                            ensure_ascii=False, 
                            indent=2
                        )
        
        except Exception as e:
            logger.error(f"Error al guardar traducciones: {e}")
    
    def listar_idiomas_disponibles(self) -> list:
        """
        Lista los idiomas disponibles.
        
        Returns:
            list: Lista de códigos de idioma disponibles
        """
        return list(self.traducciones.keys())
    
    def __call__(self, clave: str, **kwargs) -> str:
        """Permite usar la instancia como función."""
        return self.obtener(clave, **kwargs)
