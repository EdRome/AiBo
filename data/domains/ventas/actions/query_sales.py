import logging
from core.services.whatsapp import send_translated_message
from ..repository import get_sales_summary
from ..llm.extractor import get_sales_query


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class QuerySalesAction:

    def execute(self, memory, message: str, image = None, db_session=None, current_date=None):
        return_obj = {}
        try:
            sales_query = get_sales_query(message, current_date)
            if sales_query['start_date'] == '1900-12-31' and sales_query['end_date'] == '1900-12-31':
                raise Exception("Error en la consulta de ventas")
            resultado_db = get_sales_summary(
                start_date=sales_query["start_date"],
                end_date=sales_query["end_date"],
                group_by=sales_query["group_by"],
                phone_number=memory.user_id,
                db_session=db_session
            )

            if resultado_db != {}:
                return_obj['mensaje'] = resultado_db
                return_obj['transicion'] = "confirmacion_consulta" if resultado_db["cantidad_transacciones"] > 0 else "cero_consulta"
            else:
                return_obj['transicion'] = "error_consulta"
        except Exception as e:
            logger.error(f"Error en QuerySalesAction: {str(e)}")
            return_obj['transicion'] = "error_consulta"

        return_obj['memory'] = memory
        return return_obj