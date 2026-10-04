# Monitoramento automatico de novas RPIs

A 0.3.0 adiciona o workflow:

```text
.github/workflows/rpi-monitor.yml
```

## Objetivo

Detectar uma nova RPI oficialmente publicada sem:

- baixar antecipadamente o ZIP de uma edicao futura;
- ingerir dados;
- acessar banco;
- tocar em producao.

## Fonte de deteccao

O monitor usa o indice oficial:

```text
https://revistas.inpi.gov.br/rpi/
```

A CLI correspondente e:

```bash
python -m app.cli latest-rpi
```

O parser aceita as duas representacoes de data observadas no indice oficial:

```text
2026-09-29
29/09/2026
```

O endpoint direto `/txt/RM<numero>.zip` continua sendo usado para download e ingestao, mas nao para adivinhar se uma edicao futura ja foi publicada.

## Funcionamento

Em dias uteis, o GitHub Actions:

1. identifica a maior RPI ja registrada por issues com label `rpi-monitor`;
2. usa 2908 como baseline inicial quando ainda nao existe issue;
3. consulta o indice oficial da RPI;
4. extrai o maior numero publicado;
5. se o indice estiver a frente do baseline, abre um issue unico para cada nova edicao;
6. se nao houver nova publicacao, encerra com sucesso sem criar issue.

## Por que o indice e a fonte do monitor

Uma URL futura de ZIP pode responder com erro temporario do servidor, por exemplo HTTP 503, mesmo sem a edicao ter sido publicada.

O indice oficial representa a lista de revistas efetivamente publicadas e evita transformar comportamento de infraestrutura do endpoint de arquivo em sinal de publicacao.

## Estado do monitor

O historico de issues funciona como cursor remoto de deteccao.

```text
baseline inicial: 2908
indice oficial:  2908
resultado:        nenhuma issue

quando o indice publicar 2909:
detecta 2909 -> cria issue "Nova RPI detectada: 2909"
```

Esse cursor **nao e** `last_ingested_rpi`.

## Separacao de responsabilidades

```text
Indice oficial
  -> monitor detecta publicacao
  -> cria issue

CLI / ambiente autorizado
  -> baixa ZIP oficial
  -> valida ZIP/XML e hashes
  -> ingere
  -> atualiza last_ingested_rpi
```

Portanto uma publicacao detectada nunca e tratada automaticamente como ingerida.

## Permissoes

O workflow usa apenas:

```yaml
permissions:
  contents: read
  issues: write
```

Nao usa secrets de banco nem credenciais de producao.

## Execucao

O workflow possui:

- agenda em dias uteis;
- `workflow_dispatch`;
- auto-teste quando o proprio `rpi-monitor.yml` e alterado na `main`.

O gatilho por push usa filtro de caminho e nao executa em commits normais do projeto.

## Diagnostico de ZIP

O comando anterior continua disponivel para diagnosticos pontuais:

```bash
python -m app.cli discover-rpi --after 2908 --max-scan 4
```

Ele consulta diretamente os arquivos ZIP e nao e usado pelo monitor agendado.
