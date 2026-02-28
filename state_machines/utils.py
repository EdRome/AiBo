from data.models.memory.memory import Memory

def creditos_casi_agotados(memory: Memory):
    return memory.creditos_disponibles <= 5

def creditos_agotados(memory: Memory):
    return memory.creditos_disponibles == 0

def reiniciar_creditos(memory: Memory):
    memory.creditos_disponibles = 20