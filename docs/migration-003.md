# Migration 003 — estado incremental de RPI

A migration `db/003_rpi_ingestion_state.sql` adiciona o cursor de ingestao e o historico operacional da linha 0.3.0.

## Tabelas

### rpi_ingestion_state

Linha singleton `id = 1`:

- `last_ingested_rpi`: maior RPI concluida pelo controlador incremental;
- `last_checked_rpi`: maior numero tentado ou consultado pelo controlador;
- `updated_at`: ultima alteracao.

### rpi_ingestion_run

Uma linha por numero de RPI:

- `status`: `running`, `completed`, `unavailable` ou `failed`;
- URL e hashes da fonte;
- contagens de processos/eventos;
- versao do parser;
- timestamps;
- erro, quando aplicavel.

## Aplicacao

```bash
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f db/003_rpi_ingestion_state.sql
```

A migration usa `CREATE TABLE IF NOT EXISTS`, `CREATE INDEX IF NOT EXISTS` e `ON CONFLICT DO NOTHING`, permitindo reaplicacao controlada.

## Banco com dados historicos

A migration nao inventa automaticamente um `last_ingested_rpi` para dados antigos.

Depois da atualizacao, estabeleca o baseline por uma ingestao explicitamente validada, por exemplo:

```bash
python -m app.cli ingest-rpi 2908
```

Isso e deliberado: inferir um cursor apenas pelo maior numero encontrado em dados antigos poderia ocultar lacunas.

## Garantia de avanço

`last_ingested_rpi` so e atualizado depois de:

1. obter e validar o artefato oficial;
2. validar o numero interno do XML;
3. concluir a ingestao;
4. persistir o resultado como `completed`.

Falhas e RPIs ainda indisponiveis nao avancam esse cursor.
