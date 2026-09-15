# Painel Hospitalar — Visualizações Especializadas

Projeto Power BI (formato **PBIP/PBIR**) pronto para publicar no **Microsoft Fabric**.
Star schema com 10 dimensões, 48 medidas DAX e relatório de 6 páginas.

Aplica os cinco tipos de visualização da aula 05 — **Cartões/KPIs, Treemap, Mapa,
Matriz e Tabela** — à base de 100 mil atendimentos, jan/2024 a jul/2026.

```
                    dCalendario (1.096)
                            |
   dHospital (4) -----+     |     +----- dTipoAtendimento (3)
                      |     |     |
dEspecialidade (9) ---+     |     +----- dConvenio (5)
                      |     |     |
 dDiagnostico (32) ---+  fAtendimento   +--- dDesfecho (4)
                      |   100 mil       |
dProcedimento (17) ---+     |     +----- dPaciente (12)
                            |     |
                      dInternacao (2)
```

A fato guarda apenas chaves estrangeiras e métricas. Todo atributo descritivo
(município, UF, sexo, faixa etária, natureza do convênio) vive nas dimensões.

```
Hospitalar.pbip                      ← abre o projeto no Power BI Desktop
Hospitalar.SemanticModel/            ← modelo: 12 tabelas, 10 relações, 48 medidas DAX
Hospitalar.Report/                   ← relatório: 6 páginas, 75 visuais
dados/hospital_atendimentos_100k.csv ← fonte lida pelo modelo via HTTP
build_report.py + pbir.py            ← geram as páginas PBIR
validar.py                           ← checagens que rodam antes de publicar
MAPA-DAS-PERGUNTAS.md                ← pergunta → visual → justificativa
ROTEIRO-GERAR-PAINEL.md              ← como reproduzir o processo em outro exercício
```

## As seis páginas

| Página | Tipo demonstrado | Pergunta que responde |
|---|---|---|
| 1 · Cartões e KPIs | Cartões / KPIs | Qual é o valor atual do indicador mais importante? |
| 2 · Treemap | Treemap | Quais categorias possuem maior participação? |
| 3 · Mapa | Mapa | Onde o fenômeno está acontecendo? |
| 4 · Matriz | Matriz | Como os valores se comportam ao cruzar categorias? |
| 5 · Tabela | Tabela | Qual é exatamente o valor de cada informação? |
| 6 · Leitura e insights | — | Que decisão tirar de tudo isso? |

A página 1 implementa a lição central da aula: **um número isolado informa, um número com
contexto ajuda a decidir**. Os três cartões centrais carregam os cinco elementos exigidos —
valor atual, meta, variação, período anterior e tendência.

---

## Status: publicado no Fabric

| Item | Link |
|---|---|
| Relatório | https://app.powerbi.com/groups/86e5562b-f700-4471-96e7-7dacb7c7973c/reports/6893f811-0e5f-47c8-9a21-5643307f4414 |
| Semantic model | https://app.powerbi.com/groups/86e5562b-f700-4471-96e7-7dacb7c7973c/datasets/b5e7424b-b0b2-4995-b236-166c95b15737 |

Workspace **Hospitalar CEUB**. Publicado pela REST API, refresh completo com as 100 mil
linhas, e os dez indicadores conferidos por consulta DAX contra o cálculo local.

## Fonte de dados

O CSV é lido por HTTP, com credencial anônima — sem gateway e sem OneDrive. Dois parâmetros
do modelo controlam isso:

| Parâmetro | Valor |
|---|---|
| `pUrlBase` | `https://raw.githubusercontent.com` |
| `pCaminhoCSV` | `guilhermelevi/visualizacao-dados-CEUB-2026/main/01-hospitalar/dados/hospital_atendimentos_100k.csv` |

> Se o repositório voltar a ser privado, o refresh quebra: a URL raw precisa de acesso anônimo.
>
> Para abrir só no Desktop, sem nuvem, troque a consulta `Fonte` por
> `Csv.Document( File.Contents("...\dados\hospital_atendimentos_100k.csv"), ... )`.
> Caminho local **não funciona** no Service.

O arquivo usa `;` como separador e **vírgula decimal** — por isso a tipagem passa
`"pt-BR"` como cultura. Sem isso, `1272,01` vira `127201`.

---

## Publicar no Fabric

Pela REST API, sem precisar de Git integration nem de Desktop:

```
POST /v1/workspaces/{ws}/semanticModels     ← cria o modelo (TMDL em base64)
POST /v1/workspaces/{ws}/reports            ← cria o relatório (PBIR em base64)
PATCH /v1.0/myorg/gateways/{gw}/datasources/{ds}   ← credencial anônima
POST /v1.0/myorg/groups/{ws}/datasets/{id}/refreshes
```

Autenticação por device code, sem instalar nada:

```bash
curl -X POST "https://login.microsoftonline.com/common/oauth2/v2.0/devicecode" \
  -d "client_id=04b07795-8ddb-461a-bbee-02f9e1bf7b46" \
  -d "scope=https://api.fabric.microsoft.com/.default offline_access"
```

**Antes de publicar, rode as checagens:**

```bash
python3 validar.py
```

Confere que todo campo referenciado nos 75 visuais existe no modelo, que os schemas do PBIR
estão nas versões que renderizam, que nenhum visual extrapola a página e que os cinco tipos
da aula estão presentes. São exatamente os erros que **passam no import e quebram em silêncio**.

**Depois de publicar**, valide de verdade: uma consulta DAX (`/executeQueries`) para conferir
os números, um export PDF (`/ExportTo`) — se travar em 0%, o relatório está quebrado — e a
leitura do PDF visual a visual. A terceira é a que pega mais coisa.

---

## Entregar o `.pbix`

**Já está pronto** em `../ENTREGA/Hospitalar.pbix` — 4 MB, com o `DataModel` embutido,
abre em qualquer Power BI Desktop sem depender do Fabric. Foi exportado do Service com:

```
GET /v1.0/myorg/groups/{ws}/reports/{id}/Export
```

> O `.pbix` é um retrato, não um link. Se o painel mudar, exporte de novo.

Entregue também o `hospital_atendimentos_100k.csv`, que está na mesma pasta.

---

## Regenerar as páginas

```bash
python3 build_report.py   # reescreve definition/pages/ inteiro
python3 validar.py        # e confere o resultado
```

Os nomes dos visuais vêm de um contador determinístico, então rodar de novo produz
exatamente os mesmos arquivos — o diff do git mostra só o que mudou de verdade.

---

## Se algo der errado

| Sintoma | Causa provável | O que fazer |
|---|---|---|
| Refresh falha com "arquivo não encontrado" | O repositório do `pCaminhoCSV` não existe ou é privado | A URL raw precisa de acesso anônimo — crie e torne público, ou troque os parâmetros |
| Valores monetários 100× maiores | Cultura da tipagem não é pt-BR | A vírgula do CSV é decimal, não separador de milhar |
| Refresh falha com `column does not exist in the rowset` | `sourceColumn` usa o nome anterior ao rename no Power Query | Conferir o nome **depois** do `Table.RenameColumns` — `validar.py` checa isso |
| Import rejeitado com `Property 'description' is unknown` | Um comentário `///` acima de um `relationship` | Descrição só vale em tabela, coluna, medida e parâmetro |
| Relatório abre em branco, com skeleton infinito | Schemas do PBIR em versão antiga | Ver a tabela de versões em `ROTEIRO-GERAR-PAINEL.md`; `validar.py` checa isso |
| Mapa sem bolhas | Latitude/Longitude entraram como coluna direta | Precisam ser agregação **Average** — é como estão no `visual.json` |
| Eixos em ordem alfabética (abr, ago, dez…) | Falta `sortByColumn` | Já definido em `dCalendario`, `dTipoAtendimento`, `dConvenio`, `dDesfecho`, `dPaciente`, `dInternacao` |

As cores de cada visual estão definidas visual a visual, então o painel fica correto mesmo
que o tema base não carregue.

## Reproduzir este processo

`ROTEIRO-GERAR-PAINEL.md` descreve o pipeline completo, do enunciado ao painel publicado,
com as armadilhas de formato que falham em silêncio.
