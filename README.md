# Dashboard Executivo — Companhia Aérea

Projeto Power BI (formato **PBIP/PBIR**) pronto para sincronizar no **Microsoft Fabric** via Git.
Star schema com 6 dimensões, 44 medidas DAX e relatório de 5 páginas.

**Modelo:**

```
            dCalendario (1.096)
                   |
 dAeroporto (20) --+-- dRota (370)
                   |
       fVoos  ·  6.200 voos  ·  só chaves e métricas
                   |
 dAeronave (6) ----+-- dSituacao (3) -- dMotivo (9)
```

A fato guarda apenas chaves estrangeiras e métricas. Todo atributo descritivo
(cidade, UF, região, fabricante, porte, natureza da causa) vive nas dimensões.

```
CompanhiaAerea.pbix                  ← ENTREGÁVEL: abre em qualquer Power BI Desktop
CompanhiaAerea.pbip                  ← o mesmo projeto em formato de pastas (versionável)
CompanhiaAerea.SemanticModel/        ← modelo: tabelas, relações, 44 medidas DAX
CompanhiaAerea.Report/               ← relatório: 5 páginas, 62 objetos
dados/companhia_aerea_voos.csv       ← fonte lida pelo modelo via HTTP
ROTEIRO-GERAR-PAINEL.md              ← como reproduzir este processo em outro exercício
```

> O `.pbix` foi exportado do Service com `GET /v1.0/myorg/groups/{ws}/reports/{id}/Export`
> e contém o DataModel embutido — abre sem depender do Fabric.

---

## Status: já publicado no Fabric

O projeto **já está no ar** no workspace `Companhia Aerea CEUB`, publicado via Fabric REST API.

| Item | Link |
|---|---|
| Relatório | https://app.powerbi.com/groups/21e91615-1c27-4a73-ae1a-887ba415aa68/reports/d69a0523-657f-44dd-8775-cfd3c2152603 |
| Semantic model | https://app.powerbi.com/groups/21e91615-1c27-4a73-ae1a-887ba415aa68/datasets/97697c03-8626-491e-99b9-8aa51a9edb21 |

**Fonte de dados:** o CSV é lido por HTTP da URL pública deste próprio repositório
(`dados/companhia_aerea_voos.csv`), com credencial anônima. Não há gateway nem OneDrive envolvidos,
e a atualização agendada funciona sem configuração adicional.

Os dois parâmetros do modelo controlam isso:

| Parâmetro | Valor |
|---|---|
| `pUrlBase` | `https://raw.githubusercontent.com` |
| `pCaminhoCSV` | `guilhermelevi/dashboard-companhia-aerea-CEUB-2026/main/dados/companhia_aerea_voos.csv` |

> Se o repositório voltar a ser privado, o refresh quebra. Nesse caso troque a fonte para OneDrive
> ou embuta os dados no modelo.

### Republicar depois de editar os arquivos

Alterou algum `.tmdl` ou `visual.json`? Basta reenviar a definição pela API — não precisa de Git integration
(o admin do tenant do CEUB mantém a integração com GitHub desabilitada de qualquer forma).

---

## Entregar o `.pbix`

O enunciado pede o arquivo `.pbix`. Duas rotas:

**A. Baixar do Service** — no relatório: **Arquivo → Baixar este arquivo → .pbix**.
Nem todo semantic model criado pela web libera esse download. Se a opção estiver cinza, use a rota B.

**B. Abrir o projeto no Desktop** — em qualquer máquina Windows (laboratório da faculdade serve),
dê duplo clique em `CompanhiaAerea.pbip` e faça **Arquivo → Salvar como → .pbix**. Leva 30 segundos.

Entregue também o `companhia_aerea_voos.csv`.

---

## Se algo der errado

| Sintoma | Causa provável | O que fazer |
|---|---|---|
| Refresh falha com "arquivo não encontrado" | O repositório voltou a ser privado | A URL raw precisa de acesso anônimo — torne o repo público ou troque a fonte |
| Refresh falha com "column does not exist in the rowset" | `sourceColumn` usa o nome anterior ao rename no Power Query | Conferir o nome **depois** do `Table.RenameColumns` |
| Import rejeitado com `Property 'description' is unknown` | Um comentário `///` acima de um `relationship` | Descrição só vale em tabela, coluna, medida e parâmetro |
| Relatório abre em branco, com skeleton infinito | Schemas do PBIR em versão antiga | Ver a tabela de versões em `ROTEIRO-GERAR-PAINEL.md` |
| Credencial da fonte | Web anônima, sem gateway | Configurações do semantic model → Editar credenciais → Anônimo |

As cores de cada gráfico estão definidas visual a visual, então o dashboard fica correto
mesmo que o tema base não carregue.

## Reproduzir este processo

`ROTEIRO-GERAR-PAINEL.md` descreve o pipeline completo, do enunciado ao painel publicado,
com as armadilhas de formato que falham em silêncio.
