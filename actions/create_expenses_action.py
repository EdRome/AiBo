import json
import logging
from interfaces.action import Action
from data.db.expenses import crear_gasto
from llm.core.expenses_extractor import get_expenses_data
from llm.core.ocr import ocr_v1
from whatsapp.send_message.send_message import send_whatsapp_message, send_whatsapp_template

logger = logging.getLogger(__name__)

class CreateExpensesAction(Action):
    def __init__(self, idioma):
        self.idioma = idioma

    def execute(self, memory, message: str, image: bytes = None):
        """
        Orquesta el flujo de creación de gasto: extracción -> créditos -> DB -> notificación
        Args:
            memory: Objeto Memory que contiene el estado de la conversación
            message: Mensaje de texto del usuario7y_
            image: Imagen enviada por el usuari—:.-o
        Returns:
            Objeto Memory actualizado
        """
        logger.info("2.1. Iniciando CreateExpensesAction...")
        gasto_id = None
        total = None
        detalle = None

        try:
            if memory.local_state.gastos.procesar_gasto:
                logger.info("2.1.1. Procesando información de gasto...")
                if image:
                    logger.info("2.1.2. Leyendo imagen")
                    expenses_data = self._process_expenses_images(memory, image)
                    total = expenses_data.calcula_total()
                    detalle = expenses_data.output_detail()
                    gasto_id = [crear_gasto(gasto) for gasto in expenses_data.gasto]

                else:
                    logger.info("2.1.3. Leyendo texto")
                    expenses_data = self._process_expenses_text(memory, message)
                    total = expenses_data.total
                    detalle = expenses_data.output_detail()
                    gasto_id = crear_gasto(expenses_data)

                if gasto_id and detalle and total:
                    self._send_success_notification(memory, gasto_id, detalle, total)
                    # Limpieza de estado y retorno al menú
                    return self._reset_expenses_state(memory)
                else:
                    logger.error(f"Falta información como gasto_id, detalle y/o total")
                    send_whatsapp_message(memory.user_id, self.idioma.obtener('MENSAJE_ERROR_REGISTRO_GASTO'))

        except Exception as e:
            logger.error(f"Error en CreateExpensesAction: {e}")
            send_whatsapp_message(memory.user_id, self.idioma.obtener('MENSAJE_ERROR_REGISTRO_GASTO'))

        return memory

    def _process_expenses_text(self, memory, message):
        logger.info("2.1.3.1. Procesando texto de gasto...")
        # Extrae información de gasto
        expenses_data = get_expenses_data(message, memory.user_id)

        num_gastos = len(expenses_data.detalles)
        memory.restar_credito(num_gastos)

        return expenses_data

    def _process_expenses_images(self, memory, image):
        logger.info("2.1.2.1. Procesando imagen de gasto...")
        expenses_data = ocr_v1(image)

        # Cálculo de créditos para procesamiento de imagen
        num_gastos = sum(len(expense.detalles) for expense in expenses_data.gasto)
        memory.restar_credito(num_gastos)

        # Corrige teléfono
        for expense in expenses_data.gasto:
            expense.phone_number = memory.user_id

        return expenses_data
    
    def _send_success_notification(self, memory, gasto_id, detalle, total):
        logger.info(f"2.1.4. Gasto registrado con éxito. Detalle: {detalle}")

        # Almacenamos el ID del último gasto para posibles borrados posteriores
        memory.local_state.gastos.id_ultimo_gasto = gasto_id[-1] if isinstance(gasto_id, list) else gasto_id

        send_whatsapp_template(
            memory.user_id,
            self.idioma.obtener("MENSAJE_CONFIRMACION_GASTO"),
            json.dumps({'lista_detalle': detalle, 'total': str(total)})
        )

    def _reset_expenses_state(self, memory):
        """Devuelve al usuario al estado de menú y limpia buffers"""
        logger.info("2.1.5. Reiniciando buffers")
        memory.local_state.change_status('menu', True)
        memory.local_state.gastos.procesar_gasto = False
        memory.local_state.gastos.user_message = []
        memory.local_state.gastos.aibo_message = []
        memory.local_state.gastos.step = "waiting_product"
        return memory