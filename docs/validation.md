# Estado de validacao — INPI MCP 0.3.1

Data: **15/10/2026**  
Ambiente: **DEV**  
Status: **CANDIDATO / CI PENDENTE**

## Baseline 0.3.0

A 0.3.0 publicada possui:

- ingestao incremental;
- `last_ingested_rpi` e `last_checked_rpi`;
- migration 003;
- monitor de novas RPIs em modo best-effort;
- 25 testes PASS;
- migrations 002–003 PASS;
- Docker Compose PASS.

O acesso da fonte oficial a partir de runners GitHub permanece degradado por HTTP 503. Esse erro nao e interpretado como ausencia de RPI.

## Hardening 0.3.1

O candidato adiciona:

- advisory lock PostgreSQL para serializar fluxos mutantes de RPI;
- falha rapida quando outra ingestao ja esta ativa;
- retry de uma RPI previamente `failed` sem avancar o cursor antes do sucesso;
- observabilidade operacional no endpoint/status;
- endpoint administrativo fechado por padrao;
- opt-in administrativo restrito a DEV;
- transporte MCP stdio real na suite.

## Gates pendentes de CI

```text
POSTGRES_ADVISORY_LOCK            PENDING
FAILED_RUN_RECOVERY              PENDING
RPI_OBSERVABILITY                PENDING
ADMIN_ENDPOINT_DEFAULT_CLOSED     PENDING
MCP_STDIO_TRANSPORT              PENDING
PYTHON_3_11                      PENDING
PYTHON_3_13                      PENDING
POSTGRES_MIGRATIONS_002_003      PENDING
DOCKER_COMPOSE_QUICKSTART        PENDING
```

## Baseline real RPI 2908

```text
processos          39.858
classes Nice       34.736
eventos            40.201
segunda ingestao   0 novos eventos
XML SHA-256        23392bfc9e03c52c9fa8befc9be21e4f3ee50993dfe21edb876cbbd62706089d
```

## Producao

Continua nao declarada como pronta para producao.
