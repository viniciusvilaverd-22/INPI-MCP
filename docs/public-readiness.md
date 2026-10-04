# Checklist de publicacao publica

Este documento separa o **baseline ja publicado** da **Community v1 publicada**.

## Baseline Portfolio v1 — concluido

- [x] README publico preparado
- [x] Arquitetura e ferramentas MCP documentadas
- [x] `.gitignore` endurecido
- [x] `SECURITY.md` e `CONTRIBUTING.md`
- [x] licenca restritiva de portfolio
- [x] workflow de CI preparado
- [x] Git local inicializado
- [x] conjunto do primeiro commit confrontado com o manifesto
- [x] primeiro commit criado
- [x] repositorio publico criado no GitHub
- [x] `origin` configurado
- [x] branch `main` publicada

Baseline:

```text
repository = viniciusvilaverd-22/INPI-MCP
branch     = main
commit     = bec37a05d5ad383acf1e30fef35029cb1a8c18af
message    = feat: establish INPI MCP portfolio release v1
```

## Community v1 — publicada

- [x] CLI de RPI oficial
- [x] demo web local
- [x] quickstart
- [x] documentacao comunitaria
- [x] exemplo oficial RPI 2908
- [x] testes de fonte/ZIP/path traversal
- [x] 10 testes PASS
- [x] CLI RPI 2908 real PASS em modo inspect
- [x] API/demo smoke PASS
- [x] commit da Community v1
- [x] push da Community v1
- [x] CI remota da Community v1 confirmada
- [ ] screenshot/GIF publico da demo

Release commit: `99ca8569426a38d8426f04b12891a2b25b7031c4`.

CI fix commit: `d543ef2e914fab2e3d7e6b6b7d7ab8c18942ebf2`.

GitHub Actions: **PASS** — run `37171833323`.

## Arquivos que nao devem ser publicados

Por padrao, nao incluir:

- `.env`;
- `.venv/`;
- `.gentill/`;
- `.gentill-audit.jsonl`;
- `raw/`;
- `vault/`;
- logs e snapshots locais;
- dependencias temporarias de validacao;
- resultados temporarios de testes;
- scripts one-off vinculados ao ambiente local.

## Gate pos-publicacao

1. manter `raw/` e evidencias locais fora do repositorio;
2. nao declarar ingestao real completa da RPI 2908 sem recibo conclusivo;
3. nao declarar production-ready sem hardening de autenticacao, isolamento e observabilidade.

## Topicos recomendados

```text
mcp
model-context-protocol
ai-agents
python
fastapi
postgresql
trademarks
inpi
similarity
data-engineering
```
