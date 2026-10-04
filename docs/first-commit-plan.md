# Gate do primeiro commit

Data: 03/10/2026.

Este documento define o conjunto **intencional** da primeira publicação do INPI MCP. Ele não representa um commit já realizado.

## Estado do gate

- repositório Git local: **não inicializado**;
- commit: **não realizado**;
- remoto: **não configurado**;
- push: **não realizado**;
- publicação: **não realizada**.

## PUBLICAR

Arquivos raiz:

```text
.env.example
.gitattributes
.gitignore
CONTRIBUTING.md
Dockerfile
LICENSE
PUBLIC_MANIFEST.json
README.md
SECURITY.md
VALIDATION.json
docker-compose.yml
install-dev.ps1
pyproject.toml
```

Automação:

```text
.github/workflows/ci.yml
```

Aplicação:

```text
app/__init__.py
app/config.py
app/db.py
app/ingest.py
app/main.py
app/mcp_adapter.py
app/mcp_server.py
app/models.py
app/normalization.py
app/repository.py
app/schemas.py
app/services.py
app/similarity.py
```

Banco:

```text
db/001_init.sql
```

Documentação:

```text
docs/architecture.md
docs/first-commit-plan.md
docs/mcp-tools.md
docs/public-readiness.md
docs/validation.md
```

Exemplos:

```text
examples/compare-trademarks.json
examples/mcp-host-config.example.json
examples/search-trademarks.json
```

Fixture e testes:

```text
fixtures/rpi-layout-sample.xml
tests/conftest.py
tests/test_api.py
tests/test_ingest.py
tests/test_similarity.py
```

## IGNORAR

Não deve entrar no primeiro commit:

```text
.env
.venv/
.pytest_cache/
__pycache__/
.gentill/
.gentill-audit.jsonl
.gentill-audit.jsonl.lock
.docker-temp/
raw/
vault/
*.log
arquivos de diagnóstico
snapshots locais
saídas de validação locais
scripts one-off de ingestão/validação vinculados ao ambiente local
```

## REVISAR ANTES DO PRIMEIRO `git add`

1. confirmar que `.gitignore` está ativo;
2. revisar a saída de `git status --short --untracked-files=all`;
3. comparar os arquivos visíveis com `PUBLIC_MANIFEST.json`;
4. garantir que nenhum arquivo em `raw/`, `vault/`, `.gentill/` ou logs aparece como candidato;
5. só então preparar o primeiro commit.

## Gate de aceite

O primeiro commit só deve ser autorizado quando:

```text
TRACKED_CANDIDATES == PUBLIC_MANIFEST
IGNORED_SENSITIVE == PASS
LOCAL_PATH_LEAKAGE == NONE
SECRETS_SCAN == PASS
COMMIT == NOT_YET
PUSH == NOT_YET
```
