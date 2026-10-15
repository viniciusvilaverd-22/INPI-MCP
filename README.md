# INPI MCP — Inteligencia de Marcas para Agentes de IA

![Python](https://img.shields.io/badge/Python-3.11%2B-informational)
![FastAPI](https://img.shields.io/badge/FastAPI-API-informational)
![MCP](https://img.shields.io/badge/Model%20Context%20Protocol-MCP-informational)
![Version](https://img.shields.io/badge/version-0.3.1-yellow)

> Infraestrutura experimental para pesquisar, comparar, ingerir e acompanhar publicacoes de marcas brasileiras com API, PostgreSQL e Model Context Protocol.

**Projeto independente, nao oficial e sem vinculo institucional com o Instituto Nacional da Propriedade Industrial (INPI).**

## 0.3.1 — hardening

A 0.3.1 endurece a linha incremental 0.3.0:

- lock PostgreSQL por advisory lock para impedir duas ingestoes mutantes simultaneas;
- retomada comprovavel depois de execucao `failed`;
- observabilidade em `GET /v1/rpi/status`;
- duracao, contagem de estados, cursor gap e ultima falha;
- endpoint `/v1/admin/ingest/xml` fechado por padrao;
- abertura do endpoint administrativo apenas com `APP_ENV=dev` **e** `ENABLE_DEV_ADMIN_INGEST=true`;
- prova MCP via transporte stdio real, alem do teste in-process;
- CI PostgreSQL com prova real de contencao do lock.

## Ingestao incremental

Estabeleca o baseline validado:

```bash
python -m app.cli ingest-rpi 2908
python -m app.cli rpi-status
```

Retome a partir da ultima RPI concluida:

```bash
python -m app.cli ingest-next --max-count 4
```

Se a proxima publicacao ainda nao estiver disponivel ou uma execucao falhar, `last_ingested_rpi` nao avanca indevidamente.

Intervalo explicito:

```bash
python -m app.cli ingest-range 2908 2912
```

Apenas detectar publicacoes:

```bash
python -m app.cli latest-rpi
```

ou, para diagnostico direto dos ZIPs:

```bash
python -m app.cli discover-rpi --after 2908 --max-scan 4
```

## Estado operacional

```bash
python -m app.cli rpi-status
```

ou:

```text
GET /v1/rpi/status
```

O retorno inclui:

- `last_ingested_rpi`;
- `last_checked_rpi`;
- `cursor_gap`;
- contagens por status;
- ultima execucao e duracao;
- ultima falha;
- historico recente.

## Concorrencia

Em PostgreSQL, os fluxos mutantes de RPI usam um advisory lock global do INPI MCP.

Se outra ingestao estiver ativa, a segunda tentativa falha rapidamente com:

```text
outra ingestao de RPI ja esta em execucao neste banco
```

Isso evita dois `ingest-next` concorrentes disputando o mesmo cursor.

## RPI 2908 — prova E2E real

```text
processos         39.858
classes Nice      34.736
eventos           40.201
2a ingestao       0 novos eventos
API real data     PASS
MCP real data     PASS
parser            rpi-marcas-xml-0.2.1
```

| Artefato | Tamanho | SHA-256 |
|---|---:|---|
| RM2908.zip | 10.726.796 bytes | `63794e53ee247d0c70fb9b77f98ed45e2602bb0e5166e347c00d938efa1ff400` |
| RM2908.xml | 61.214.732 bytes | `23392bfc9e03c52c9fa8befc9be21e4f3ee50993dfe21edb876cbbd62706089d` |

A 0.3.1 acrescenta ao gate MCP uma sessao **stdio real**, com `initialize`, `list_tools` e chamadas reais de `search_trademark`, `get_trademark` e `compare_trademark`.

## Docker DEV

```bash
docker compose up --build
```

O compose DEV habilita explicitamente o endpoint administrativo local:

```text
APP_ENV=dev
ENABLE_DEV_ADMIN_INGEST=true
```

Fora dessa combinacao, o endpoint administrativo responde 404 e nao aparece no OpenAPI.

## Migrations

Para bancos anteriores a 0.2.1:

```bash
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f db/002_specification_hash.sql
```

Para estado incremental 0.3.x:

```bash
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f db/003_rpi_ingestion_state.sql
```

## Monitor de novas RPIs

O workflow de monitoramento e **best-effort**. O INPI tem respondido HTTP 503 a runners do GitHub em alguns momentos.

Esse comportamento e tratado de forma segura:

- erro 5xx nao e interpretado como "nao existe nova RPI";
- nenhuma RPI falsa e criada;
- nenhuma ingestao automatica de banco e executada;
- o monitor nao possui credenciais de banco.

## MCP

Ferramentas atuais:

- `search_trademark`
- `compare_trademark`
- `get_trademark`

O MCP e um **adapter**. A regra de negocio permanece no servico de dominio.

## Similaridade

O motor `sim-v0.1.0` combina:

```text
35% lexical
30% fonetica
20% estrutura de tokens
15% afinidade de mercado/classe
```

O score significa similaridade computacional, nao probabilidade de deferimento ou parecer juridico.

## Seguranca

- endpoint administrativo fechado por padrao;
- monitor sem credenciais de banco;
- `raw/`, `.env`, `.gentill/` e evidencias locais fora do Git;
- producao continua fora do escopo desta release.

Consulte [SECURITY.md](SECURITY.md).

## Licenca

Este e um repositorio publico/source-available. O arquivo [LICENSE](LICENSE) define os direitos de uso atuais.

## Aviso

Este software e experimental e possui finalidade tecnica e informativa. Resultados de similaridade nao constituem parecer juridico, decisao do INPI ou garantia de registrabilidade de marca.
