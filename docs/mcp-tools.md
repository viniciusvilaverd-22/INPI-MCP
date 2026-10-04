# Ferramentas MCP

O servidor atual está em `app/mcp_server.py` e usa `app/mcp_adapter.py` para acessar o domínio.

## 1. `search_trademark`

Pesquisa marcas conhecidas na base.

### Entrada

```json
{
  "query": "GENTILL MOB",
  "nice_classes": [39],
  "limit": 20
}
```

A resposta contém a consulta e os candidatos encontrados, incluindo processo, marca, classes e score de similaridade quando aplicável.

## 2. `compare_trademark`

Compara diretamente dois sinais.

### Entrada

```json
{
  "left_name": "GENTILL MOB",
  "right_name": "GENTIL MOB",
  "left_classes": [39],
  "right_classes": [39]
}
```

### Saída

Retorna a decomposição do motor `sim-v0.1.0`:

- `overall`;
- `lexical`;
- `phonetic`;
- `token_structure`;
- `semantic`;
- `market_affinity`;
- `reasons`;
- `engine_version`.

## 3. `get_trademark`

Consulta um processo já presente na base.

### Entrada

```json
{
  "process_number": "123456789"
}
```

Quando o processo não existe, o adapter retorna `found: false`.

## Princípio arquitetural

O MCP não é o núcleo do produto.

```text
cliente MCP
    -> MCP server
        -> adapter
            -> domínio
```

A mesma lógica também é exposta por REST, reduzindo duplicação e facilitando testes.

## Ferramentas planejadas, não implementadas nesta release

- sugestão de classes de Nice;
- criação de monitoramento;
- consulta de eventos de monitoramento;
- operações relacionadas a billing.

Essas capacidades constam no roadmap e não devem ser confundidas com o runtime atual.
