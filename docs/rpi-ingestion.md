# Ingestao auditavel e incremental de RPI oficial

## Fonte

A fonte padrao e:

```text
https://revistas.inpi.gov.br/txt/RM<numero>.zip
```

O projeto nao depende de scraping HTML para a ingestao.

## Pipeline

```text
numero da RPI
  -> fonte oficial
  -> download temporario
  -> validacao ZIP
  -> extracao segura do XML
  -> validacao revista.numero
  -> SHA-256 ZIP + XML
  -> parser versionado
  -> processos + classes + eventos idempotentes
  -> RPIIngestionRun = completed
  -> last_ingested_rpi avanca
```

Se qualquer etapa falhar, `last_ingested_rpi` nao avanca.

## Estado persistente

A 0.3.0 adiciona:

```text
rpi_ingestion_state
  id = 1
  last_ingested_rpi
  last_checked_rpi
  updated_at

rpi_ingestion_run
  rpi_number
  status
  hashes da fonte
  contagens
  parser_version
  started_at / finished_at
  error
```

`last_checked_rpi` pode ficar a frente de `last_ingested_rpi` quando a proxima publicacao ainda nao existe ou uma tentativa falha. Isso e intencional.

## Comandos

Baixar somente:

```bash
python -m app.cli download-rpi 2908
```

Ingerir uma RPI:

```bash
python -m app.cli ingest-rpi 2908
```

Ingerir um intervalo inclusivo:

```bash
python -m app.cli ingest-range 2908 2912
```

Retomar depois da ultima RPI concluida:

```bash
python -m app.cli ingest-next --max-count 4
```

Consultar o estado:

```bash
python -m app.cli rpi-status
```

Descobrir novas publicacoes sem ingestao:

```bash
python -m app.cli discover-rpi --after 2908 --max-scan 4
```

## Semantica de retomada

Exemplo:

```text
last_ingested_rpi = 2908

ingest-next --max-count 4
  2909 -> completed
  2910 -> unavailable
  para

estado final:
last_ingested_rpi = 2909
last_checked_rpi  = 2910
```

Na proxima execucao, `ingest-next` tenta 2910 novamente. Nao pula para 2911.

## RPI ja concluida

Por padrao, uma RPI registrada como `completed` e ignorada pelo controlador incremental. Isso evita download e parsing desnecessarios.

`--force` permite uma revalidacao explicita da fonte.

## Idempotencia de dados

Eventos usam a chave logica:

- RPI;
- processo;
- codigo do despacho;
- protocolo;
- hash estavel do payload.

Classes Nice usam:

- processo;
- classe;
- SHA-256 da especificacao integral.

## Migrations

Bancos anteriores a 0.2.1:

```bash
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f db/002_specification_hash.sql
```

Estado incremental 0.3.0:

```bash
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f db/003_rpi_ingestion_state.sql
```

Instalacoes novas criam o schema atual via SQLAlchemy.

## RPI 2908

Evidencia real preservada:

```text
ZIP_BYTES   = 10.726.796
ZIP_SHA256  = 63794e53ee247d0c70fb9b77f98ed45e2602bb0e5166e347c00d938efa1ff400
XML_BYTES   = 61.214.732
XML_SHA256  = 23392bfc9e03c52c9fa8befc9be21e4f3ee50993dfe21edb876cbbd62706089d
processos   = 39.858
classes     = 34.736
eventos     = 40.201
idempotencia= PASS
```

## Seguranca

O extrator nao usa `extractall()`. O XML e copiado para destino controlado.

O monitor automatico e separado da ingestao e nao possui credenciais de banco. Veja [rpi-monitoring.md](rpi-monitoring.md).
