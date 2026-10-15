# Checklist de publicacao publica

## Baselines concluidas

- [x] Portfolio v1 publicado;
- [x] Community v1 publicada;
- [x] RPI 2908 E2E real validada;
- [x] INPI MCP 0.2.1 publicado;
- [x] INPI MCP 0.3.0 incremental publicado;
- [x] migration 002;
- [x] migration 003;
- [x] monitor de RPI com falha segura para HTTP 5xx.

## INPI MCP 0.3.1 — candidato

- [x] advisory lock implementado;
- [x] teste de recovery apos falha implementado;
- [x] observabilidade operacional implementada;
- [x] endpoint administrativo fechado por padrao;
- [x] teste de transporte MCP stdio implementado;
- [ ] CI Python 3.11;
- [ ] CI Python 3.13;
- [ ] prova PostgreSQL advisory lock;
- [ ] migrations 002–003;
- [ ] Docker Compose;
- [ ] merge na main;
- [ ] metadados finais PUBLISHED/PASS.

## Fora da publicacao

Nao incluir:

- `.env`;
- `.venv/`;
- `.gentill/`;
- `raw/`;
- `vault/`;
- logs e evidencias locais.

## Producao

A 0.3.1 continua DEV. Producao exige autenticacao/autorizacao, rate limiting, isolamento, observabilidade operacional e hardening de infraestrutura.
