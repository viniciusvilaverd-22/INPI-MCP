# Estado de validacao — INPI MCP 0.2.1

Data: **04/10/2026**  
Ambiente: **DEV**

## Baseline publicado

A Community v1 anterior permanece registrada pelos commits:

```text
release commit = 99ca8569426a38d8426f04b12891a2b25b7031c4
CI fix commit  = d543ef2e914fab2e3d7e6b6b7d7ab8c18942ebf2
GitHub Actions = PASS
run             = 37171833323
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

Gates locais:

```text
RPI_2908_FULL_REAL_INGESTION = PASS
IDEMPOTENCY_REAL_DATA        = PASS
API_REAL_DATA                = PASS
MCP_REAL_DATA                = PASS_IN_PROCESS
```

SHA-256 do XML ingerido:

```text
23392bfc9e03c52c9fa8befc9be21e4f3ee50993dfe21edb876cbbd62706089d
```

O MCP validou registro e execucao in-process de `search_trademark`, `compare_trademark` e `get_trademark`. O transporte stdio externo nao fez parte deste E2E.

## Defeitos revelados

### Layout oficial de classes Nice

A RPI real usa `lista-classe-nice > classe-nice`. O parser 0.2.1 aceita esse layout e preserva o layout direto usado pelas fixtures historicas.

### Especificacoes Nice longas

Uma especificacao real ultrapassou 8 mil caracteres e excedeu o limite de linha de um indice B-tree quando o texto integral fazia parte da restricao UNIQUE.

A versao 0.2.1 preserva `specification` integral, adiciona `specification_hash` SHA-256 e usa:

```text
trademark_id + nice_class + specification_hash
```

como chave de unicidade.

## Migration 002

`db/002_specification_hash.sql`:

- habilita `pgcrypto`;
- adiciona a coluna se ausente;
- faz backfill SHA-256;
- recusa grupos duplicados antes de mudar a restricao;
- remove `uq_tm_class_spec`;
- cria `uq_tm_class_spec_hash`;
- e desenhada para reaplicacao idempotente.

A CI candidata cria um PostgreSQL 16 com schema legado, dados preexistentes, especificacao longa e repeticao da migration.

## Docker quickstart

O Dockerfile foi corrigido para copiar `app/` antes de `pip install .`.

A CI candidata tambem executa `docker compose up -d --build`, verifica `/health`, ingere a fixture, pesquisa a marca e executa `docker compose down -v`.

## Producao

Continua **nao declarado**:

- production-ready;
- autenticacao pronta;
- multi-tenant pronto;
- endpoint administrativo seguro para Internet;
- monitoramento recorrente operacional;
- billing operacional.
