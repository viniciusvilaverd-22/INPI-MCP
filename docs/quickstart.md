# Quickstart — 5 minutos

A forma mais simples de experimentar o INPI MCP e pela stack Docker de DEV.

## 1. Suba a API e o PostgreSQL

```bash
docker compose up --build
```

Abra:

- demo: `http://localhost:8000/demo`;
- Swagger: `http://localhost:8000/docs`;
- health: `http://localhost:8000/health`;
- estado de RPI: `http://localhost:8000/v1/rpi/status`.

## 2. Carregue a fixture

```bash
curl -X POST "http://localhost:8000/v1/admin/ingest/xml?path=fixtures/rpi-layout-sample.xml"
```

Depois pesquise `MARCA EXEMPLO` com classe Nice `39`.

## 3. Compare sinais

```bash
curl -X POST http://localhost:8000/v1/trademarks/compare \
  -H "Content-Type: application/json" \
  -d '{"left":{"name":"GENTILL MOB","nice_classes":[39]},"right":{"name":"GENTIL MOB","nice_classes":[39]}}'
```

O score e similaridade computacional, nao probabilidade juridica.

## 4. Instale a CLI

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -e ".[test,mcp]"
```

## 5. Estabeleca o baseline de ingestao

```bash
python -m app.cli ingest-rpi 2908
python -m app.cli rpi-status
```

Depois, para acompanhar as proximas RPIs:

```bash
python -m app.cli ingest-next --max-count 4
```

A CLI para na primeira RPI ainda indisponivel e nao avanca `last_ingested_rpi` indevidamente.

Um intervalo explicito:

```bash
python -m app.cli ingest-range 2908 2912
```

Apenas detectar novas publicacoes:

```bash
python -m app.cli discover-rpi --after 2908 --max-scan 4
```

## Banco persistente existente

Se o banco veio de uma versao anterior a 0.2.1:

```bash
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f db/002_specification_hash.sql
```

Para adicionar o estado incremental da 0.3.0:

```bash
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f db/003_rpi_ingestion_state.sql
```

Instalacoes novas nao precisam aplicar as migrations manualmente.

## Monitor automatico

O workflow `.github/workflows/rpi-monitor.yml` detecta novas RPIs em dias uteis e abre issues com label `rpi-monitor`.

Ele nao baixa o ZIP completo nem ingere automaticamente.

Detalhes: [rpi-monitoring.md](rpi-monitoring.md).

## Limites

Esta release continua DEV:

- o endpoint administrativo de ingestao nao deve ser exposto publicamente;
- nao ha autenticacao ou multi-tenant;
- o monitor remoto nao substitui a validacao SHA-256 durante a ingestao;
- resultados nao substituem pesquisa juridica ou consulta oficial ao INPI.
