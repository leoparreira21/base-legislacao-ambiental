-- Registro de buscas sem resultado (lacunas da base)
-- Aplicar com:
--   npx wrangler d1 execute legislacao-ambiental --remote --file cloudflare/biblioteca/migracoes/2026-11-28-buscas-sem-resultado.sql

CREATE TABLE IF NOT EXISTS buscas_sem_resultado (
  id                INTEGER PRIMARY KEY AUTOINCREMENT,
  termo_normalizado TEXT    NOT NULL,
  termo_original    TEXT    NOT NULL,
  modo              TEXT    NOT NULL CHECK (modo IN ('simples', 'avancado')),
  filtros           TEXT    NOT NULL DEFAULT '{}',
  ocorrencias       INTEGER NOT NULL DEFAULT 1,
  primeira_vez      TEXT    NOT NULL DEFAULT (datetime('now')),
  ultima_vez        TEXT    NOT NULL DEFAULT (datetime('now')),
  status            TEXT    NOT NULL DEFAULT 'pendente'
                            CHECK (status IN ('pendente', 'resolvido', 'ignorar')),
  observacao        TEXT,
  UNIQUE (termo_normalizado, modo)
);

CREATE INDEX IF NOT EXISTS idx_buscas_sem_resultado_status
  ON buscas_sem_resultado (status, ocorrencias DESC);
