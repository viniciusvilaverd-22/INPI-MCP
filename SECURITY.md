# Política de segurança

## Estado do projeto

O INPI MCP está em estágio de MVP técnico e **não é considerado pronto para produção**.

O endpoint administrativo de ingestão existe para DEV e não deve ser exposto diretamente à Internet no estado atual.

## Relato de vulnerabilidades

Não publique segredos, credenciais, dados pessoais ou detalhes de exploração em issues públicas.

Quando o repositório estiver hospedado no GitHub, prefira um **Private Vulnerability Report / Security Advisory**, se a funcionalidade estiver habilitada. Se não estiver, abra apenas uma issue sem detalhes sensíveis solicitando um canal privado com o mantenedor.

## Escopo de segurança desta release

Ainda não estão concluídos:

- autenticação;
- autorização;
- isolamento multi-tenant;
- rate limiting;
- hardening do endpoint administrativo;
- observabilidade de produção;
- revisão completa de LGPD;
- política operacional de rotação de segredos.

## Credenciais locais

As credenciais presentes no `docker-compose.yml` são valores de desenvolvimento local e não devem ser reutilizadas em HML ou produção.

Arquivos `.env`, fontes brutas, logs, diretórios `.gentill/` e evidências locais são excluídos da publicação por `.gitignore`.

## Dados do INPI

O projeto deve preservar a distinção entre:

- informação oficial da fonte;
- dado normalizado pelo sistema;
- score computacional;
- interpretação jurídica.

Um score de similaridade nunca deve ser apresentado como decisão oficial ou probabilidade garantida de deferimento.
