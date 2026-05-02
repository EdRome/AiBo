CREATE TABLE testing.memory (
    user_id TEXT PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    active_context TEXT,
    machine_stack TEXT[],
    global_memory JSONB,
    local_state JSONB,
    last_interaction TIMESTAMP WITH TIME ZONE,
    task_name TEXT,
    creditos_disponibles INT DEFAULT 20
);

CREATE TABLE testing.memoria_estados (
  user_id TEXT PRIMARY KEY,
  estado_actual TEXT,
  progreso_nivel INTEGER,
  nivel_actual TEXT,
  contexto_json JSONB,
  siguiente_nivel TEXT,
  misiones TEXT[],

  CONSTRAINT fk_user_id_memory
    FOREIGN KEY (user_id)
    REFERENCES testing.memory(user_id)
    ON DELETE CASCADE
);