# Política de segurança

## Estado do projeto

O INPI MCP permanece em estágio técnico de DEV e **não é considerado pronto para produção**.

## Endpoint administrativo

`POST /v1/admin/ingest/xml` é uma facilidade local de DEV.

Desde a 0.3.1 ele fica **fechado por padrão** e só responde quando as duas condições são verdadeiras:

```text
APP_ENV=dev
ENABLE_DEV_ADMIN_INGEST=true
```

Mesmo quando habilitado, o endpoint não aparece no OpenAPI.

O `docker-compose.yml` habilita essa opção explicitamente apenas para o quickstart DEV.

## Concorrência de ingestão

No PostgreSQL, fluxos mutantes de RPI usam advisory lock para serializar a ingestão.

Uma segunda execução concorrente não espera indefinidamente nem disputa o cursor: ela falha rapidamente.

O lock é validado contra PostgreSQL real na CI.

## Monitor de novas RPIs

O monitor remoto:

- não possui credenciais de banco;
- não faz ingestão automática;
- usa apenas `contents: read` e `issues: write`;
- não interpreta HTTP 5xx do INPI como ausência de publicação;
- não cria RPI ou issue falsa quando a fonte está indisponível.

## Relato de vulnerabilidades

Não publique segredos, credenciais, dados pessoais ou detalhes de exploração em issues públicas.

Prefira um Private Vulnerability Report / Security Advisory quando disponível.

## Ainda fora do escopo

Não estão concluídos para produção:

- autenticação completa;
- autorização;
- isolamento multi-tenant;
- rate limiting;
- observabilidade de produção;
- revisão completa de LGPD;
- rotação operacional de segredos;
- hardening de infraestrutura de produção.

## Credenciais locais

As credenciais do `docker-compose.yml` são valores locais de DEV e não devem ser reutilizadas em HML ou produção.

Arquivos `.env`, fontes brutas, logs, diretórios `.gentill/` e evidências locais são excluídos da publicação.

## Dados do INPI

O projeto preserva a distinção entre:

- informação oficial da fonte;
- dado normalizado pelo sistema;
- score computacional;
- interpretação jurídica.

Um score de similaridade nunca deve ser apresentado como decisão oficial ou probabilidade garantida de deferimento.
