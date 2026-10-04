# INPI MCP — Inteligencia de Marcas para Agentes de IA

![Python](https://img.shields.io/badge/Python-3.11%2B-informational)
![FastAPI](https://img.shields.io/badge/FastAPI-API-informational)
![MCP](https://img.shields.io/badge/Model%20Context%20Protocol-MCP-informational)
![Tests](https://img.shields.io/badge/tests-11%20passed-success)
![Version](https://img.shields.io/badge/version-0.2.1-yellow)

> Infraestrutura experimental para pesquisar, comparar e ingerir publicacoes de marcas brasileiras com API, PostgreSQL e Model Context Protocol.

**Projeto independente, nao oficial e sem vinculo institucional com o Instituto Nacional da Propriedade Industrial (INPI).**

## RPI 2908 — prova E2E real

A versao 0.2.1 incorpora correcoes descobertas numa prova E2E com a RPI oficial 2908 em PostgreSQL 16 descartavel:

```text
processos         39.858
classes Nice      34.736
eventos           40.201
2a ingestao       0 novos eventos
API real data     PASS
MCP real data     PASS_IN_PROCESS
parser            rpi-marcas-xml-0.2.1
```

Fonte comprovada:

| Artefato | Tamanho | SHA-256 |
|---|---:|---|
| RM2908.zip | 10.726.796 bytes | `63794e53ee247d0c70fb9b77f98ed45e2602bb0e5166e347c00d938efa1ff400` |
| RM2908.xml | 61.214.732 bytes | `23392bfc9e03c52c9fa8befc9be21e4f3ee50993dfe21edb876cbbd62706089d` |

## Comece em 5 minutos

```bash
docker compose up --build
```

Depois abra:

- **Demo:** `http://localhost:8000/demo`
- **Swagger:** `http://localhost:8000/docs`
- **Health:** `http://localhost:8000/health`

Para carregar a fixture de demonstracao:

```bash
curl -X POST "http://localhost:8000/v1/admin/ingest/xml?path=fixtures/rpi-layout-sample.xml"
```

Guia completo: [docs/quickstart.md](docs/quickstart.md).

## RPI oficial pela CLI

```bash
pip install -e ".[test,mcp]"

python -m app.cli download-rpi 2908
python -m app.cli ingest-rpi 2908
```

Detalhes: [docs/rpi-ingestion.md](docs/rpi-ingestion.md).

## O que mudou em 0.2.1

- suporte ao layout oficial `lista-classe-nice > classe-nice`;
- compatibilidade preservada com `classe-nice` direto;
- `specification_hash` SHA-256 para evitar indexar especificacoes Nice muito longas;
- migration PostgreSQL `db/002_specification_hash.sql`;
- Dockerfile alinhado ao packaging atual;
- CI com prova de upgrade legado e smoke do Docker Compose.

### Migrando um banco DEV existente

Antes de executar a aplicacao 0.2.1 sobre um banco persistente criado por versoes anteriores:

```bash
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f db/002_specification_hash.sql
```

A migration faz backfill dos hashes, recusa grupos duplicados que exigem revisao manual e substitui a unicidade baseada no texto integral por:

```text
trademark_id + nice_class + specification_hash
```

Ela nao apaga duplicatas automaticamente.

Veja [docs/migration-002.md](docs/migration-002.md).

## MCP

Ferramentas atuais:

- `search_trademark`
- `compare_trademark`
- `get_trademark`

O MCP e um **adapter**. A regra de negocio permanece no servico de dominio.

[Contratos MCP](docs/mcp-tools.md) · [Arquitetura](docs/architecture.md)

## Similaridade

O motor `sim-v0.1.0` combina:

```text
35% lexical
30% fonetica
20% estrutura de tokens
15% afinidade de mercado/classe
```

O score significa **similaridade computacional**. Nao significa chance de aprovacao, chance de indeferimento ou parecer juridico.

## Testes

```bash
pytest -q
```

Validacao local apos o E2E:

```text
11 passed, 1 warning in 0.83s
```

O estado completo esta em [docs/validation.md](docs/validation.md).

## Comunidade

Veja [docs/community.md](docs/community.md) para trilha de aprendizado e ideias de contribuicao.

> O arquivo [LICENSE](LICENSE) continua definindo os direitos de uso atuais.

## Seguranca

O endpoint `/v1/admin/ingest/xml` e uma facilidade de **DEV** e nao deve ser exposto publicamente no estado atual.

Nao versione `.env`, `raw/`, `.gentill/`, logs ou evidencias locais.

Consulte [SECURITY.md](SECURITY.md).

## Aviso

Este software e experimental e possui finalidade tecnica e informativa. Resultados de similaridade nao constituem parecer juridico, decisao do INPI ou garantia de registrabilidade de marca.
