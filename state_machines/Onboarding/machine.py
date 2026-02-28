import logging
from state_machines.executor import StateMachineExecutor
from state_machines.Onboarding.Etapa1 import Etapa1
from state_machines.Onboarding.Etapa2 import Etapa2
from state_machines.Onboarding.Etapa3 import Etapa3
from state_machines.Onboarding.Etapa4 import Etapa4
from data.models.memory.memory import Memory

logger = logging.getLogger(__name__)

def onboarding_machine(memory: Memory, active_state: str):
    # Ejecutar máquina de estados en modo "advance" para avanzar al siguiente estado
    # memory = StateMachineExecutor.execute_state_machine(memory, mode="advance")
    full_message = "\n".join(getattr(memory.local_state, active_state).user_message)

    # --- ETAPA 1 ---
    if active_state == "etapa1":
        etapa1 = Etapa1.from_dict(memory, active_state, full_message)
        if "Para ponerme en contexto, ¿me podrías contar en pocas palabras" in etapa1.ultimo_mensaje_enviado:
            memory.local_state.etapa1.active = False
            memory.local_state.etapa2.active = True
        memory = StateMachineExecutor.process_machine_message(memory, etapa1.ultimo_mensaje_enviado)
    
    # --- ETAPA 2 ---
    elif active_state == "etapa2":
        memory.active_context = "Etapa2"
        if full_message == "":
            full_message = memory.local_state.etapa1.user_message[-1]

        etapa2 = Etapa2.from_memory(memory, full_message)
        if "Veo que tienes varias cosas en mente:" in etapa2.ultimo_mensaje_enviado:
            memory.local_state.etapa2.active = False
            memory.local_state.etapa3.active = True

        memory = StateMachineExecutor.process_machine_message(memory, etapa2.ultimo_mensaje_enviado)
    
    # --- ETAPA 3 ---
    elif active_state == "etapa3":
        memory.active_context = "Etapa3"
        if full_message == "":
            full_message = memory.local_state.etapa2.user_message[-1]
            logger.info(f"full_message para etapa 3: {full_message}")

        etapa3 = Etapa3.from_memory(memory, full_message)
        if "Tu respuesta es muy valiosa. Una última pregunta para entender la raíz" in etapa3.ultimo_mensaje_enviado:
            memory.local_state.etapa3.active = False
            memory.local_state.etapa4.active = True

        memory = StateMachineExecutor.process_machine_message(memory, etapa3.ultimo_mensaje_enviado)
    
    # --- ETAPA 4 ---
    elif active_state == "etapa4":
        memory.active_context = "Etapa4"
        if full_message == "":
            full_message = memory.local_state.etapa3.user_message[-1]

        etapa4 = Etapa4.from_memory(memory, full_message)
        if "Perfecto. Con lo que hemos hablado, tengo una idea clara." in etapa4.ultimo_mensaje_enviado:
            memory.local_state.etapa4.active = False

        memory = StateMachineExecutor.process_machine_message(memory, etapa4.ultimo_mensaje_enviado)
    
    StateMachineExecutor.persist_memory(memory)