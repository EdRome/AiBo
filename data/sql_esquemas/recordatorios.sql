CREATE TYPE estatus_recordatorio AS ENUM ('activo', 'inactivo', 'ejecutado', 'borrado');
create table dev.recordatorios (
  id serial primary key,
  user_id text,
  titulo text,
  descripcion text,
  estatus estatus_recordatorio DEFAULT 'activo',
  fecha_recordatorio timestamptz,
  fecha_creacion TIMESTAMPtZ default now(),
  fecha_actualizacion TIMESTAMPtZ default now(),
  keywords text[]
);