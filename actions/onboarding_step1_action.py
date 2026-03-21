import json
import logging
from interfaces.action import Action
from whatsapp.send_message.send_message import send_whatsapp_message, send_whatsapp_template
from llm.core.entity_extractor import extract_business_and_name

logger = logging.getLogger(__name__)

class OnboardingStep1(Action):
    def __init__(self, idioma):
        self.idioma = idioma

    def execute(self, memory, message: str, image: bytes = None):
        """
        Orquesta el flujo de la etapa 1 del onboarding
        Args:
            memory: Objeto Memory que contiene el estado de la conversación
            message: Mensaje de texto del usuario
            image: Imagen enviada por el usuario (no se usa, solo por compatibilidad con Action)
        Returns:
            Objeto Memory actualizado
        """
        try:
            logger.info("Iniciando etapa 1 del onboarding")
            memory = self._extraer_entidades(memory, message)
            nombre_emprendedor = memory.global_memory.datos_negocio.emprendedor.nombre
            nombre_negocio = memory.global_memory.datos_negocio.emprendedor.nombre_negocio
            giro = memory.global_memory.datos_negocio.negocio.giro
            ubicacion = memory.global_memory.datos_negocio.negocio.ubicacion
            logger.info(f"Nombre del emprendedor {nombre_emprendedor} & nombre del negocio {nombre_negocio}")
            logger.info(f"Giro del negocio {giro} & ubicacion {ubicacion}")

            if not nombre_negocio and nombre_emprendedor:
                # Falta nombre del negocio
                memory = self._pregunta_nombre_negocio(memory)

            elif nombre_negocio and not nombre_emprendedor:
                # Falta nombre del emprendedor
                memory = self._pregunta_nombre_emprendedor(memory)

            # elif nombre_emprendedor and nombre_negocio and not giro:
            #     # Falta el giro de la empresa
            #     memory = self._pregunta_giro(memory)

            elif nombre_emprendedor and nombre_negocio and giro and not ubicacion:
                # Falta la ubicacion de la empresa
                memory = self._pregunta_ubicacion(memory)

            elif not nombre_negocio and not nombre_emprendedor:
                memory = self._mensaje_inicial(memory)

            elif nombre_negocio and nombre_emprendedor and giro and ubicacion:
                # Envía mensaje de validación
                memory = self._final(memory)
                return self._reset_etapa1_state(memory)

        except Exception as e:
            logger.error(f"Error al ejecutar la etapa 1 del onboarding: {e}")
            send_whatsapp_message(memory.user_id, self.idioma.obtener("MENSAJE_ERROR_ETAPA1"))

        return memory

    def _extraer_entidades(self, memory, message: str):
        """
        Extrae el nombre del emprendedor y del negocio.
        """
        if message:
            datos_extraidos = extract_business_and_name(message)

            if datos_extraidos.nombre_negocio:
                memory.global_memory.datos_negocio.emprendedor.nombre_negocio = datos_extraidos.nombre_negocio
            
            if datos_extraidos.nombre:
                memory.global_memory.datos_negocio.emprendedor.nombre = datos_extraidos.nombre
            
            if datos_extraidos.giro:
                memory.global_memory.datos_negocio.negocio.giro = datos_extraidos.giro

            if datos_extraidos.ubicacion:
                memory.global_memory.datos_negocio.negocio.ubicacion = datos_extraidos.ubicacion

        return memory

    def _pregunta_nombre_negocio(self, memory):
        """
        Pregunta por el nombre del negocio. Solo si ya tenemos el nombre del emprendedor 
        y no el nombre del negocio
        """
        mensaje = self.idioma.obtener(
            "MENSAJE_FALTA_NEGOCIO_ETAPA1", 
            {'nombre': memory.global_memory.datos_negocio.emprendedor.nombre}
        )
        send_whatsapp_message(memory.user_id, mensaje)
        return self._add_aibo_message(memory, mensaje)

    def _pregunta_nombre_emprendedor(self, memory):
        """
        Pregunta por el nombre del emprendedor. Solo si ya tenemos el nombre del negocio
        y no el nombre del emprendedor
        """
        mensaje = self.idioma.obtener(
            "MENSAJE_FALTA_NOMBRE_ETAPA1", 
            {'empresa':memory.global_memory.datos_negocio.emprendedor.nombre_negocio}
        )
        send_whatsapp_message(memory.user_id, mensaje)
        return self._add_aibo_message(memory, mensaje)

    def _pregunta_giro(self, memory):
        """
        Pregunta por el giro del negocio. Solo si ya tenemos nombre del emprendedor y negocio
        """
        mensaje = self.idioma.obtener(
            "MENSAJE_VALIDACION_ETAPA1", 
            {
                'nombre':memory.global_memory.datos_negocio.emprendedor.nombre, 
                'empresa':memory.global_memory.datos_negocio.emprendedor.nombre_negocio
            }
        )
        send_whatsapp_message(memory.user_id, mensaje)
        return self._add_aibo_message(memory, mensaje)

    def _pregunta_ubicacion(self, memory):
        """
        Pregunta por la ubicación del negocio. Solo si ya tenemos el nombre del emprendedor, el negocio y el giro
        """
        mensaje = self.idioma.obtener(
            "MENSAJE_FALTA_UBICACION"
        )
        send_whatsapp_message(memory.user_id, mensaje)
        return self._add_aibo_message(memory, mensaje)

    def _final(self, memory):
        """
        Envia mensaje de validación final
        """
        mensaje = self.idioma.obtener("MENSAJE_FINAL_ONBOARDING")
        send_whatsapp_message(memory.user_id, mensaje)
        return self._add_aibo_message(memory, mensaje)

    def _mensaje_inicial(self, memory):
        bienvenida = self.idioma.obtener("MENSAJE_BIENVENIDA_ETAPA1")
        solicitud_info = self.idioma.obtener("MENSAJE_SOLICITUD_INFO_ETAPA1")

        mensaje = f"{bienvenida}\n\n{solicitud_info}"

        send_whatsapp_message(memory.user_id, mensaje)
        return self._add_aibo_message(memory, mensaje)

    def _reset_etapa1_state(self, memory):
        """
        Limpia el estado de la etapa 1 del onboarding
        """
        memory.local_state.change_status('menu', True)
        memory.local_state.etapa1.user_message = []
        memory.local_state.etapa1.aibo_message = []
        send_whatsapp_template(memory.user_id, self.idioma.obtener("MENU_INICIO_RAPIDO"))
        return memory
        
    def _add_aibo_message(self, memory, message):
        """
        Agrega los mensajes que se envían en nombre de AiBo
        """
        memory.local_state.etapa1.aibo_message.append(message)
        return memory