import json
from statemachine import StateMachine, State
from typing import Optional
from data.models.memory.memory import Memory
from whatsapp.send_message.send_message import send_whatsapp_message
from llm.core.phrase_analyzer import channel_analyzer, need_analyzer
from llm.core.summary_creator import create_summary
from datetime import datetime, timezone
import time
import logging

logger = logging.getLogger(__name__)

class Etapa2(StateMachine):
    """
    ETAPA 2: PROFUNDIZACIÓN EN EL NEGOCIO
    Integrado con arquitectura de memoria centralizada
    """
    # --- MENSAJES ---
    # mensaje_inicio = """Entiendo que {negocio} se enfoca en {descripcion} ¡Suena interesante!
    mensaje_inicio = """Entiendo
    {descripcion}
    ¡Suena interesante!

Ahora, cuéntame **¿dónde o cómo consigues a la mayoría de tus clientes hoy en día?** (Por ejemplo: ¿tienes una tienda física, vendes por Facebook o Instagram, recomiendan tus clientes, usas una página web?)."""
    mensaje_profundizando_redes = "¡Excelente! ¿Y de todas las redes, en cuál sientes que tienes más contacto con tus clientes?"
    mensaje_profundizando_boca_boca = "Esa es la mejor recomendación. ¿Te gustaría poder apoyarte en ese buen trabajo para llegar a más personas?"
    mensaje_sin_canales_claros = "Entiendo, muchos negocios comienzan así. ¿Has explorado alguna opción para dar a conocer más tu negocio?"
    mensaje_transicion = """Gracias por compartirlo. Me ayuda a tener una mejor foto de tu negocio.

Ahora, para ir al grano y enfocarnos en lo que de verdad importa, **¿cuáles son las 2 o 3 cosas que más te quitan el sueño o te gustaría mejorar en tu negocio en este momento?** (Piensa en cosas como: conseguir más clientes, organizar mejor tu tiempo, vender más a quienes ya te compran, simplificar tu trabajo diario)."""
    mensaje_priorizando_necesidades = "Veo que tienes varias cosas en mente: {items}. De estas, **¿cuál es la que sientes que más te frena o estresa hoy mismo?**"
    mensaje_cierre_una_necesidad = "Entendido, vamos a enfocarnos en esa necesidad."

    # --- ESTADOS ---
    inicio = State(initial=True)
    esperando_canales = State()
    profundizando_redes = State()
    profundizando_boca_boca = State()
    sin_canales_claros = State()
    esperando_necesidades = State()
    clarificando_necesidad_vaga = State()
    priorizando_necesidades = State()
    cierre_una_necesidad = State()
    final = State(final=True)
    
    # --- TRANSICIONES ---
    procesar_mensaje = (
        inicio.to.itself() |
        esperando_canales.to.itself() |
        profundizando_redes.to.itself() |
        profundizando_boca_boca.to.itself() |
        sin_canales_claros.to.itself() |
        esperando_necesidades.to.itself() |
        clarificando_necesidad_vaga.to.itself() |
        priorizando_necesidades.to.itself()
    )
    
    preguntar_canales = inicio.to(esperando_canales)
    
    # Transiciones desde respuesta de canales
    a_profundizar_redes = esperando_canales.to(profundizando_redes)
    a_profundizar_boca_boca = esperando_canales.to(profundizando_boca_boca)
    a_profundizar_sin_canales = esperando_canales.to(sin_canales_claros)
    a_necesidades = (
        esperando_canales.to(esperando_necesidades) |
        profundizando_redes.to(esperando_necesidades) |
        profundizando_boca_boca.to(esperando_necesidades) |
        sin_canales_claros.to(esperando_necesidades)
    )
    
    # Transiciones para necesidades
    a_clarificar_vaga = esperando_necesidades.to(clarificando_necesidad_vaga)
    a_priorizar_lista = esperando_necesidades.to(priorizando_necesidades)
    a_cierre_una_necesidad = priorizando_necesidades.to(cierre_una_necesidad)

    # Finalización
    finalizar = (
        cierre_una_necesidad.to(final) |
        clarificando_necesidad_vaga.to(final) |
        priorizando_necesidades.to(final)
    )
    
    def __init__(
        self, 
        memory: Memory,
        mensaje_usuario: Optional[str] = None
    ):
        self.memory = memory
        self.mensaje_usuario = mensaje_usuario or ""
        
        # Almacenar respuestas temporalmente
        self.respuesta_canales = ""
        self.respuesta_necesidades = ""
        self.canales = None
        self.needs = None
        self.ultimo_mensaje_enviado = ""
        
        super().__init__()
    
    def _actualizar_memoria_local(self, estado: str, aibo_msg: str = "", llm_response: str = ""):
        """Actualiza la memoria local con la interacción actual"""
        # Actualizar el estado activo
        self.memory.local_state.etapa1.active = False
        self.memory.local_state.etapa2.active = True
        self.memory.local_state.etapa3.active = False
        self.memory.local_state.etapa4.active = False
        
        # # Guardar mensajes
        # if aibo_msg:
        #     self.memory.local_state.etapa2.aibo_message.append(aibo_msg)
        
        # if self.mensaje_usuario:
        #     self.memory.local_state.etapa2.user_message.append(self.mensaje_usuario)
        
        # if llm_response:
        #     self.memory.local_state.etapa2.llm_response = llm_response
        
        # Actualizar timestamp
        self.memory.last_interaction = datetime.now(timezone.utc)
    
    def _actualizar_memoria_global(self):
        """Promueve información importante a memoria global"""
        # Si tenemos respuestas completas, actualizar datos del negocio
        if self.canales:
            self.memory.global_memory.channels = self.canales

        if self.needs:
            self.memory.global_memory.datos_negocio.needs = self.needs
    
    def on_enter_inicio(self):
        """Comienza la etapa 2 - resume etapa 1 y pregunta sobre canales"""
        # Solo procesamos si hay un mensaje inicial
        if not self.mensaje_usuario:
            return

        if self.memory.global_memory.datos_negocio.negocio.descripcion == "":
            summary = create_summary(self.mensaje_usuario)
            self.memory.global_memory.datos_negocio.negocio = summary

        # Obtener información de la etapa 1 desde memoria global
        datos_negocio = self.memory.global_memory.datos_negocio
        descripcion = datos_negocio.negocio.descripcion
        
        # Construir mensaje de inicio
        mensaje = self.mensaje_inicio.format(
            descripcion=descripcion
        )
        
        # Enviar y actualizar memoria
        self.ultimo_mensaje_enviado = mensaje
        send_whatsapp_message(self.memory.user_id, mensaje)
        self._actualizar_memoria_local("inicio", mensaje, "Pregunta sobre canales de venta")
    
    def on_enter_esperando_canales(self):
        """Procesa la respuesta sobre canales de venta"""
        if not self.mensaje_usuario:
            return
            
        self.respuesta_canales = self.mensaje_usuario
        
        # Analizar tipo de canal mencionado
        analisis = channel_analyzer(self.respuesta_canales)
        
        self.memory.local_state.etapa2.llm_response = json.dumps(analisis.model_dump())

        # Actualizar memoria con análisis
        self.memory.global_memory.channels = analisis
        
        # Decidir transición basada en análisis
        if analisis.has_multiple_social_networks():
            self.a_profundizar_redes()
        elif analisis.boca_boca:
            self.a_profundizar_boca_boca()
        elif analisis.sin_canales_claros:
            self.a_sin_canales()
        else:
            # Si no detecta nada específico, va directo a necesidades
            self.a_necesidades()
            self.canales = analisis
    
    def on_enter_profundizando_redes(self):
        """Profundiza si mencionó redes sociales"""
        mensaje = self.mensaje_profundizando_redes
        send_whatsapp_message(self.memory.user_id, mensaje)
        self.ultimo_mensaje_enviado = mensaje
        self._actualizar_memoria_local("profundizando_redes", mensaje, "Pidiendo especificar red principal")
    
    def on_enter_profundizando_boca_boca(self):
        """Profundiza si mencionó boca a boca"""
        mensaje = self.mensaje_profundizando_boca_boca
        send_whatsapp_message(self.memory.user_id, mensaje)
        self.ultimo_mensaje_enviado = mensaje
        self._actualizar_memoria_local("profundizando_boca_boca", mensaje, "Profundizando en boca a boca")
    
    def on_enter_sin_canales_claros(self):
        """Responde si no tiene canales claros"""
        mensaje = self.mensaje_sin_canales_claros
        send_whatsapp_message(self.memory.user_id, mensaje)
        self.ultimo_mensaje_enviado = mensaje
        self._actualizar_memoria_local("sin_canales_claros", mensaje, "Explorando opciones de canales")
    
    def on_enter_cierre_una_necesidad(self):
        """Responde si se eligió una necesidad"""
        mensaje = self.mensaje_cierre_una_necesidad
        send_whatsapp_message(self.memory.user_id, mensaje)
        self.ultimo_mensaje_enviado = mensaje
        self._actualizar_memoria_local("cierre_una_necesidad", mensaje, "Cerrando necesidad")
        self.memory.local_state.etapa2.active = False
        self.memory.local_state.etapa3.active = True

    def on_enter_esperando_necesidades(self):
        """Pregunta sobre necesidades y áreas de mejora"""
        # Verificar si ya estamos en este estado (evitar mensaje duplicado)
        if self.memory.local_state.etapa2.aibo_message and \
           "¿cuáles son las 2 o 3 cosas que más te quitan el sueño" in self.memory.local_state.etapa2.aibo_message[-1]:
            # Ya se envió el mensaje, solo procesar respuesta si existe
            if self.mensaje_usuario:
                self._procesar_respuesta_necesidades()

            return
        
        # Enviar mensaje de transición
        send_whatsapp_message(self.memory.user_id, self.mensaje_transicion)
        self.ultimo_mensaje_enviado = self.mensaje_transicion
        self._actualizar_memoria_local("esperando_necesidades", self.mensaje_transicion, "Pregunta sobre necesidades del negocio")
        
        # # Si ya tenemos un mensaje (puede venir de transición directa), procesarlo
        # if self.mensaje_usuario:
        #     self._procesar_respuesta_necesidades()
    
    def _procesar_respuesta_profundizacion(self):
        """Procesa respuestas en estados de profundización"""
        if not self.mensaje_usuario:
            return
        

        analisis = channel_analyzer(self.mensaje_usuario)
        self.memory.global_memory.channels = analisis
        
        # Pasar al siguiente estado (necesidades)
        self.a_necesidades()

    def _procesar_respuesta_necesidades(self):
        """Procesa la respuesta sobre necesidades"""
        self.respuesta_necesidades = self.mensaje_usuario
        
        # Analizar tipo de respuesta
        analisis = need_analyzer(self.respuesta_necesidades, self.memory.global_memory.datos_negocio)
        
        # Guardar análisis en memoria
        self.memory.local_state.etapa2.llm_response = json.dumps(analisis.model_dump())
        
        if analisis.es_respuesta_vaga:
            # Pedir clarificación
            self.a_clarificar_vaga()
        
        # elif analisis['es_lista'] and len(analisis['items']) > 1:
        elif analisis.necesidades and len(analisis.necesidades) > 1:
            # Guardar items temporalmente
            self.necesidades_temporales = analisis.necesidades
            self.a_priorizar_lista()
        
        # Actualizar memoria global
        self.memory.global_memory.datos_negocio.needs = analisis
        self.needs = analisis
        self.finalizar()

    def on_enter_clarificando_necesidad_vaga(self):
        """Pide clarificación para respuesta vaga"""
        analisis = need_analyzer(self.respuesta_necesidades, self.memory.global_memory.datos_negocio)
        
        mensaje = f"Cuando dices '{analisis.frase_vaga}', ¿es porque te gustaría llegar a gente nueva, o que los que ya te conocen compren con más frecuencia?"
        send_whatsapp_message(self.memory.user_id, mensaje)
        self.ultimo_mensaje_enviado = mensaje
        self._actualizar_memoria_local("clarificando_necesidad_vaga", mensaje, "Clarificando necesidad vaga")
    
    def on_enter_priorizando_necesidades(self):
        """Pide priorización si dio una lista"""
        items_str = ", ".join(self.necesidades_temporales[:3])
        mensaje = self.mensaje_priorizando_necesidades.format(items=items_str)
        
        send_whatsapp_message(self.memory.user_id, mensaje)
        self.ultimo_mensaje_enviado = mensaje
        self._actualizar_memoria_local("priorizando_necesidades", mensaje, "Pidiendo priorización de necesidades")
        self.memory.local_state.etapa2.active = False
        self.memory.local_state.etapa3.active = True
    
    def on_enter_final(self):
        """Finaliza la etapa 2"""
        # Actualizar memoria global con información consolidada
        self._actualizar_memoria_global()
        
        # Actualizar estado en memoria
        # self._actualizar_memoria_local("final", "", "Etapa 2 completada")
        
        # Aquí podrías activar la siguiente etapa
        # self.memory.machine_stack.append("Etapa3")
        self.memory.local_state.etapa2.active = False
        self.memory.local_state.etapa3.active = True
    
    def procesar_mensaje_usuario(self, mensaje_usuario: str):
        """Procesa un nuevo mensaje del usuario"""
        self.mensaje_usuario = mensaje_usuario
        
        # Extraer información del mensaje
        if self.mensaje_usuario:
            # Puedes agregar aquí análisis adicional si es necesario
            pass
        
        if 'profundizando' in self.current_state.id:
            self._procesar_respuesta_profundizacion()
        elif self.current_state.id in ('priorizando_necesidades','clarificando_necesidad_vaga'):
            self.finalizar()
        else:
            # Disparar la transición de procesar mensaje
            self.procesar_mensaje()
    
    def to_dict(self) -> dict:
        """Serializa el estado para persistencia"""
        # La memoria principal ya se guarda por separado
        # Aquí solo información específica de la máquina
        return {
            'estado_actual': self.current_state.id,
            'respuesta_canales': self.respuesta_canales,
            'respuesta_necesidades': self.respuesta_necesidades,
            'necesidades_temporales': getattr(self, 'necesidades_temporales', [])
        }
    
    @classmethod
    def from_memory(cls, memory: Memory, mensaje_usuario: Optional[str] = None):
        """Reconstruye desde memoria del sistema"""
        maquina = cls(memory=memory, mensaje_usuario=None)
        
        # Intentar reconstruir estado específico
        ultimo_mensaje_aibo = memory.local_state.etapa2.aibo_message[-1] if memory.local_state.etapa2.aibo_message else ""
        ultimo_mensaje_usuario = memory.local_state.etapa2.user_message[-1] if memory.local_state.etapa2.user_message else ""
        if ultimo_mensaje_usuario == "":
            ultimo_mensaje_usuario = mensaje_usuario
        
        if "¿dónde o cómo consigues a la mayoría de tus clientes" in ultimo_mensaje_aibo:
            maquina.current_state = maquina.esperando_canales
            maquina.respuesta_canales = ultimo_mensaje_usuario
        
        elif "¿Y de todas las redes, en cuál sientes" in ultimo_mensaje_aibo:
            maquina.current_state = maquina.profundizando_redes
        
        elif "¿Te gustaría poder apoyarte" in ultimo_mensaje_aibo:
            maquina.current_state = maquina.profundizando_boca_boca
        
        elif "¿Has explorado alguna opción" in ultimo_mensaje_aibo:
            maquina.current_state = maquina.sin_canales_claros
        
        elif "¿cuáles son las 2 o 3 cosas que más te quitan el sueño" in ultimo_mensaje_aibo:
            maquina.respuesta_necesidades = ultimo_mensaje_usuario
            maquina.current_state = maquina.esperando_necesidades
        
        elif "¿es porque te gustaría llegar a gente nueva" in ultimo_mensaje_aibo:
            maquina.current_state = maquina.clarificando_necesidad_vaga
        
        elif "¿cuál es la que sientes que más te frena" in ultimo_mensaje_aibo:
            maquina.necesidades_temporales = getattr(maquina, 'necesidades_temporales', [])
            maquina.current_state = maquina.priorizando_necesidades
        
        # Procesar mensaje si hay uno nuevo
        if mensaje_usuario:
            maquina.procesar_mensaje_usuario(mensaje_usuario)
        
        return maquina