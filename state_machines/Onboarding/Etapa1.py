from statemachine import StateMachine, State
from data.models.memory.memory import Memory
from data.models.etapa1.negocio import DatosNegocio
from llm.core.entity_extractor import extract_business_and_name
from whatsapp.send_message.send_message import send_whatsapp_message
from typing import Optional

class Etapa1(StateMachine):
    """Conexión inicial - Adaptada para arquitectura asíncrona con Cloud Tasks"""
    
    # Mensajes predefinidos
    mensaje_bienvenida = "¡Hola! Me da mucho gusto saludarte. Soy AiBo, tu asistente para explorar cómo puedes hacer crecer tu negocio con un poco de ayuda."
    mensaje_solicitud_info = "Para poder ayudarte de manera más personalizada, ¿podrías decirme tu nombre y el nombre de tu negocio o proyecto?"
    mensaje_falta_nombre = "Perfecto, ¿y cómo te llamas?"
    mensaje_falta_negocio = "Gracias {nombre}. ¿Y cómo se llama tu negocio o proyecto?"
    mensaje_validacion = """¡Mucho gusto, {nombre}! Un placer conocer de {empresa}.

Para ponerme en contexto, ¿me podrías contar en pocas palabras **qué es lo principal que ofrecen o venden?** (por ejemplo: comida casera, servicios de plomería, ropa para bebés, cursos en línea)."""
    mensaje_reconocimiento = "¡Perfecto! Ya tengo tu nombre: {nombre}"
    mensaje_reconocimiento_negocio = "¡Excelente! Entiendo que tu negocio se llama: {empresa}"

    # Estados
    inicio = State(initial=True)
    esperando_nombre = State()
    esperando_negocio = State()
    validacion = State(final=True)
    
    # Transiciones
    procesar_mensaje = inicio.to.itself() | esperando_nombre.to.itself() | esperando_negocio.to.itself()
    solicitar_nombre = inicio.to(esperando_nombre)
    solicitar_negocio = (inicio.to(esperando_negocio) | esperando_nombre.to(esperando_negocio))
    finalizar_etapa = (esperando_negocio.to(validacion) | inicio.to(validacion))
    
    def __init__(self, telefono: str, memory: Memory, mensaje_usuario: Optional[str] = None):
        self.datos_negocio = memory.global_memory.datos_negocio.emprendedor
        self.telefono = telefono
        self.mensaje_usuario = mensaje_usuario or ""
        self.ultimo_mensaje_enviado = ""
        self._extraer_entidades_iniciales()
        self.memory = memory
        super().__init__()
    
    def _extraer_entidades_iniciales(self):
        """Extrae información del mensaje inicial del usuario"""
        if self.mensaje_usuario:
            datos_extraidos = extract_business_and_name(self.mensaje_usuario)
            if datos_extraidos.nombre:
                self.datos_negocio.nombre = datos_extraidos.nombre
            if datos_extraidos.nombre_negocio:
                self.datos_negocio.nombre_negocio = datos_extraidos.nombre_negocio
    
    def on_enter_inicio(self):
        """Maneja el estado inicial - primer mensaje del usuario"""
        if not self.mensaje_usuario or self.mensaje_usuario.strip() == "":
            return
            
        # Si ya tenemos ambos datos en el primer mensaje
        if self.datos_negocio.nombre and self.datos_negocio.nombre_negocio:
            self._enviar_mensaje_validacion()
            self.finalizar_etapa()
        
        # Si solo tenemos nombre
        elif self.datos_negocio.nombre and not self.datos_negocio.nombre_negocio:
            mensaje = f"{self.mensaje_bienvenida}\n\n{self.mensaje_reconocimiento.format(nombre=self.datos_negocio.nombre)}"
            self.ultimo_mensaje_enviado = mensaje
            send_whatsapp_message(self.telefono, mensaje)
            self.solicitar_negocio()
        
        # Si solo tenemos negocio
        elif not self.datos_negocio.nombre and self.datos_negocio.nombre_negocio:
            mensaje = f"{self.mensaje_bienvenida}\n\n{self.mensaje_reconocimiento_negocio.format(empresa=self.datos_negocio.nombre_negocio)}"
            self.ultimo_mensaje_enviado = mensaje
            send_whatsapp_message(self.telefono, mensaje)
            self.solicitar_nombre()
        
        # Si no tenemos nada
        else:
            mensaje = f"{self.mensaje_bienvenida}\n\n{self.mensaje_solicitud_info}"
            self.ultimo_mensaje_enviado = mensaje
            send_whatsapp_message(self.telefono, mensaje)
            # self.solicitar_nombre()
    
    def on_enter_esperando_nombre(self):
        """Maneja el estado de espera por el nombre"""

        if self.mensaje_usuario and self.mensaje_usuario.strip():
            datos_extraidos = extract_business_and_name(self.mensaje_usuario)
            
            # Actualizar nombre si se encontró
            if datos_extraidos.nombre:
                self.datos_negocio.nombre = datos_extraidos.nombre
                
                # Verificar si también tenemos el negocio
                if datos_extraidos.nombre_negocio:
                    self.datos_negocio.nombre_negocio = datos_extraidos.nombre_negocio
                
                # Si tenemos ambos, proceder a validación
                if self.datos_negocio.nombre and self.datos_negocio.nombre_negocio:
                    self._enviar_mensaje_validacion()
                    self.finalizar_etapa()
                    return
                
                # Si solo tenemos nombre, preguntar por negocio
                mensaje = self.mensaje_reconocimiento.format(nombre=self.datos_negocio.nombre)
                if not self.datos_negocio.nombre_negocio:
                    # mensaje += f"\n\n{self.mensaje_falta_negocio.format(nombre=self.datos_negocio.nombre)}"
                    self.ultimo_mensaje_enviado = mensaje
                    send_whatsapp_message(self.telefono, mensaje)
                    self.solicitar_negocio()
                else:
                    self._enviar_mensaje_validacion()
                    self.finalizar_etapa()
            else:
                # No se pudo extraer nombre, volver a preguntar
                self.ultimo_mensaje_enviado = self.mensaje_falta_nombre
                send_whatsapp_message(self.telefono, self.mensaje_falta_nombre)
    
    def on_enter_esperando_negocio(self):
        """Maneja el estado de espera por el nombre del negocio"""
        
        if self.mensaje_usuario and self.mensaje_usuario.strip():
            datos_extraidos = extract_business_and_name(self.mensaje_usuario)
            
            # Actualizar negocio si se encontró
            if datos_extraidos.nombre_negocio:
                self.datos_negocio.nombre_negocio = datos_extraidos.nombre_negocio
            
            # Actualizar nombre si también se proporcionó
            if datos_extraidos.nombre:
                self.datos_negocio.nombre = datos_extraidos.nombre
            
            # Verificar si tenemos ambos
            if self.datos_negocio.nombre and self.datos_negocio.nombre_negocio:
                self._enviar_mensaje_validacion()
                self.finalizar_etapa()
            elif self.datos_negocio.nombre_negocio:
                # Solo tenemos negocio, preguntar por nombre
                mensaje = f"{self.mensaje_reconocimiento_negocio.format(empresa=self.datos_negocio.nombre_negocio)}\n\n{self.mensaje_falta_nombre}"
                self.ultimo_mensaje_enviado = mensaje
                send_whatsapp_message(self.telefono, mensaje)
                self.solicitar_nombre()
            else:
                # No se pudo extraer negocio, volver a preguntar
                if self.datos_negocio.nombre:
                    mensaje = self.mensaje_falta_negocio.format(nombre=self.datos_negocio.nombre)
                    self.ultimo_mensaje_enviado = mensaje
                    send_whatsapp_message(self.telefono, mensaje)

    def _enviar_mensaje_validacion(self):
        """Envía el mensaje de validación final"""
        mensaje = self.mensaje_validacion.format(
            nombre=self.datos_negocio.nombre,
            empresa=self.datos_negocio.nombre_negocio
        )
        self.ultimo_mensaje_enviado = mensaje
        self.memory.local_state.etapa1.aibo_message.append(mensaje)
        send_whatsapp_message(self.telefono, mensaje)
    
    def procesar_respuesta_usuario(self):
        """Procesa una nueva respuesta del usuario"""
        self.procesar_mensaje(self.mensaje_usuario)

    def to_dict(self):
        """Serializa el estado actual para almacenar en memoria/conversación"""
        return {
            'estado_actual': self.current_state.id,
            'datos_negocio': {
                'nombre': self.datos_negocio.nombre,
                'nombre_negocio': self.datos_negocio.nombre_negocio
            },
            'telefono': self.telefono
        }
    
    @classmethod
    def from_memory(cls, memory: Memory, active_state: str, mensaje_usuario: Optional[str] = None):
        """Reconstruye la máquina de estados desde datos serializados"""
        maquina = cls(
            telefono=memory.user_id,
            memory=memory,
            mensaje_usuario=mensaje_usuario
        )
        
        # Restaurar estado
        if active_state == 'esperando_nombre':
            maquina.solicitar_nombre()
        elif active_state == 'esperando_negocio':
            maquina.solicitar_negocio()
        elif active_state == 'validacion':
            maquina.finalizar_etapa()
        
        return maquina