import json
import logging
import requests

from typing import Optional
from requests.auth import HTTPBasicAuth

from data.models.memory.memory import Memory
from whatsapp.send_message.send_message import send_whatsapp_message, send_whatsapp_template
from llm.core.entity_extractor import get_intention, confirm_delete
from llm.core.sales_extractor import get_sales_data, get_image_content
from llm.core.ocr import ocr_v1
from whatsapp.messages.multiidioma import MultiIdioma
from data.db.sales import crear_venta, borrar_venta

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class MenuMachine():
    
    def __init__(self, memory: Memory, message: str, idioma: MultiIdioma = None, image: bytes = None):
        self.memory = memory
        self.user_message = message
        self.image = image
        self.idioma = idioma if idioma else MultiIdioma(memory.global_memory.language)

    def on_enter_inventario(self):
        send_whatsapp_message(
            self.memory.user_id,
            self.idioma.obtener('MENSAJE_FUNCIONALIDAD_FALTANTE')
        )
        send_whatsapp_template(
            self.memory.user_id,
            self.idioma.obtener('MENU_INICIO_RAPIDO')
        )
        self.memory.local_state.change_status('menu', True)

    def on_enter_otras_acciones(self):
        send_whatsapp_message(
            self.memory.user_id,
            self.idioma.obtener("MENSAJE_FUNCIONALIDAD_FALTANTE")
        )
        send_whatsapp_template(
            self.memory.user_id,
            self.idioma.obtener("MENU_INICIO_RAPIDO")
        )
        self.memory.local_state.change_status('menu', True)

    def on_enter_venta(self):
        # Entra al estado de inicio de venta y envía mensaje de confirmación
        mensaje = self.idioma.obtener("MENSAJE_INICIO_VENTA")
        send_whatsapp_template(
            self.memory.user_id,
            mensaje
        )
        self.memory.local_state.ventas.aibo_message.append(mensaje)
        self.memory.local_state.change_status('ventas', True) # Activa el estado "ventas"
        self.memory.local_state.ventas.procesar_venta = True # Activa el siguiente estado "procesar_venta"

    def _process_sales_text(self):
        logger.error("Procesando mensaje...")
        # Extrae información de venta
        sales_data = get_sales_data(self.user_message, self.memory.user_id)

        num_ventas = len(sales_data.detalles)
        logger.error(f'Número de ventas: {num_ventas}')
        self.memory.restar_credito(num_ventas)
        logger.error(f'Creditos restantes: {self.memory.creditos_disponibles}')

        return sales_data

    def _process_sales_images(self):
        logger.error("Procesando imagen...")
        sales_data = ocr_v1(self.image)

        num_ventas = sum(len(sale.detalles) for sale in sales_data.venta)
        logger.error(f'Número de ventas: {num_ventas}')
        self.memory.restar_credito(num_ventas)
        logger.error(f'Creditos restantes: {self.memory.creditos_disponibles}')

        # Corrige teléfono
        for sale in sales_data.venta:
            sale.phone_number = self.memory.user_id

        return sales_data

    def process_sales_message(self):
        venta_id = None
        total = None
        detalle = None

        if self.image:
            sales_data = self._process_sales_images()
            venta_id = [crear_venta(venta) for venta in sales_data.venta]
            total = sales_data.calcula_total()
            detalle = sales_data.output_detail()
        else:
            sales_data = self._process_sales_text()
            # Crea registro de venta en BD
            venta_id = crear_venta(sales_data)
            detalle = sales_data.output_detail()
            total = sales_data.total
        
        if venta_id and detalle and total:
            # Envía mensaje de confirmación
            logger.error(f"Detalle: {detalle}")
            logger.error(f"Total: {total}")
            send_whatsapp_template(
                self.memory.user_id, 
                self.idioma.obtener("MENSAJE_CONFIRMACION_VENTA"),
                json.dumps({'lista_detalle': detalle,'total': str(total)})
            )
            self.memory.local_state.ventas.id_ultima_venta = venta_id[-1] if isinstance(venta_id, list) else venta_id
        else:
            send_whatsapp_message(self.memory.user_id, self.idioma.obtener('MENSAJE_ERROR_REGISTRO_VENTA'))

        self.memory.local_state.change_status('menu', True) # Si ocurre un error, vuelve al estado "menu"
        self.memory.local_state.ventas.procesar_venta = False # Desactiva el estado "procesar_venta"
        self.memory.local_state.ventas.user_message = []

    def on_enter_borrar_venta(self):
        self.memory.local_state.change_status('ventas', True)
        self.memory.local_state.ventas.borrar_venta = True
        mensaje = self.idioma.obtener("MENSAJE_CONFIRMACION_BORRAR_VENTA")
        send_whatsapp_template(self.memory.user_id, mensaje)

    def process_borrar_venta_message(self):
        if confirm_delete(self.memory.local_state.ventas.user_message[-1]):
            borrado = borrar_venta(self.memory.local_state.ventas.id_ultima_venta, self.memory.user_id)
            if borrado:
                send_whatsapp_message(self.memory.user_id, self.idioma.obtener('MENSAJE_VENTA_BORRADA_CORRECTAMENTE'))
            else:
                send_whatsapp_message(self.memory.user_id, self.idioma.obtener('MENSAJE_ERROR_REGISTRO_VENTA'))

        self.memory.local_state.change_status('menu', True)
        self.memory.local_state.ventas.borrar_venta = False
        self.memory.local_state.ventas.user_message = []
        send_whatsapp_template(self.memory.user_id, self.idioma.obtener("MENU_INICIO_RAPIDO"))

    def process_inventory_message(self):
        pass

    @classmethod
    def from_memory(cls, memory: Memory, active_state: str, message: str = None, image: bytes = None):
        logger.error("Entrando a Menu")
        maquina = cls(
            memory=memory,
            message=message,
            image=image
        )

        logger.error(f"Estado activo: {active_state}")
        maquina.memory.local_state.menu.user_message = []
        if (active_state and active_state == 'menu') or not active_state:
            logger.error("Validando intención del usuario")
            intention = get_intention(message)
            # maquina.memory.local_state.menu.llm_response += intention + "\n"
            logger.error(f"Intención del usuario: {intention}")

            if intention == 'registrar_venta':
                maquina.memory.local_state.change_status('ventas', True)
                maquina.on_enter_venta()

            elif intention == 'registrar_inventario':
                # maquina.memory.local_state.change_status('inventario', True)
                maquina.on_enter_inventario()

            elif intention == 'borrar_venta':
                maquina.memory.local_state.change_status('ventas', True)
                maquina.on_enter_borrar_venta()

            elif intention == 'borrar_inventario':
                maquina.memory.local_state.change_status('inventario', True)
                # maquina.on_enter_borrar_inventario()

            elif intention == 'menu':
                send_whatsapp_template(maquina.memory.user_id, maquina.idioma.obtener("MENU_INICIO_RAPIDO"))

            elif intention == 'otras_acciones':
                maquina.on_enter_otras_acciones()

        elif active_state and active_state == 'ventas':
            if maquina.memory.local_state.ventas.procesar_venta:
                logger.error("Procesando mensaje de venta")
                maquina.process_sales_message()
            elif maquina.memory.local_state.ventas.borrar_venta:
                logger.error("Procesando mensaje de borrar venta")
                maquina.process_borrar_venta_message()

        elif active_state and active_state == 'inventario':
            logger.error("Procesando mensaje de inventario")
            maquina.process_inventory_message()

        return maquina