import json
import logging
from interfaces.action import Action
from data.db.sales import crear_venta
from llm.core.sales_extractor import get_sales_data
from llm.core.ocr import ocr_v1
from whatsapp.send_message.send_message import send_whatsapp_message, send_whatsapp_template

logger = logging.getLogger(__name__)

class CreateSalesAction(Action):
    def __init__(self, idioma):
        self.idioma = idioma

    def execute(self, memory, message: str, image: bytes = None):
        """
        Orquesta el flujo de creación de venta: extracción -> créditos -> DB -> notificación
        Args:
            memory: Objeto Memory que contiene el estado de la conversación
            message: Mensaje de texto del usuario
            image: Imagen enviada por el usuario
        Returns:
            Objeto Memory actualizado
        """
        logger.info("2.1. Iniciando CreateSalesAction...")
        venta_id = None
        total = None
        detalle = None

        try:
            if memory.local_state.ventas.procesar_venta:
                logger.info("2.1.1. Procesando información de venta...")
                if image:
                    logger.info("2.1.2. Leyendo imagen")
                    sales_data = self._process_sales_images(memory, image)
                    total = sales_data.calcula_total()
                    detalle = sales_data.output_detail()
                    venta_id = [crear_venta(venta) for venta in sales_data.venta]

                else:
                    logger.info("2.1.3. Leyendo texto")
                    sales_data = self._process_sales_text(memory, message)
                    total = sales_data.total
                    detalle = sales_data.output_detail()
                    venta_id = crear_venta(sales_data)

                if venta_id and detalle and total:
                    self._send_success_notification(memory, venta_id, detalle, total)
                else:
                    logger.error(f"Falta información como venta_id, detalle y/o total")
                    send_whatsapp_message(memory.user_id, self.idioma.obtener('MENSAJE_ERROR_REGISTRO_VENTA'))

        except Exception as e:
            logger.error(f"Error en CreateSalesAction: {e}")
            send_whatsapp_message(memory.user_id, self.idioma.obtener('MENSAJE_ERROR_REGISTRO_VENTA'))

        # Limpieza de estado y retorno al menú
        return self._reset_sales_state(memory)

    def _process_sales_text(self, memory, message):
        logger.info("2.1.3.1. Procesando texto de venta...")
        # Extrae información de venta
        sales_data = get_sales_data(message, memory.user_id)

        num_ventas = len(sales_data.detalles)
        memory.restar_credito(num_ventas)

        return sales_data

    def _process_sales_images(self, memory, image):
        logger.info("2.1.2.1. Procesando imagen de venta...")
        sales_data = ocr_v1(image)

        # Cálculo de créditos para procesamiento de imagen
        num_ventas = sum(len(sale.detalles) for sale in sales_data.venta)
        memory.restar_credito(num_ventas)

        # Corrige teléfono
        for sale in sales_data.venta:
            sale.phone_number = memory.user_id

        return sales_data
    
    def _send_success_notification(self, memory, venta_id, detalle, total):
        logger.info(f"2.1.4. Venta registrada con éxito. Detalle: {detalle}")

        # Almacenamos el ID de la última venta para posibles borrados posteriores
        memory.local_state.ventas.id_ultima_venta = venta_id[-1] if isinstance(venta_id, list) else venta_id

        send_whatsapp_template(
            memory.user_id,
            self.idioma.obtener("MENSAJE_CONFIRMACION_VENTA"),
            json.dumps({'lista_detalle': detalle, 'total': str(total)})
        )

    def _reset_sales_state(self, memory):
        """Devuelve al usuario al estado de menú y limpia buffers"""
        logger.info("2.1.5. Reiniciando buffers")
        memory.local_state.change_status('menu', True)
        memory.local_state.ventas.procesar_venta = False
        memory.local_state.ventas.user_message = []
        memory.local_state.ventas.aibo_message = []
        memory.local_state.ventas.step = "waiting_product"
        return memory