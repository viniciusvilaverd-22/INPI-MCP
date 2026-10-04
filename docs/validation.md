# Estado de validacao — Community Release v1

Data: **03/10/2026**
Ambiente: **DEV**

## Resultado fresco

A validacao canonica da Community v1 foi executada em container Python 3.13 com o workspace local montado em modo de teste.

Resultado:

```text
10 passed, 1 warning in 0.86s
```

A advertencia foi uma `StarletteDeprecationWarning` do `TestClient` e nao bloqueou a suite.

## CLI + RPI 2908 real

A CLI foi executada contra o XML oficial ja existente no workspace, **sem novo download**:

```text
rpi_number = 2908
rpi_date   = 29/09/2026
xml_bytes  = 61214732
```

Resultado: **PASS**.

Esse teste valida o comando `inspect-rpi` sobre o artefato real e nao deve ser confundido com prova de ingestao completa da revista.

## API e demo

Smoke local:

```text
API_DEMO_SMOKE=PASS
{"status":"ok","version":"0.2.0","release":"community-v1"}
```

Validado:

- `GET /health` = 200;
- release reportada = `community-v1`;
- versao = `0.2.0`;
- `GET /demo` = 200;
- pagina da demo contem o identificador `INPI MCP`.

## RPI 2908 — proveniencia oficial

Evidencia historica preservada e reconfirmada localmente:

```text
SOURCE_URL=https://revistas.inpi.gov.br/txt/RM2908.zip
ZIP_BYTES=10726796
ZIP_SHA256=63794e53ee247d0c70fb9b77f98ed45e2602bb0e5166e347c00d938efa1ff400
XML_BYTES=61214732
XML_SHA256=23392bfc9e03c52c9fa8befc9be21e4f3ee50993dfe21edb876cbbd62706089d
```

Interpretacao correta:

- **download oficial da RPI 2908: PASS**;
- **integridade ZIP/XML por SHA-256: PASS**;
- **CLI sobre XML real: PASS**;
- **ingestao completa real da RPI 2908: ainda nao declarada como PASS**.

A missao historica de ingestao falhou antes dessa etapa por um problema no runner PowerShell/Docker. A Community v1 substitui essa dependencia por uma CLI Python deterministica, mas esta validacao nao executou `ingest-rpi 2908` para evitar uma mutacao de dados fora do escopo do smoke autorizado.

## Cobertura Community v1

Os 10 testes cobrem:

- health e busca via API;
- disponibilidade da demo;
- ingestao XML;
- idempotencia de eventos;
- normalizacao;
- similaridade;
- URL oficial de RPI;
- extracao segura de ZIP;
- validacao do numero interno da revista;
- defesa contra path traversal.

## MCP

O runtime MCP da Portfolio v1 permanece com evidencia **PASS**. As tres ferramentas atuais nao foram alteradas pela Community v1:

- `search_trademark`;
- `compare_trademark`;
- `get_trademark`.

## Observacao sobre o host Windows

A instalacao local Python 3.14 do Windows apresentou um erro interno do proprio `asyncio/pdb` ao iniciar pytest. Nenhuma correcao de sistema foi feita. A validacao canonica foi executada em container Python 3.13, que e uma versao suportada pelo projeto.

## Producao

Continua **nao declarado**:

- production-ready;
- autenticacao pronta;
- multi-tenant pronto;
- endpoint administrativo seguro para Internet;
- monitoramento recorrente operacional;
- billing operacional.

As alteracoes Community v1 permanecem **locais, sem commit e sem push**.
