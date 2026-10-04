# Comunidade

O INPI MCP tenta ser util em tres niveis.

## Para quem desenvolve

- exemplo real de Model Context Protocol sobre um dominio publico;
- separacao entre adapter MCP e regras de negocio;
- FastAPI + SQLAlchemy + PostgreSQL;
- pipeline deterministico de dados;
- hashes e idempotencia;
- mecanismo de similaridade explicavel.

## Para pesquisa e legaltech

- estrutura local consultavel de processos publicados;
- comparacao computacional de sinais;
- classes Nice como contexto;
- rastreabilidade da RPI e do parser.

## Para quem esta aprendendo

Comece por:

1. [Quickstart](quickstart.md);
2. demo `/demo`;
3. [Arquitetura](architecture.md);
4. [Ingestao de RPI](rpi-ingestion.md);
5. [Ferramentas MCP](mcp-tools.md).

## Boas primeiras contribuicoes

Exemplos de evolucoes de baixo risco:

- melhorar testes de layouts XML diferentes;
- internacionalizacao da demo;
- novas explicacoes do score;
- dataset publico de pares de marcas para calibracao;
- benchmarks de desempenho;
- documentacao de classes Nice.

Mudancas de autenticacao, billing, multi-tenant, conclusao juridica ou fonte oficial devem passar por decisao arquitetural.

## Regra de linguagem

Nunca descreva um score do projeto como:

- chance de aprovacao;
- chance de indeferimento;
- parecer juridico;
- decisao do INPI.

A formulacao correta e **similaridade computacional**.
