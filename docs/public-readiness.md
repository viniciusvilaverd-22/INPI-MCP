# Checklist de publicacao publica

Este documento separa o **baseline ja publicado** das alteracoes **Community v1 ainda locais**.

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

## Community v1 — estado local

- [x] CLI de RPI oficial
- [x] demo web local
- [x] quickstart
- [x] documentacao comunitaria
- [x] exemplo oficial RPI 2908
- [x] testes de fonte/ZIP/path traversal
- [x] 10 testes PASS
- [x] CLI RPI 2908 real PASS em modo inspect
- [x] API/demo smoke PASS
- [ ] commit da Community v1
- [ ] push da Community v1
- [ ] CI remota da Community v1 confirmada
- [ ] screenshot/GIF publico da demo

As alteracoes Community v1 **nao foram publicadas** nesta etapa.

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

## Gate para publicar a Community v1

Antes de qualquer novo commit/push:

1. revisar `git status --short --untracked-files=all`;
2. confirmar que nenhum item ignorado aparece;
3. revisar o diff da Community v1;
4. confirmar que `VALIDATION.json` esta em PASS;
5. criar commit somente com nova autorizacao;
6. fazer push somente com nova autorizacao;
7. verificar CI remota depois do push.

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
