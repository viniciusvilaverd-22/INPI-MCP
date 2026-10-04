# Checklist de publicação pública

Este documento separa **preparação local** de **publicação efetiva**.

## Estado atual

- [x] README público preparado
- [x] Arquitetura pública documentada
- [x] Ferramentas MCP documentadas
- [x] Limitações e evidências documentadas
- [x] `.gitignore` endurecido para não incluir runtime/evidências locais
- [x] Política de segurança criada
- [x] Diretrizes de contribuição criadas
- [x] Licença restritiva de portfólio criada
- [x] Workflow de CI preparado
- [x] Conjunto exato do primeiro commit definido
- [x] Manifesto público machine-readable criado
- [ ] Repositório Git inicializado
- [ ] `git status` confrontado com o manifesto
- [ ] Primeiro commit
- [ ] Repositório GitHub criado
- [ ] Push executado
- [ ] GitHub Actions executado com PASS
- [ ] GitHub Security / vulnerability reporting configurado
- [ ] Descrição e tópicos do repositório configurados
- [ ] Screenshot ou GIF de demonstração adicionado

Os itens não marcados exigem uma etapa posterior e não foram executados nesta preparação.

## Arquivos que não devem ser publicados

Por padrão, não incluir:

- `.env`;
- `.venv/`;
- `.gentill/`;
- `.gentill-audit.jsonl`;
- `raw/`;
- `vault/`;
- logs e snapshots locais;
- saídas de diagnóstico;
- resultados temporários de testes;
- scripts one-off vinculados a caminhos absolutos da máquina local de desenvolvimento.

A lista intencional do primeiro commit está em [first-commit-plan.md](first-commit-plan.md) e `PUBLIC_MANIFEST.json`.

## Conteúdo público recomendado

```text
README.md
LICENSE
SECURITY.md
CONTRIBUTING.md
.gitignore
.gitattributes
.github/
app/
db/
docs/
examples/
fixtures/
tests/
Dockerfile
docker-compose.yml
pyproject.toml
.env.example
install-dev.ps1
VALIDATION.json
PUBLIC_MANIFEST.json
```

## Descrição recomendada para o GitHub

> Infraestrutura de inteligência de marcas com FastAPI, PostgreSQL e Model Context Protocol (MCP), com ingestão auditável e similaridade explicável.

## Tópicos recomendados

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

## Gate antes da publicação

Antes do primeiro `git add`, revisar a lista efetiva de arquivos e confirmar que nenhum arquivo ignorado já foi incorporado manualmente.

Após a publicação, o primeiro gate remoto deve ser:

```text
GitHub Actions CI = PASS
```

Somente depois desse resultado deve-se adicionar um badge dinâmico de CI ao README.
