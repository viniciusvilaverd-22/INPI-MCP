# Estado de validacao — INPI MCP 0.2.1

Data: **04/10/2026**  
Ambiente: **DEV**  
Status: **PUBLICADO / CI PASS**

## Publicacao

```text
release commit = 50d932f7231f032a5d842a129b13b78f3f486874
pull request   = #1
PR CI run      = 37182703042
main CI run    = 37182747943
```

Todos os jobs da CI na `main` passaram:

```text
Python 3.11                PASS
Python 3.13                PASS
PostgreSQL migration 002   PASS
Docker Compose quickstart  PASS
```

## Suite local apos o E2E

```text
11 passed, 1 warning in 0.83s
```

## RPI 2908 — E2E real

A RPI oficial 2908 foi ingerida em PostgreSQL 16 descartavel, sem novo download e sem tocar em producao.

```text
RPI                2908
data               29/09/2026
processos          39.858
classes Nice       34.736
eventos            40.201
parser             rpi-marcas-xml-0.2.1
primeira ingestao  145.227 s
segunda ingestao    64.940 s
novos eventos       0
```

Gates:

```text
RPI_2908_FULL_REAL_INGESTION = PASS
IDEMPOTENCY_REAL_DATA        = PASS
API_REAL_DATA                = PASS
MCP_REAL_DATA                = PASS_IN_PROCESS
MIGRATION_002_POSTGRES       = PASS
DOCKER_COMPOSE_QUICKSTART    = PASS
```

SHA-256 do XML ingerido:

```text
23392bfc9e03c52c9fa8befc9be21e4f3ee50993dfe21edb876cbbd62706089d
```

O MCP validou registro e execucao in-process de `search_trademark`, `compare_trademark` e `get_trademark`. O transporte stdio externo nao fez parte deste E2E.

## Migration 002

A CI criou um schema legado em PostgreSQL 16, preservou dados preexistentes, aplicou `db/002_specification_hash.sql`, inseriu uma especificacao longa e reaplicou a migration para provar idempotencia.

A nova chave e:

```text
trademark_id + nice_class + specification_hash
```

A migration nao exclui duplicatas automaticamente; se detectar grupos equivalentes, aborta para revisao manual.

## Docker quickstart

A CI executou:

```text
docker compose up -d --build
GET /health
ingestao da fixture
busca MARCA EXEMPLO
docker compose down -v
```

Resultado: **PASS**.

## Producao

Continua **nao declarado**:

- production-ready;
- autenticacao pronta;
- multi-tenant pronto;
- endpoint administrativo seguro para Internet;
- monitoramento recorrente operacional;
- billing operacional.
