import json
import logging
import spacy
from spacy.lang.es.stop_words import STOP_WORDS
from interfaces.action import Action
from whatsapp.send_message.send_message import send_whatsapp_message
from data.models.sqlalchemy.recordatorios import Recordatorio
from data.models.menu.recordatorios import RecordatorioItem
from data.db.recordatorios import insert_recordatorio
from cloud_task.cloud_task import schedule_remainder_task

logger = logging.getLogger(__name__)

class CreateRemaindersAction(Action):
    def __init__(self, idioma):
        self.idioma = idioma

    def execute(self, memory, message: str, image: bytes = None):
        """
        Orquesta el flujo de creación de recordatorios: creación -> créditos -> DB -> notificación
        Args:
            memory: Objeto Memory que contiene el estado de la conversación
            message: Mensaje de texto del usuario
            image: Imagen enviada por el usuario (Sin uso, se mantiene por compatibilidad con la interface)
        Returns:
            Objeto Memory actualizado
        """
        logger.info("2.1. Iniciando CreateRemaindersAction...")
        try:
            return self._process_remainders_text(memory, message)
        except Exception as e:
            logger.error(f"Error en CreateRemaindersAction: {e}")
            send_whatsapp_message(memory.user_id, self.idioma.obtener('MENSAJE_ERROR_REGISTRO_RECORDATORIO'))
        
        return memory

    def _create_keywords_list(self, message):
        # Crea lista de keywords
        nlp = spacy.load("es_core_news_sm", disable=["ner", "parser"])
        sin_stopwords = [word for word in message.lower().split() if word not in STOP_WORDS]
        sin_numeros = [word for word in sin_stopwords if not word.isdigit()]
        sin_puntuacion = [word for word in sin_numeros if word.isalpha()]
        sin_indicador_hora = [word for word in sin_puntuacion if word not in ['pm','am']]
        normalizado = " ".join(sin_indicador_hora)

        doc = nlp(normalizado)
        keywords = [token.lemma_ for token in doc]

        return keywords

    def _save_remainder(self, memory, remainder_data, keywords):
        # Crea el recordatorio
        recordatorio = Recordatorio(
            user_id=memory.user_id,
            titulo=remainder_data.get('titulo'),
            descripcion=remainder_data.get('descripcion'),
            fecha_recordatorio=remainder_data.get('fecha_recordatorio'),
            keywords=keywords,
            estatus='activo'
        )

        recordatorio = insert_recordatorio(recordatorio)
        return recordatorio


    def _process_remainders_text(self, memory, message):
        logger.info("2.1.1. Procesando texto para crear recordatorio...")
        # Extrae información del recordatorio
        remainder_data = extract_remainder_data(message)

        keywords = self._create_keywords_list(message)
        
        recordatorio = self._save_remainder(memory, remainder_data, keywords)

        # Si el recordatorio se insertó correctamente
        if recordatorio:
            # Programa la tarea
            task_id = schedule_remainder_task(memory.user_id, recordatorio)
            # Si la tarea no se pudo programar
            if task_id == -1:
                memory.local_state.recordatorios.aibo_message.append(
                    self.idioma.obtener('MENSAJE_ERROR_REGISTRO_RECORDATORIO')
                )
                send_whatsapp_message(memory.user_id, self.idioma.obtener('MENSAJE_ERROR_REGISTRO_RECORDATORIO'))
            else:
                # Agrega el recordatorio a la memoria y retorna mensaje de éxito al usuario
                memory.local_state.recordatorios.recordatorio.append(
                    RecordatorioItem(
                        id=recordatorio.id,
                        titulo=recordatorio.titulo,
                        descripcion=recordatorio.descripcion,
                        fecha_recordatorio=recordatorio.fecha_recordatorio,
                        keywords=recordatorio.keywords,
                        estatus=recordatorio.estatus,
                        task_id=task_id
                    )
                )
                mensaje = self.idioma.obtener(
                    'MENSAJE_REGISTRO_RECORDATORIO_EXITOSO', 
                    {'recordatorio': recordatorio.descripcion + ' en la fecha ' + recordatorio.fecha_recordatorio}
                )
                memory.local_state.recordatorios.aibo_message.append(mensaje)
                send_whatsapp_message(memory.user_id, mensaje)
        else:
            # Si el recordatorio no se insertó correctamente, retorna mensaje de error al usuario
            memory.local_state.recordatorios.aibo_message.append(
                self.idioma.obtener('MENSAJE_ERROR_REGISTRO_RECORDATORIO')
            )
            send_whatsapp_message(memory.user_id, self.idioma.obtener('MENSAJE_ERROR_REGISTRO_RECORDATORIO'))

        return memory
