# Checklist de publicacao publica

## Portfolio v1 — concluido

- [x] repositorio publico criado;
- [x] branch `main` publicada;
- [x] README, seguranca e contribuicao documentados;
- [x] CI inicial configurada.

Baseline inicial:

```text
bec37a05d5ad383acf1e30fef35029cb1a8c18af
```

## Community v1 — concluida

- [x] CLI de RPI oficial;
- [x] demo web local;
- [x] quickstart;
- [x] ferramentas MCP;
- [x] CI Python 3.11/3.13.

## INPI MCP 0.2.1 — publicado

- [x] RPI 2908 real E2E;
- [x] 39.858 processos ingeridos;
- [x] 34.736 classes Nice;
- [x] 40.201 eventos;
- [x] segunda ingestao com 0 novos eventos;
- [x] API com dados reais;
- [x] MCP com dados reais in-process;
- [x] parser `rpi-marcas-xml-0.2.1`;
- [x] migration `002_specification_hash.sql`;
- [x] upgrade de schema legado validado em PostgreSQL 16;
- [x] especificacao Nice longa validada;
- [x] reaplicacao idempotente da migration;
- [x] Docker Compose quickstart validado;
- [x] PR #1 validado e mergeado;
- [x] CI da `main` confirmada.

```text
release commit = 50d932f7231f032a5d842a129b13b78f3f486874
main CI run    = 37182747943
status         = PASS
```

## Arquivos que nao devem ser publicados

Por padrao, nao incluir:

- `.env`;
- `.venv/`;
- `.gentill/`;
- `.gentill-audit.jsonl`;
- `raw/`;
- `vault/`;
- logs e snapshots locais;
- resultados temporarios de testes.

## Proximo gate tecnico

A proxima evolucao deve ser ingestao incremental de multiplas RPIs e monitoramento de novas publicacoes. Producao continua fora do escopo ate existir hardening de autenticacao, isolamento e observabilidade.
