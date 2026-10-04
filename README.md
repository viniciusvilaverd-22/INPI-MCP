# INPI MCP — Inteligencia de Marcas para Agentes de IA

![Python](https://img.shields.io/badge/Python-3.11%2B-informational)
![FastAPI](https://img.shields.io/badge/FastAPI-API-informational)
![MCP](https://img.shields.io/badge/Model%20Context%20Protocol-MCP-informational)
![Tests](https://img.shields.io/badge/tests-10%20passed-success)
![Release](https://img.shields.io/badge/release-Community%20v1-yellow)

> Infraestrutura experimental para pesquisar, comparar e ingerir publicacoes de marcas brasileiras com API, PostgreSQL e Model Context Protocol.

**Projeto independente, nao oficial e sem vinculo institucional com o Instituto Nacional da Propriedade Industrial (INPI).**

A Community Release v1 aproxima o projeto de quem quer **usar e aprender**, nao apenas ler a arquitetura: ha demo web local, quickstart, CLI para RPI oficial, hashes de proveniencia e testes de extracao segura.

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

A automacao:

1. usa `https://revistas.inpi.gov.br/txt/RM<numero>.zip`;
2. baixa para arquivo temporario;
3. valida o ZIP;
4. extrai somente o XML esperado para destino controlado;
5. valida o numero interno da revista;
6. calcula SHA-256 do ZIP e XML;
7. registra `source.json` local;
8. ingere com parser versionado e eventos idempotentes.

Detalhes: [docs/rpi-ingestion.md](docs/rpi-ingestion.md).

## Caso real documentado

O download oficial da **RPI 2908** foi comprovado em DEV:

| Artefato | Tamanho | SHA-256 |
|---|---:|---|
| RM2908.zip | 10.726.796 bytes | `63794e53ee247d0c70fb9b77f98ed45e2602bb0e5166e347c00d938efa1ff400` |
| RM2908.xml | 61.214.732 bytes | `23392bfc9e03c52c9fa8befc9be21e4f3ee50993dfe21edb876cbbd62706089d` |

A Community v1 tambem validou a CLI `inspect-rpi` diretamente sobre esse XML real, sem redownload.

Ainda assim, **nao declaramos a ingestao completa real da RPI 2908 como validada**. O registro publicavel esta em [examples/rpi-2908-official.json](examples/rpi-2908-official.json).

## O que o projeto entrega

| Capacidade | Estado |
|---|---|
| FastAPI | Implementada |
| PostgreSQL | Implementado |
| Ingestao XML idempotente | Implementada |
| SHA-256 da fonte | Implementado |
| Downloader oficial de RPI | Implementado |
| CLI de RPI | Implementada |
| Demo web local | Implementada |
| Busca por nome/classes | Implementada |
| Similaridade lexical/fonetica | Implementada |
| Score explicavel | Implementado |
| Testes automatizados | 10 PASS em DEV |
| CLI com RPI 2908 real | PASS em modo inspect |
| API/demo local | PASS |
| MCP | Implementado; runtime baseline PASS |
| Monitoramento continuo | Planejado |
| Autenticacao/multi-tenant | Planejado |
| Producao | Nao declarada |

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

O componente semantico permanece `0.0` nesta versao.

O score significa **similaridade computacional**. Nao significa chance de aprovacao, chance de indeferimento ou parecer juridico.

## Estrutura comunitaria

```text
app/
  cli.py             CLI para RPI oficial
  rpi_source.py      download, hash e extracao segura
  static/demo.html   demo local
  ...                dominio/API/MCP

docs/
  quickstart.md
  rpi-ingestion.md
  community.md
  architecture.md
  mcp-tools.md

examples/
tests/
fixtures/
```

## Testes

```bash
pytest -q
```

Validacao local fresca da Community v1:

```text
10 passed, 1 warning in 0.86s
```

A suite cobre:

- URL oficial da RPI;
- extracao de ZIP;
- validacao do numero da revista;
- defesa contra path traversal;
- disponibilidade da demo e metadata da release;
- ingestao e idempotencia;
- API, normalizacao e similaridade.

O estado completo esta em [docs/validation.md](docs/validation.md).

## Comunidade

Veja [docs/community.md](docs/community.md) para trilha de aprendizado e ideias de contribuicao.

> Nota: o arquivo [LICENSE](LICENSE) continua definindo os direitos de uso atuais. Esta release nao altera a licenca do projeto.

## Seguranca

O endpoint `/v1/admin/ingest/xml` e uma facilidade de **DEV** e nao deve ser exposto publicamente no estado atual.

Nao versione `.env`, `raw/`, `.gentill/`, logs ou evidencias locais.

Consulte [SECURITY.md](SECURITY.md).

## Aviso

Este software e experimental e possui finalidade tecnica e informativa. Resultados de similaridade nao constituem parecer juridico, decisao do INPI ou garantia de registrabilidade de marca.
