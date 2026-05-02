from datetime import datetime, timedelta
from data.db.remainders import get_remainder_count
from data.db.memory import get_memory_state
from data.db.sales import get_sales_count
from data.db.messages import check_streak

class GamificationManager:
    LEVELS_CONFIG = {
        'Sincronización de interfaz': {
            'target_level': 'Centinela Local',
            'requirements': {
                'remainders': 1,
                'sales': 1,
                'queries': 1,
                'onboarding': 1
            }
        },
        'Centinela Local': {
            'target_level': 'Socio de la red',
            'requirements': {
                'remainders': 5,
                'sales': 5,
                'queries': 5,
                'streak': 3
            }
        }
    }

    MESSAGE_TEXT = {
        'requirements':{
            'remainders': 'recordatorios',
            'sales': 'ventas',
            'queries': 'consultas',
            'onboarding': 'perfil'
        }
    }

    @staticmethod
    def get_user_stats(memory):
        user_id = memory.user_id
        return {
            'remainders': get_remainder_count(user_id),
            'sales': get_sales_count(user_id),
            'onboarding': GamificationManager.check_profile_complete(memory),
            'streak': check_streak(user_id)
        }

    @staticmethod
    def manage_progress(memory):
        user_id = memory.user_id
        memory_state = get_memory_state(user_id)
        # Si no había nivel actual, se asigna el nivel 1
        if not memory_state.nivel_actual:
            memory_state.nivel_actual = 'Sincronización de interfaz'
            memory_state.progreso_nivel = 0

        # Se extrae la configuración del nievel actual
        config = GamificationManager.LEVELS_CONFIG.get(memory_state.nivel_actual)
        # Si no hay más niveles, retorna solo la memoria. ESTO DEBERÍA SER UN BUG, SIEMPRE DEBE HABER NIVELES NUEVOS
        if not config: return memory_state

        # Obten las estadísticas del usuario y sus requisitos para cambiar de nivel
        stats = GamificationManager.get_user_stats(memory)
        reqs = config['requirements']

        completed_tasks = 0
        total_tasks = len(reqs)
        new_missions = []
        event_type = ""
        # Valida que misiones ya están cumplidas
        tasks_done = [mision for mision in memory_state.misiones or [] if "✅" in mision]

        for key, target in reqs.items():
            current = stats.get(key, 0)
            is_done = current >= target
            status_icon = "✅" if is_done else "⬜"
            texto = GamificationManager.MESSAGE_TEXT['requirements'].get(key)
            new_missions.append(f"{status_icon} {texto.capitalize()}: {min(current, target)}/{target}")

            # Valida si la tarea que acaba de completas NO se había completado antes
            was_already_done = any(texto.capitalize() in mision for mision in tasks_done)
            if is_done and not was_already_done:
                newly_completed_mission = True
                completed_tasks += 1
                event_type = "MISSION_COMPLETED"

        memory_state.progreso_nivel = int((completed_tasks / total_tasks) * 100)
        memory_state.misiones = new_missions
        memory_state.siguiente_nivel = config['target_level'] # Aquí trae el nivel objetivo actual

        if memory_state.progreso_nivel >= 100:
            memory_state.nivel_actual = config['target_level']
            memory_state.progreso_nivel = 0
            event_type = "LEVEL_UP"
            # En caso de haber hecho un cambio de nivel, actualiza el siguiente nivel objetivo
            memory_state.siguiente_nivel = GamificationManager.LEVELS_CONFIG.get(memory_state.nivel_actual)['target_level']

        return memory_state, event_type

    @staticmethod
    def check_profile_complete(memory):
        memoria_global = memory.global_memory
        datos_negocio = memoria_global.datos_negocio

        nombre_negocio = datos_negocio.emprendedor.nombre_negocio
        nombre_emprendedor = datos_negocio.emprendedor.nombre
        giro_negocio = datos_negocio.negocio.giro
        ubicacion_negocio = datos_negocio.negocio.ubicacion

        nombre_negocio_completo = nombre_negocio is not None and nombre_negocio != ""
        nombre_emprendedor_completo = nombre_emprendedor is not None and nombre_emprendedor != ""
        giro_negocio_completo = giro_negocio is not None and giro_negocio != ""
        ubicacion_negocio_completo = ubicacion_negocio is not None and ubicacion_negocio != ""

        return int(nombre_negocio_completo and nombre_emprendedor_completo and giro_negocio_completo and ubicacion_negocio_completo)