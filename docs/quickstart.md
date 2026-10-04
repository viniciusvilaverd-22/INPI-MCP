# Quickstart — 5 minutos

A forma mais simples de experimentar o INPI MCP e pela stack Docker de DEV.

## 1. Suba a API e o PostgreSQL

```bash
docker compose up --build
```

A API fica em:

```text
http://localhost:8000
```

Abra:

- demo local: `http://localhost:8000/demo`;
- OpenAPI/Swagger: `http://localhost:8000/docs`;
- health: `http://localhost:8000/health`.

## 2. Carregue a fixture de demonstracao

A fixture e pequena e serve apenas para validar o fluxo.

```bash
curl -X POST "http://localhost:8000/v1/admin/ingest/xml?path=fixtures/rpi-layout-sample.xml"
```

Depois pesquise `MARCA EXEMPLO` na demo com a classe Nice `39`.

## 3. Compare sinais

```bash
curl -X POST http://localhost:8000/v1/trademarks/compare \
  -H "Content-Type: application/json" \
  -d '{"left":{"name":"GENTILL MOB","nice_classes":[39]},"right":{"name":"GENTIL MOB","nice_classes":[39]}}'
```

O score e **similaridade computacional**, nunca probabilidade de deferimento.

## 4. RPI oficial pela CLI

Para trabalhar com uma publicacao oficial:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -e ".[test,mcp]"

python -m app.cli download-rpi 2908
python -m app.cli ingest-rpi 2908
```

A CLI:

1. usa a URL oficial `https://revistas.inpi.gov.br/txt/RM<numero>.zip`;
2. grava em `raw/rpi/<numero>/`;
3. calcula SHA-256 do ZIP e XML;
4. valida se o numero interno da revista corresponde ao solicitado;
5. evita extracao de caminhos arbitrarios do ZIP;
6. reaproveita o ZIP local por padrao;
7. ingere usando o mesmo parser versionado da API.

`raw/` e ignorado pelo Git.

## Banco persistente criado antes da 0.2.1

Se voce ja possui um PostgreSQL persistente criado por uma versao anterior, aplique a migration antes de iniciar a API 0.2.1:

```bash
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f db/002_specification_hash.sql
```

Instalacoes novas nao precisam desse passo manual.

Detalhes: [migration-002.md](migration-002.md).

## Limites

Esta release continua sendo DEV:

- o endpoint administrativo de ingestao nao deve ser exposto publicamente;
- nao ha autenticacao ou multi-tenant;
- a base local depende das RPIs que voce ingeriu;
- resultados nao substituem pesquisa juridica ou consulta oficial ao INPI.
