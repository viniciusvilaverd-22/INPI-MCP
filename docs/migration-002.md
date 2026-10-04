# Migration 002 — specification_hash

A migration `db/002_specification_hash.sql` atualiza bancos PostgreSQL persistentes criados antes do INPI MCP 0.2.1.

## Motivo

A RPI 2908 mostrou especificacoes Nice com milhares de caracteres. PostgreSQL nao consegue usar valores TEXT muito grandes diretamente em uma chave UNIQUE B-tree.

A nova estrutura preserva o texto integral e usa SHA-256 somente para a chave de idempotencia.

## Aplicacao

Em DEV:

```bash
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f db/002_specification_hash.sql
```

## Comportamento

A migration:

1. habilita `pgcrypto`;
2. exige que `trademark_nice_class` ja exista;
3. adiciona `specification_hash VARCHAR(64)`;
4. faz backfill com SHA-256 de `COALESCE(specification, '')`;
5. detecta grupos duplicados antes de trocar a unicidade;
6. define a coluna como NOT NULL;
7. remove `uq_tm_class_spec`;
8. cria `uq_tm_class_spec_hash`.

Se houver duplicatas equivalentes, a migration **aborta** para revisao manual. Ela nao exclui dados.

## Fresh install

Instalacoes novas nao precisam executar a migration manualmente: o modelo SQLAlchemy atual ja cria `specification_hash` e a nova restricao.

## Validacao

A CI cria um schema legado real em PostgreSQL 16, aplica a migration, preserva dados preexistentes, insere uma especificacao longa e reaplica a migration para confirmar idempotencia.
