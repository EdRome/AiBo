from statemachine import StateMachine, State
from typing import Optional
from data.models.memory.memory import Memory
from whatsapp.send_message.send_message import send_whatsapp_message
from llm.core.summary_creator import create_pain_point_summary
from llm.core.phrase_analyzer import other_pain_analyzer

class Etapa4(StateMachine):

    mensaje_inicio = """Gracias por tu honestidad, {nombre}. Me queda mucho más claro. Por lo que veo, en {empresa}, el desafío central gira alrededor de **{resumen_punto_de_dolor}**, y eso se debe principalmente a {causa_raiz}.

Lo que me describes es justo donde podemos ayudar. Nos especializamos en **apoyar a negocios como el tuyo a {objetivo_general} usando estrategias y herramientas prácticas, sin complicaciones.**"""

    mensaje_pregunta_otro_desafio = """Para asegurarme de que entendí todo bien y no me salté nada importante:
**¿Hay algún otro desafío o algo que consideres vital para el éxito de tu negocio que no hayamos mencionado?**"""

    # mensaje_confirmacion = """Perfecto. Con lo que hemos hablado, tengo una idea clara."""

    mensaje_confirmacion = """Con esto terminamos la bienvenida a AiBo.
Lo que sigue es compartite el menú de acciones que ofrecemos y que puedas empezar a registrar tus ventas e inventarios.
La información que me compartiste es muy valiosa y será utilizada únicamente para ayudarte a crecer tu negocio.

Gracias por confiar en AiBo. ¡Te deseo éxito en tu negocio!
"""

    # --- ESTADOS ---
    inicio = State(initial=True)
    pregunta_otro_desafio = State()
    final = State(final=True)

    # --- TRANSICIONES ---
    a_preguntar_otro_desafio = inicio.to(pregunta_otro_desafio)
    a_finalizar = pregunta_otro_desafio.to(final)

    def __init__(self, memory: Memory, mensaje_usuario: Optional[str] = None):
        self.memory = memory
        self.mensaje_usuario = mensaje_usuario or ""
        self.ultimo_mensaje_enviado = ""
        super().__init__()

    def on_enter_inicio(self):
        if not self.mensaje_usuario:
            return

        pain_point_summary = create_pain_point_summary(self.mensaje_usuario)

        self.memory.global_memory.datos_negocio.needs.pain_point.causa_raiz = pain_point_summary.causa_raiz
        self.memory.global_memory.datos_negocio.needs.pain_point.objetivo_general = pain_point_summary.objetivo_general
        self.memory.global_memory.datos_negocio.needs.pain_point.resumen_punto_de_dolor = pain_point_summary.resumen_punto_de_dolor

        mensaje = self.mensaje_inicio.format(
            nombre=self.memory.global_memory.datos_negocio.emprendedor.nombre,
            empresa=self.memory.global_memory.datos_negocio.emprendedor.nombre_negocio,
            resumen_punto_de_dolor=pain_point_summary.resumen_punto_de_dolor,
            causa_raiz=pain_point_summary.causa_raiz,
            objetivo_general=pain_point_summary.objetivo_general
        )

        send_whatsapp_message(self.memory.user_id, mensaje)
        self.ultimo_mensaje_enviado = mensaje

    def on_enter_pregunta_otro_desafio(self):
        if not self.mensaje_usuario:
            return

        mensaje = self.mensaje_pregunta_otro_desafio
        send_whatsapp_message(self.memory.user_id, mensaje)
        self.ultimo_mensaje_enviado = mensaje

    def on_enter_final(self):
        if not self.mensaje_usuario:
            return

        otros = other_pain_analyzer(self.mensaje_usuario, self.memory.global_memory.datos_negocio.needs.punto_de_dolor)
        self.memory.global_memory.datos_negocio.needs.pain_point.otros = otros

        mensaje = self.mensaje_confirmacion
        send_whatsapp_message(self.memory.user_id, mensaje)
        self.ultimo_mensaje_enviado = mensaje
        self.memory.local_state.etapa4.active = False

    def procesar_mensaje_usuario(self, mensaje_usuario: str):
        self.mensaje_usuario = mensaje_usuario
        if self.current_state == self.inicio:
            self.a_preguntar_otro_desafio()

    @classmethod
    def from_memory(cls, memory: Memory, mensaje_usuario: Optional[str] = None):
        maquina = cls(
            memory=memory,
            mensaje_usuario=mensaje_usuario
        )
        
        ultimo_mensaje_aibo = memory.local_state.etapa4.aibo_message[-1] if memory.local_state.etapa4.aibo_message else ""

        if 'Nos especializamos en **apoyar a negocios como el tuyo a' in ultimo_mensaje_aibo:
            maquina.current_state = maquina.inicio
        if 'Para asegurarme de que entendí todo bien y no me salté nada importante' in ultimo_mensaje_aibo:
            maquina.current_state = maquina.pregunta_otro_desafio
        if 'Perfecto. Con lo que hemos hablado, tengo una idea clara.' in ultimo_mensaje_aibo:
            maquina.current_state = maquina.final

        if mensaje_usuario:
            maquina.procesar_mensaje_usuario(mensaje_usuario)

        return maquina