# Ingestao auditavel de RPI oficial

## Fonte

A fonte padrao e a Revista da Propriedade Industrial em XML/ZIP:

```text
https://revistas.inpi.gov.br/txt/RM<numero>.zip
```

O projeto nao depende de scraping HTML para essa ingestao.

## Fluxo Community v1

```text
numero da RPI
  -> URL oficial
  -> download .zip.download
  -> validacao ZIP
  -> rename atomico RM<numero>.zip
  -> extracao segura somente do XML
  -> validacao do atributo revista.numero
  -> SHA-256 ZIP + XML
  -> source.json local
  -> parser versionado
  -> processos + classes + eventos idempotentes
```

O modulo responsavel e `app/rpi_source.py`.

## Comandos

Somente baixar/validar:

```bash
python -m app.cli download-rpi 2908
```

Inspecionar um XML existente:

```bash
python -m app.cli inspect-rpi raw/rpi/2908/RM2908.xml
```

Baixar e ingerir:

```bash
python -m app.cli ingest-rpi 2908
```

Use `--force` somente quando quiser baixar novamente a mesma publicacao.

## Idempotencia

A ingestao de eventos usa uma chave logica composta por:

- numero da RPI;
- processo;
- codigo do despacho;
- protocolo;
- hash estavel do payload.

Reexecutar a mesma RPI nao deve criar eventos duplicados.

## Caso real: RPI 2908

Uma execucao anterior em DEV comprovou o download oficial:

- URL: `https://revistas.inpi.gov.br/txt/RM2908.zip`;
- ZIP: **10.726.796 bytes**;
- SHA-256 ZIP: `63794e53ee247d0c70fb9b77f98ed45e2602bb0e5166e347c00d938efa1ff400`;
- XML: **61.214.732 bytes**;
- SHA-256 XML: `23392bfc9e03c52c9fa8befc9be21e4f3ee50993dfe21edb876cbbd62706089d`.

Aquela missao antiga falhou **antes da ingestao**, durante descoberta do container Docker em um script PowerShell. Por isso o projeto nao converte esse download em prova de ingestao completa.

A Community v1 remove essa dependencia: download, validacao e ingestao passam pela CLI Python.

## Seguranca

O extrator nao chama `extractall()`. O XML selecionado e copiado para um destino controlado, evitando que nomes de arquivo dentro do ZIP escrevam fora de `raw/rpi/<numero>/`.
