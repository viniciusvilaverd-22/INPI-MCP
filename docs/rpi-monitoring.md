# Monitoramento automatico de novas RPIs

A 0.3.0 adiciona o workflow:

```text
.github/workflows/rpi-monitor.yml
```

## Objetivo

Detectar que uma nova RPI oficial passou a existir sem:

- baixar o ZIP completo;
- ingerir dados;
- acessar banco;
- tocar em producao.

## Funcionamento

Em dias uteis, o GitHub Actions:

1. identifica a maior RPI ja registrada por issues com label `rpi-monitor`;
2. usa 2908 como baseline inicial quando ainda nao existe issue;
3. consulta no maximo quatro numeros sequenciais;
4. tenta `HEAD` na URL oficial;
5. se o servidor recusar `HEAD`, usa `GET` com `Range: bytes=0-0`;
6. para na primeira RPI indisponivel;
7. abre um issue unico para cada nova RPI encontrada.

## Estado do monitor

O historico de issues funciona como cursor do monitor remoto.

Exemplo:

```text
baseline inicial: 2908
detecta 2909 -> cria issue "Nova RPI detectada: 2909"
proxima execucao -> inicia depois de 2909
```

Esse cursor de deteccao **nao e** `last_ingested_rpi`.

## Separacao de responsabilidades

```text
GitHub monitor
  -> detecta existencia
  -> cria issue

CLI / ambiente autorizado
  -> baixa
  -> valida hashes
  -> ingere
  -> atualiza last_ingested_rpi
```

Portanto uma publicacao detectada nunca e tratada automaticamente como ingerida.

## Permissoes

O workflow usa:

```yaml
permissions:
  contents: read
  issues: write
```

Nao usa secrets de banco, credenciais de producao ou tokens externos.

## Execucao manual

O workflow tambem oferece `workflow_dispatch` para prova controlada.

A consulta equivalente pela CLI e:

```bash
python -m app.cli discover-rpi --after 2908 --max-scan 4
```

## Falhas

Erros de rede diferentes de ausencia normal da publicacao fazem o job falhar. Isso evita transformar indisponibilidade da fonte em falso estado de "nao existe".

Um HTTP 404 e tratado como RPI ainda indisponivel.
