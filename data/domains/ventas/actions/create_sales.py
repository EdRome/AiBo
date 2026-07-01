import logging
from ..repository import crear_venta
from ..llm.extractor import get_sales_data, get_image_content
from config.utils import pick_random_number

logger = logging.getLogger(__name__)

class CreateSalesAction:

    def execute(self, memory, message: str, image: bytes = None, db_session=None, current_date=None):
        """
        Orquesta el flujo de creación de venta: extracción -> créditos -> DB -> notificación
        Args:
            memory: Objeto Memory que contiene el estado de la conversación
            message: Mensaje de texto del usuario
            image: Imagen enviada por el usuario
        Returns:
            Objeto Memory actualizado
        """
        logger.info("Iniciando CreateSalesAction...")
        venta_id = None
        total = None
        detalle = None
        return_obj = {}

        try:
            logger.info("2.1.1. Procesando información de venta...")
            if image:
                logger.info("2.1.2. Leyendo imagen")
                sales_data = self._process_sales_images(memory, image, current_date)
                total = sales_data.calcula_total()
                detalle = sales_data.output_detail()
                venta_id = [crear_venta(venta, db_session, current_date) for venta in sales_data.venta]

            else:
                logger.info("2.1.3. Leyendo texto")
                sales_data = self._process_sales_text(memory, message, current_date)
                total = sales_data.total
                detalle = sales_data.output_detail()
                venta_id = crear_venta(sales_data, db_session, current_date)

            if venta_id and detalle and total:
                num = pick_random_number()
                return_obj['mensaje'] = {'lista_detalle':detalle, 'total': str(total)}
                return_obj['transicion'] = f'confirmacion_registro_{str(num)}'
            else:
                logger.error(f"Falta información como venta_id, detalle y/o total")
                return_obj['transicion'] = 'error_registro'

        except Exception as e:
            logger.error(f"Error en CreateSalesAction: {e}")
            return_obj['transicion'] = 'error_registro'

        return_obj['memory'] = memory
        return_obj['action'] = 'venta'
        return return_obj

    def _process_sales_text(self, memory, message, current_date):
        logger.info("Procesando texto de venta...")
        # Extrae información de venta
        sales_data = get_sales_data(message, memory.user_id, current_date)

        return sales_data

    def _process_sales_images(self, memory, image, current_date):
        logger.info("Procesando imagen de venta...")
        sales_data = get_image_content(image, current_date)

        # Corrige teléfono
        for sale in sales_data.venta:
            sale.phone_number = memory.user_id

        return sales_data
