# INPI MCP — Inteligencia de Marcas para Agentes de IA

![Python](https://img.shields.io/badge/Python-3.11%2B-informational)
![FastAPI](https://img.shields.io/badge/FastAPI-API-informational)
![MCP](https://img.shields.io/badge/Model%20Context%20Protocol-MCP-informational)
![Version](https://img.shields.io/badge/version-0.3.0-yellow)

> Infraestrutura experimental para pesquisar, comparar, ingerir e acompanhar publicacoes de marcas brasileiras com API, PostgreSQL e Model Context Protocol.

**Projeto independente, nao oficial e sem vinculo institucional com o Instituto Nacional da Propriedade Industrial (INPI).**

## O que a 0.3.0 acrescenta

A linha 0.3.0 transforma a ingestao unitária em um fluxo incremental retomavel:

- estado persistente `last_ingested_rpi`;
- `last_checked_rpi` separado do ultimo numero concluido;
- historico de execucoes por RPI;
- `ingest-range` para intervalos;
- `ingest-next` para retomar automaticamente;
- parada segura na primeira RPI ainda indisponivel;
- descoberta leve de novas RPIs sem baixar o ZIP inteiro;
- monitor agendado no GitHub que abre um issue quando detecta nova publicacao;
- migration PostgreSQL `003_rpi_ingestion_state.sql`;
- endpoint read-only `GET /v1/rpi/status`.

**O monitor nao ingere automaticamente.** Deteccao e mutacao de banco permanecem separadas.

## Comece em 5 minutos

```bash
docker compose up --build
```

Depois abra:

- **Demo:** `http://localhost:8000/demo`
- **Swagger:** `http://localhost:8000/docs`
- **Health:** `http://localhost:8000/health`
- **Estado RPI:** `http://localhost:8000/v1/rpi/status`

Guia completo: [docs/quickstart.md](docs/quickstart.md).

## Ingestao incremental

Estabeleca o primeiro numero conhecido:

```bash
python -m app.cli ingest-rpi 2908
```

Consulte o cursor:

```bash
python -m app.cli rpi-status
```

Depois retome automaticamente:

```bash
python -m app.cli ingest-next --max-count 4
```

Se a proxima RPI ainda nao existir, a execucao para sem alterar `last_ingested_rpi`. Na proxima tentativa, ela recomeca exatamente nesse numero.

Para um intervalo explicito:

```bash
python -m app.cli ingest-range 2908 2912
```

Para apenas verificar publicacoes, sem ingestao:

```bash
python -m app.cli discover-rpi --after 2908 --max-scan 4
```

Detalhes: [docs/rpi-ingestion.md](docs/rpi-ingestion.md) e [docs/rpi-monitoring.md](docs/rpi-monitoring.md).

## RPI 2908 — prova E2E real

A RPI oficial 2908 foi validada em PostgreSQL 16 descartavel:

```text
processos         39.858
classes Nice      34.736
eventos           40.201
2a ingestao       0 novos eventos
API real data     PASS
MCP real data     PASS_IN_PROCESS
parser            rpi-marcas-xml-0.2.1
```

| Artefato | Tamanho | SHA-256 |
|---|---:|---|
| RM2908.zip | 10.726.796 bytes | `63794e53ee247d0c70fb9b77f98ed45e2602bb0e5166e347c00d938efa1ff400` |
| RM2908.xml | 61.214.732 bytes | `23392bfc9e03c52c9fa8befc9be21e4f3ee50993dfe21edb876cbbd62706089d` |

## Banco persistente existente

Para bancos anteriores a 0.2.1:

```bash
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f db/002_specification_hash.sql
```

Para habilitar o estado incremental da 0.3.0:

```bash
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f db/003_rpi_ingestion_state.sql
```

As migrations sao testadas para reaplicacao idempotente. Nenhuma delas exclui automaticamente registros de marcas.

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

O score significa **similaridade computacional**, nao probabilidade de deferimento ou parecer juridico.

## Seguranca

- o endpoint `/v1/admin/ingest/xml` continua restrito a DEV;
- o monitor do GitHub usa apenas permissao de leitura de conteudo e escrita de issues;
- o monitor nao recebe credenciais de banco;
- `raw/`, `.env`, `.gentill/` e evidencias locais permanecem fora do Git.

Consulte [SECURITY.md](SECURITY.md).

## Licenca

Este e um repositorio publico/source-available. O arquivo [LICENSE](LICENSE) define os direitos de uso atuais; a publicacao do codigo nao altera essa licenca.

## Aviso

Este software e experimental e possui finalidade tecnica e informativa. Resultados de similaridade nao constituem parecer juridico, decisao do INPI ou garantia de registrabilidade de marca.
