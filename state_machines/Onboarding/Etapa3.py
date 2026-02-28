import logging
from statemachine import StateMachine, State
from typing import Optional
from datetime import datetime, timezone
from data.models.memory.memory import Memory
from llm.core.phrase_analyzer import main_pain_analyzer, affection_analyzer
from llm.core.summary_creator import create_affection_summary
from whatsapp.send_message.send_message import send_whatsapp_message

logger = logging.getLogger(__name__)

class Etapa3(StateMachine):
    """
    ETAPA 3: DESCUBRIMIENTO DE PUNTOS DE DOLOR ESPECÍFICOS 
    """

    mensaje_inicio = """Entiendo. Que {punto_de_dolor} sea un desafío debe ser frustrante. Déjame hacerte una pregunta más específica sobre eso:

**"Cuando {punto_de_dolor}, ¿cómo afecta eso tu día a día o tus planes de crecimiento?"** (Por ejemplo: ¿te hace dedicar mucho tiempo a buscar clientes en lugar de atenderlos?, ¿te impide lanzar un nuevo producto?)."""

    mensaje_profundizacion_tiempo = """Parece que el tiempo es un recurso clave. ¿Sientes que pierdes muchas horas en cosas que podrían hacerse más rápido o solas?"""
    mensaje_profundizacion_incertidumbre = """Esa falta de claridad para planear, ¿te ha hecho perder oportunidades o tomar decisiones con mucha duda?"""
    mensaje_profundizacion_dinero = """¿Este tema ha hecho que los ingresos sean muy variables mes a mes, o que sea difícil saber cuánto vas a ganar?"""

    mensaje_pregunta_causa_raiz = """Tu respuesta es muy valiosa. Una última pregunta para entender la raíz:

**En tu experiencia, ¿qué crees que es la principal razón por la que {punto_de_dolor} sigue pasando?** (Ej.: ¿es falta de herramientas, de conocimiento sobre cómo hacerlo, de tiempo para implementar cambios?)."""

    # --- ESTADOS ---
    inicio = State(initial=True)
    profundizando_tiempo = State()
    profundizando_incertidumbre = State()
    profundizando_dinero = State()
    esperando_causa_raiz = State()
    final = State(final=True)

    # Transiciones
    a_profundizar_tiempo = inicio.to(profundizando_tiempo)
    a_profundizar_incertidumbre = inicio.to(profundizando_incertidumbre)
    a_profundizar_dinero = inicio.to(profundizando_dinero)
    a_esperando_causa_raiz = (profundizando_tiempo.to(esperando_causa_raiz) | profundizando_incertidumbre.to(esperando_causa_raiz) | profundizando_dinero.to(esperando_causa_raiz) | inicio.to(esperando_causa_raiz))
    finalizar = (profundizando_tiempo.to(final) | profundizando_incertidumbre.to(final) | profundizando_dinero.to(final) | esperando_causa_raiz.to(final))

    def __init__(self, memory: Memory, mensaje_usuario: Optional[str] = None):
        self.memory = memory
        self.mensaje_usuario = mensaje_usuario or ""

        self.respuesta_afectacion = ""
        self.respuesta_causa_raiz = ""
        self.ultimo_mensaje_enviado = ""
        
        super().__init__()

    def on_enter_inicio(self):
        """Comienza la etapa 3 - pregunta sobre afectación"""
        logger.info(f"Entrando en on_enter_inicio de Etapa3")
        if not self.mensaje_usuario:
            return
        
        if not self.memory.local_state.etapa3.aibo_message:
            analisis = main_pain_analyzer(self.mensaje_usuario)
            self.memory.global_memory.datos_negocio.needs.pain_point = analisis
            mensaje = self.mensaje_inicio.format(punto_de_dolor=self.memory.global_memory.datos_negocio.needs.punto_de_dolor)

            send_whatsapp_message(self.memory.user_id, mensaje)
            self.ultimo_mensaje_enviado = mensaje

    def on_enter_profundizando_tiempo(self):
        mensaje = self.mensaje_profundizacion_tiempo
        send_whatsapp_message(self.memory.user_id, mensaje)
        self.ultimo_mensaje_enviado = mensaje

    def on_enter_profundizando_incertidumbre(self):
        mensaje = self.mensaje_profundizacion_incertidumbre
        send_whatsapp_message(self.memory.user_id, mensaje)
        self.ultimo_mensaje_enviado = mensaje

    def on_enter_profundizando_dinero(self):
        mensaje = self.mensaje_profundizacion_dinero
        send_whatsapp_message(self.memory.user_id, mensaje)
        self.ultimo_mensaje_enviado = mensaje

    def on_enter_esperando_causa_raiz(self):
        mensaje = self.mensaje_pregunta_causa_raiz.format(punto_de_dolor=self.memory.global_memory.datos_negocio.needs.punto_de_dolor)
        send_whatsapp_message(self.memory.user_id, mensaje)
        self.ultimo_mensaje_enviado = mensaje

    def _procesar_respuesta_afectacion(self):
        if not self.mensaje_usuario:
            return

        analisis = affection_analyzer(self.mensaje_usuario)

        self.memory.global_memory.datos_negocio.needs.pain_point.tiempo = analisis.tiempo
        self.memory.global_memory.datos_negocio.needs.pain_point.incertidumbre = analisis.incertidumbre
        self.memory.global_memory.datos_negocio.needs.pain_point.dinero = analisis.dinero

        if analisis.tiempo:
            self.a_profundizar_tiempo()
        elif analisis.incertidumbre:
            self.a_profundizar_incertidumbre()
        elif analisis.dinero:
            self.a_profundizar_dinero()

    def _procesar_respuesta_profundizacion(self):
        if not self.mensaje_usuario:
            return

        analisis = create_affection_summary(self.mensaje_usuario)

        self.memory.global_memory.datos_negocio.needs.pain_point.afectacion = analisis.afectacion

        self.a_esperando_causa_raiz()

    def _actualizar_memoria_local(self, estado: str, aibo_msg: str = "", llm_response: str = ""):
        """Actualiza la memoria local con la interacción actual"""
        # Actualizar el estado activo
        self.memory.local_state.etapa1.active = False
        self.memory.local_state.etapa2.active = False
        self.memory.local_state.etapa3.active = True
        self.memory.local_state.etapa4.active = False
        
        # Guardar mensajes
        if aibo_msg:
            self.memory.local_state.etapa3.aibo_message.append(aibo_msg)
        
        if self.mensaje_usuario:
            self.memory.local_state.etapa3.user_message.append(self.mensaje_usuario)
        
        if llm_response:
            self.memory.local_state.etapa3.llm_response = llm_response
        
        # Actualizar timestamp
        self.memory.last_interaction = datetime.now(timezone.utc)

    def procesar_mensaje_usuario(self, mensaje_usuario: str):
        self.mensaje_usuario = mensaje_usuario

        if 'inicio' in self.current_state.id:
            self._procesar_respuesta_afectacion()
        elif 'profundizando' in self.current_state.id:
            self._procesar_respuesta_profundizacion()
    
    @classmethod
    def from_memory(cls, memory: Memory, mensaje_usuario: Optional[str] = None):
        maquina = cls(memory=memory, mensaje_usuario=mensaje_usuario)
        
        ultimo_mensaje_aibo = memory.local_state.etapa3.aibo_message[-1] if memory.local_state.etapa3.aibo_message else ""

        if '¿cómo afecta eso tu día a día o tus planes de crecimiento?' in ultimo_mensaje_aibo:
            logger.info(f"Entrando a inicio de maquina de etapa 3")
            maquina.current_state = maquina.inicio
        
        elif '¿Sientes que pierdes muchas horas en cosas que podrían hacerse más rápido o solas?' in ultimo_mensaje_aibo:
            logger.info(f"Entrando a profundizando tiempo de maquina de etapa 3")
            maquina.current_state = maquina.profundizando_tiempo
        
        elif '¿Esa falta de claridad para planear, ¿te ha hecho perder oportunidades o tomar decisiones con mucha duda?' in ultimo_mensaje_aibo:
            logger.info(f"Entrando a profundizando incertidumbre de maquina de etapa 3")
            maquina.current_state = maquina.profundizando_incertidumbre
        
        elif '¿Este tema ha hecho que los ingresos sean muy variables mes a mes, o que sea difícil saber cuánto vas a ganar?' in ultimo_mensaje_aibo:
            logger.info(f"Entrando a profundizando dinero de maquina de etapa 3")
            maquina.current_state = maquina.profundizando_dinero
        
        elif '¿En tu experiencia, ¿qué crees que es la principal razón por la que' in ultimo_mensaje_aibo:
            logger.info(f"Entrando a esperando causa raiz de maquina de etapa 3")
            maquina.current_state = maquina.esperando_causa_raiz
        
        # Procesar mensaje si hay uno nuevo
        if mensaje_usuario:
            maquina.procesar_mensaje_usuario(mensaje_usuario)
        
        return maquina