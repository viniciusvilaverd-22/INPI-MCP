# Contribuindo

O INPI MCP está sendo mantido como projeto técnico de portfólio e pesquisa aplicada.

## Antes de propor uma mudança

Abra uma issue descrevendo problema, comportamento esperado, impacto, evidências ou referências e riscos de compatibilidade.

Evite PRs grandes ou refatorações sem discussão prévia.

## Requisitos para código

Mudanças devem:

- preservar idempotência;
- manter provenance e versionamento;
- não misturar lógica de domínio com o adapter MCP;
- não transformar score computacional em conclusão jurídica;
- incluir ou atualizar testes quando aplicável;
- não adicionar credenciais, dados pessoais ou fontes brutas ao Git.

## Testes

```bash
pip install -e ".[test,mcp]"
pytest -q
```

Também deve ser possível importar o servidor MCP:

```bash
python -c "from app.mcp_server import mcp; print(type(mcp).__name__)"
```

## Escopo

Mudanças relacionadas a autenticação, multi-tenant, billing, ingestão de fontes reais ou contratos públicos devem ser tratadas como decisões arquiteturais, não como ajustes casuais.
