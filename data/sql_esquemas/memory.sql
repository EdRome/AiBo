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