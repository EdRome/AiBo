CREATE TABLE transactional.whatsapp (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    sender TEXT,
    receiver TEXT,
    body TEXT,
    data JSONB,
    multimedia TEXT
);