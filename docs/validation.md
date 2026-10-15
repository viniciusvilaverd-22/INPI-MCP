# Estado de validacao — INPI MCP 0.3.1

Data: **15/10/2026**  
Ambiente: **DEV**  
Status: **PUBLICADO / CI PASS**

## Publicacao

```text
release commit = 0398db00c517428a5afffb746f7c2b6abc5b808a
pull request   = #8
PR CI run      = 38799483624
main CI run    = 38799612128
```

## Gates da 0.3.1

```text
Python 3.11                   PASS
Python 3.13                   PASS
31 testes                     PASS
MCP stdio real                PASS
PostgreSQL advisory lock      PASS
Recovery apos failed          PASS
Observabilidade RPI           PASS
Admin endpoint default closed PASS
Migrations 002-003            PASS
Docker Compose quickstart     PASS
```

## MCP

O gate MCP nao e mais apenas in-process.

A CI inicia `python -m app.mcp_server` via stdio, inicializa uma sessao MCP, lista as ferramentas e chama:

- `search_trademark`;
- `get_trademark`;
- `compare_trademark`.

As chamadas usam uma base isolada com fixture real do projeto.

## Concorrencia

Em PostgreSQL, os fluxos mutantes de RPI usam advisory lock.

A CI prova que:

1. uma sessao adquire o lock;
2. uma segunda sessao recebe `RPIIngestionBusyError`;
3. o segundo fluxo nao entra na regiao critica;
4. o lock e liberado ao final.

## Recuperacao

Uma execucao que termina como `failed` nao avanca `last_ingested_rpi`.

O teste de recovery repete a mesma RPI, conclui com sucesso e somente entao avanca o cursor.

## Observabilidade

`GET /v1/rpi/status` e `python -m app.cli rpi-status` incluem:

- `last_ingested_rpi`;
- `last_checked_rpi`;
- `cursor_gap`;
- contagens por estado;
- ultima execucao;
- duracao;
- ultima falha;
- historico recente.

## Endpoint administrativo

`POST /v1/admin/ingest/xml` fica fechado por padrao.

Ele somente responde quando:

```text
APP_ENV=dev
ENABLE_DEV_ADMIN_INGEST=true
```

O endpoint nao aparece no OpenAPI.

## Baseline real RPI 2908

```text
processos          39.858
classes Nice       34.736
eventos            40.201
segunda ingestao   0 novos eventos
XML SHA-256        23392bfc9e03c52c9fa8befc9be21e4f3ee50993dfe21edb876cbbd62706089d
```

## Monitor

O monitor remoto continua best-effort porque o host do INPI pode responder HTTP 503 aos runners do GitHub.

Falhas 5xx nao sao tratadas como ausencia de RPI e nao geram publicacoes falsas.

## Producao

A 0.3.1 continua **nao declarada pronta para producao**.
