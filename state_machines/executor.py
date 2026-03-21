"""
Módulo centralizado para ejecutar máquinas de estados de manera consistente.
Maneja la sincronización entre el estado de la máquina y la memoria persistida.
"""
import logging
from typing import Optional
from data.models.memory.memory import Memory, LocalState, GenericResult
from data.db.memory import update_memory
from state_machines.Onboarding.Etapa1 import Etapa1
from state_machines.Menu.Menu import MenuMachine

logger = logging.getLogger(__name__)


class StateMachineExecutor:
    """Ejecutor centralizado para máquinas de estados."""
    
    @staticmethod
    def get_active_state(memory: Memory) -> Optional[str]:
        """
        Obtiene el nombre del estado activo en la memoria.
        
        Args:
            memory: Objeto Memory con el estado actual
            
        Returns:
            Nombre del estado activo o None si no hay ninguno
        """
        for state_name in memory.local_state.model_dump().keys():
            state_obj = getattr(memory.local_state, state_name)
            if state_obj.active:
                return state_name
        return 'menu'
    
    @staticmethod
    def sync_machine_state(machine, memory: Memory) -> None:
        """
        Sincroniza el estado de la máquina con el estado guardado en memoria.
        Como statemachine no permite establecer el estado directamente,
        ejecutamos las transiciones necesarias para llegar al estado correcto.
        
        Args:
            machine: Instancia de la máquina de estados
            memory: Objeto Memory con el estado persistido
        """
        active_state_name = StateMachineExecutor.get_active_state(memory)
        if not active_state_name:
            return
        
        # Si ya estamos en el estado correcto, no hacer nada
        if machine.current_state.id == active_state_name:
            return
        
        # Para Etapa1, ejecutar transiciones necesarias para llegar al estado
        # Esto es necesario porque statemachine no permite establecer el estado directamente
        if isinstance(machine, Etapa1):
            current_state_name = machine.current_state.id
            
            # Mapeo de rutas de transición posibles
            transition_paths = {
                ("receive_message", "welcome_message"): lambda: machine.to_welcome_message(),
                ("welcome_message", "ask_name"): lambda: machine.to_ask_name(),
                ("welcome_message", "ask_business_name"): lambda: machine.to_ask_business_name(),
                ("ask_name", "ask_business_name"): lambda: machine.to_ask_business_name(),
                ("ask_business_name", "validate_name_and_business"): lambda: machine.to_validation_response(),
            }
            
            # Intentar transición directa
            transition_key = (current_state_name, active_state_name)
            if transition_key in transition_paths:
                try:
                    transition_paths[transition_key]()
                    logger.info(f"Sincronizado estado de máquina de {current_state_name} a {active_state_name}")
                except Exception as e:
                    logger.warning(f"No se pudo sincronizar estado: {e}")
            else:
                logger.warning(f"No hay ruta de transición directa de {current_state_name} a {active_state_name}")
    
    @staticmethod
    def update_memory_state(memory: Memory, new_state_name: str) -> None:
        """
        Actualiza el estado activo en la memoria.
        
        Args:
            memory: Objeto Memory a actualizar
            new_state_name: Nombre del nuevo estado activo
        """
        # Desactivar todos los estados
        for state_name in memory.local_state.model_dump().keys():
            state_obj = getattr(memory.local_state, state_name)
            state_obj.active = False
        
        # Activar el nuevo estado
        if hasattr(memory.local_state, new_state_name):
            new_state_obj = getattr(memory.local_state, new_state_name)
            new_state_obj.active = True
            logger.info(f"Estado activo actualizado a: {new_state_name}")
    
    @staticmethod
    def process_user_message(memory: Memory, message: str) -> Memory:
        """
        Procesa un mensaje del usuario en el contexto de la máquina de estados.
        
        Args:
            memory: Objeto Memory con el estado actual
            message: Mensaje del usuario
            
        Returns:
            Memory actualizada
        """
        active_state = StateMachineExecutor.get_active_state(memory)
        if not active_state:
            logger.warning("No hay estado activo para procesar el mensaje")
            return memory
        
        # Agregar mensaje al estado activo
        state_obj = getattr(memory.local_state, active_state)
        state_obj.user_message.append(message)
        # state_obj.user_message.append(message)
        
        return memory
    
    @staticmethod
    def process_machine_message(memory: Memory, message: str) -> Memory:
        """
        Procesa un mensaje de la máquina de estados.

        Args:
            memory: Objeto Memory con el estado actual
            message: Mensaje de la máquina de estados
            
        Returns:
            Memory actualizada
        """
        active_state = StateMachineExecutor.get_active_state(memory)
        if not active_state:
            logger.warning("No hay estado activo para procesar el mensaje")
            return memory
        
        # Agregar mensaje al estado activo
        state_obj = getattr(memory.local_state, active_state)
        state_obj.aibo_message.append(message)
        
        return memory

    @staticmethod
    def execute_state_machine(memory: Memory, mode: str = "process") -> Memory:
        """
        Ejecuta la máquina de estados según el contexto activo.
        """
        if memory.active_context == "Etapa1":
            return StateMachineExecutor._execute_etapa1(memory, mode)
        elif memory.active_context == "Menu":
            return StateMachineExecutor._execute_menu(memory, mode)
        elif memory.active_context == "ventas":
            return StateMachineExecutor._execute_sales(memory, mode)
        elif memory.active_context == "inventario":
            return StateMachineExecutor._execute_inventory(memory, mode)
        else:
            logger.warning(f"Contexto desconocido: {memory.active_context}")
            return memory

    @staticmethod
    def _execute_menu(memory: Memory, mode: str) -> Memory:
        machine = MenuMachine(memory)
        # Menu simple: always waiting selection.
        # Process user msg
        if hasattr(memory.local_state.menu, 'user_message'):
            # This relies on LocalState menu having user_message which GenericResult does
            for msg in memory.local_state.menu.user_message:
                machine.waiting_waiting_selection(msg)
            
            # Clear processed messages? 
            # Usually we don't clear default GenericResult but since we don't hold state, maybe we should?
            # actually executor process_user_message appends to list.
            # We should probably clear it after processing to avoid re-processing?
            # Etapa1 doesn't seem to clear. Loops over them.
            # If we don't clear, we process old messages forever.
            # Fix: clear buffer after processing.
            memory.local_state.menu.user_message = []
            
        next_ctx = machine.get_next_context()
        if next_ctx:
            memory.active_context = next_ctx
            # Reset/Init target context state?
            StateMachineExecutor._init_context_state(memory, next_ctx)
            
        StateMachineExecutor.persist_memory(memory)
        return memory

    @staticmethod
    def _init_context_state(memory: Memory, context: str):
        """Helper to initialize state when entering a new context"""
        if context == "Menu":
            memory.local_state.menu.active = True
            # Menu has no complex state to reset usually
        elif context == "ventas":
            memory.local_state.ventas.active = True
            memory.local_state.ventas.step = "waiting_product" # Reset
            memory.local_state.ventas.product = None
            memory.local_state.ventas.quantity = None
            # Trigger initial message for Sales?
            # Machine.on_enter_waiting_product checks if message sent.
            # We can run machine once with empty message to trigger entry?
            # Or assume next loop handles it?
            # Better: Run "on_enter" logic now.
            SalesMachine(memory).on_enter_waiting_product()
            
        elif context == "inventario":
            memory.local_state.inventario.active = True
            memory.local_state.inventario.step = "waiting_product"
            memory.local_state.inventario.product = None
            memory.local_state.inventario.stock = None
            InventoryMachine(memory).on_enter_waiting_product()

    
    @staticmethod
    def _execute_etapa1(memory: Memory, mode: str) -> Memory:
        """
        Ejecuta la máquina de estados Etapa1.
        
        Args:
            memory: Objeto Memory con el estado actual
            mode: Modo de ejecución ("process" o "advance")
            
        Returns:
            Memory actualizada
        """
        # Crear instancia de la máquina de estados
        etapa1 = Etapa1(memory.user_id, memory)
        
        # Sincronizar estado de la máquina con la memoria
        # StateMachineExecutor.sync_machine_state(etapa1, memory)
        
        # active_state = StateMachineExecutor.get_active_state(memory)
        # if not active_state:
        #     logger.warning("No hay estado activo en Etapa1")
        #     return memory
        
        # logger.info(f"Ejecutando Etapa1 en modo '{mode}' para estado: {active_state}")
        
        # if mode == "process":
        #     # Procesar mensajes del usuario
        #     state_obj = getattr(memory.local_state, active_state)
        #     for message in state_obj.user_message:
        #         waiting_method = getattr(etapa1, f"waiting_{active_state}", None)
        #         if waiting_method:
        #             waiting_method(message=message)
        #         else:
        #             logger.warning(f"No se encontró método waiting_{active_state}")
            
        #     # Después de procesar mensajes, verificar si hay transiciones automáticas
        #     # que deban ejecutarse basándose en las condiciones actuales
        #     try:
        #         # Transición automática desde receive_message
        #         if active_state == "receive_message" and etapa1.current_state.name == "receive_message":
        #             etapa1.to_welcome_message()
        #             logger.info(f"Transición automática de receive_message a welcome_message")
                
        #         # Después de procesar, verificar si podemos avanzar desde el estado actual
        #         # Esto permite transiciones automáticas cuando se cumplen las condiciones
        #         current_after_process = etapa1.current_state.name
        #         next_auto_state = StateMachineExecutor._determine_next_state(etapa1, current_after_process)
                
        #         if next_auto_state:
        #             transition_method = getattr(etapa1, f"to_{next_auto_state}", None)
        #             if transition_method:
        #                 transition_method()
        #                 logger.info(f"Transición automática después de procesar mensajes: {current_after_process} -> {next_auto_state}")
        #     except Exception as e:
        #         logger.warning(f"No se pudo ejecutar transición automática: {e}")
        
        # elif mode == "advance":
        #     # Determinar y ejecutar el siguiente estado
        #     next_state = StateMachineExecutor._determine_next_state(etapa1, active_state)
            
        #     if next_state:
        #         transition_method = getattr(etapa1, f"to_{next_state}", None)
        #         if transition_method:
        #             try:
        #                 # Ejecutar la transición
        #                 transition_method()
        #                 logger.info(f"Transición ejecutada hacia {next_state}")
        #             except Exception as e:
        #                 logger.error(f"Error en transición a {next_state}: {e}")
        #         else:
        #             logger.warning(f"No se encontró método to_{next_state}")
        #     else:
        #         logger.info(f"No hay siguiente estado desde {active_state}, permaneciendo en el mismo estado")
        
        # # Detectar cambio de estado y actualizar memoria
        # final_state = etapa1.current_state.name
        # if final_state != active_state:
        #     # El estado cambió, actualizar memoria
        #     StateMachineExecutor.update_memory_state(memory, final_state)
        #     logger.info(f"Estado actualizado en memoria: {active_state} -> {final_state}")
        
        # # Actualizar datos_negocio en memoria global (puede haber cambiado durante la ejecución)
        # memory.global_memory.datos_negocio = etapa1.datos_negocio
        
        # Persistir cambios en la base de datos
        StateMachineExecutor.persist_memory(etapa1.memory)
        
        return etapa1.memory
    
    @staticmethod
    def _determine_next_state(machine, current_state: str) -> Optional[str]:
        """
        Determina el siguiente estado basado en las condiciones de la máquina.
        Usa la API de statemachine para obtener transiciones posibles.
        
        Args:
            machine: Instancia de la máquina de estados
            current_state: Estado actual
            
        Returns:
            Nombre del siguiente estado o None si debe permanecer en el actual
        """
        # Obtener el estado actual de la máquina
        current_state_obj = getattr(machine, current_state, None)
        if not current_state_obj:
            return None
        
        # Obtener todas las transiciones posibles desde el estado actual
        # La biblioteca statemachine expone las transiciones en el objeto State
        try:
            # Obtener transiciones disponibles desde el estado actual
            available_transitions = []
            
            # Para Etapa1, mapear lógicamente las transiciones posibles
            if isinstance(machine, Etapa1):
                if current_state == "receive_message":
                    # Siempre puede transicionar a welcome_message
                    return "welcome_message"
                
                elif current_state == "welcome_message":
                    # Extraer entidades primero para evaluar condiciones
                    machine.datos_negocio = machine.extract_business_and_name()
                    
                    # Evaluar qué transición es apropiada
                    if machine.falta_nombre() and not machine.falta_nombre_negocio():
                        return "ask_name"
                    elif not machine.falta_nombre() and machine.falta_nombre_negocio():
                        return "ask_business_name"
                    # Si faltan ambos, permanece en welcome_message (waiting)
                    return None
                
                elif current_state == "ask_name":
                    # Extraer entidades primero
                    machine.datos_negocio = machine.extract_business_and_name()
                    
                    # Si ya tiene nombre, puede avanzar
                    if not machine.falta_nombre():
                        return "ask_business_name"
                    return None
                
                elif current_state == "ask_business_name":
                    # Extraer entidades primero
                    machine.datos_negocio = machine.extract_business_and_name()
                    
                    # Si tiene ambos datos, puede avanzar
                    if not machine.falta_nombre() and not machine.falta_nombre_negocio():
                        return "validate_name_and_business"
                    return None
                
                elif current_state == "validate_name_and_business":
                    # Estado final, no hay más transiciones
                    return None
            
        except Exception as e:
            logger.error(f"Error al determinar siguiente estado: {e}")
            return None
        
        return None
    
    @staticmethod
    def persist_memory(memory: Memory) -> None:
        """
        Persiste la memoria en la base de datos.
        
        Args:
            memory: Objeto Memory a persistir
        """
        update_memory(
            memory.user_id,
            memory.active_context,
            memory.machine_stack,
            memory.global_memory.model_dump(),
            memory.local_state.model_dump(),
            memory.last_interaction,
            memory.task_name,
            memory.creditos_disponibles
        )
        logger.info("Memoria persistida en base de datos")

