# Checklist de publicacao publica

## Baselines concluidas

- [x] Portfolio v1;
- [x] Community v1;
- [x] RPI 2908 E2E real;
- [x] INPI MCP 0.2.1;
- [x] INPI MCP 0.3.0 incremental.

## INPI MCP 0.3.1 — publicado

- [x] advisory lock PostgreSQL;
- [x] recovery apos falha;
- [x] observabilidade operacional;
- [x] endpoint administrativo fechado por padrao;
- [x] opt-in administrativo somente em DEV;
- [x] MCP stdio real;
- [x] Python 3.11 PASS;
- [x] Python 3.13 PASS;
- [x] 31 testes PASS;
- [x] migrations 002–003 PASS;
- [x] Docker Compose PASS;
- [x] PR #8 mergeado;
- [x] CI da `main` confirmada.

```text
release commit = 0398db00c517428a5afffb746f7c2b6abc5b808a
main CI run    = 38799612128
status         = PASS
```

## Monitor de RPI

O workflow remoto permanece best-effort devido a HTTP 503 ocasionais do INPI para runners GitHub.

Esse estado e seguro:

- nao infere falsa ausencia;
- nao cria RPI falsa;
- nao ingere banco automaticamente.

## Arquivos fora da publicacao

- `.env`;
- `.venv/`;
- `.gentill/`;
- `raw/`;
- `vault/`;
- logs e evidencias locais.

## Producao

Continua fora do escopo ate existirem autenticacao/autorizacao, rate limiting, isolamento, observabilidade de producao e hardening de infraestrutura.
