# Cobertura do enunciado

O exercício exige **no mínimo 8 perguntas**. Este dashboard responde **as 15**.

| # | Pergunta | Página | Visualização escolhida | Por que essa escolha |
|---|---|---|---|---|
| 1 | Rotas com maior quantidade de passageiros | 3 · Comercial | Barras horizontais | Comparação de grandeza entre categorias com rótulos longos; a barra horizontal preserva a legibilidade do nome da rota |
| 2 | Evolução dos passageiros no período | 1 · Executiva | Linha + média móvel 3M | Série temporal contínua; a média móvel separa tendência de ruído mensal |
| 3 | Aeroportos que concentram mais voos | 1 · Executiva | Barras horizontais | Ranking direto entre 20 aeroportos |
| 4 | Concentração geográfica da operação | 1 · Executiva | Mapa de bolhas | A pergunta é explicitamente espacial; o tamanho da bolha codifica volume |
| 5 | Participação de pontuais, atrasados e cancelados | 1 · Executiva | Rosca | Composição de um todo com apenas 3 partes — caso em que a rosca funciona bem |
| 6 | Rotas com maiores atrasos médios | 2 · Operação | Barras horizontais (top 15) | Ranking; corte em 15 rotas com pelo menos 10 voos evita distorção por amostra pequena |
| 7 | Distribuição dos tempos de atraso | 2 · Operação | Colunas (histograma) | A pergunta é sobre distribuição, não sobre ranking; as faixas ordenadas revelam a cauda longa |
| 8 | Voos com atraso fora do normal | 2 · Operação | Dispersão | Outliers só aparecem quando cada voo é um ponto; a nuvem mostra o comportamento normal e o que escapa dele |
| 9 | Relação entre distância e preço | 3 · Comercial | Dispersão | Duas variáveis contínuas — o formato natural para inspecionar correlação |
| 10 | Relação entre ocupação e lucratividade | 3 · Comercial | Dispersão com legenda por faixa | Mesma lógica; a cor por faixa de ocupação evidencia o ponto de virada |
| 11 | Motivos de atraso e cancelamento | 2 · Operação | Barras horizontais ordenadas | Prioriza causas por frequência — leitura de Pareto |
| 12 | Rotas com alto volume **e** alta receita | 3 · Comercial | Dispersão com bolha | Pergunta de duas dimensões simultâneas; o tamanho da bolha acrescenta o lucro como terceira |
| 13 | Comparação entre tipos de aeronave | 3 · Comercial | Tabela | Cinco atributos por modelo; a tabela permite comparar valores exatos sem competir por espaço |
| 14 | Principais indicadores gerais | todas | Cartões de KPI | 7 a 8 cartões no topo de cada página, com cor semântica |
| 15 | Desempenho detalhado das rotas | 4 · Detalhamento | Matriz hierárquica | Consulta linha a linha com origem → destino expansível |

## Requisitos técnicos

| Exigido | Entregue |
|---|---|
| Dataset próprio, mínimo 5.000 registros | 6.200 voos, 370 rotas, 20 aeroportos, 2 anos |
| Importação e tratamento no Power BI | Power Query: tipagem por coluna, remoção de linhas vazias, dimensão de aeroportos derivada dos pares origem/destino |
| Mínimo 8 perguntas respondidas | 15 |
| Mínimo 8 visualizações | 20 gráficos + 29 cartões de KPI |
| Mínimo 3 tipos de gráfico | 9 tipos: rosca, linha, barras, colunas, combinado, mapa, dispersão, tabela, matriz |
| Mínimo 3 KPIs em cartões | 29 cartões |
| Mínimo 2 filtros/segmentadores | 8 segmentadores (2 por página analítica) |
| Títulos explicativos | Todos os visuais têm título e subtítulo indicando a pergunta respondida |
| Organizado para público executivo | Topo: título e filtros → KPIs → análises → detalhamento → insights |
| Parte 4: 3 insights com decisão | Página 5, com números extraídos da própria base |

## Psicologia das cores aplicada

A paleta é funcional, não decorativa:

| Cor | Uso | Onde |
|---|---|---|
| Azul `#123A5E` | institucional, neutro | títulos, cabeçalhos, KPIs sem carga de julgamento |
| Verde `#2E9B6B` | positivo | voos pontuais, lucro, margem |
| Âmbar `#E8A33D` | atenção | voos atrasados, atraso médio |
| Vermelho `#C8414F` | negativo | cancelamentos, prejuízo, causas de falha |
| Cinza `#63768A` | secundário | textos de apoio, custo, eixos |

Nenhuma série recebe cor só para diferenciar visualmente: quando a categoria não carrega julgamento
(região, aeronave, competência), a cor é um azul neutro único.


## Modelagem dimensional

Star schema: uma fato cercada por seis dimensões, todas filtrando no sentido único (1 → *).

| Tabela | Linhas | Papel |
|---|---|---|
| `fVoos` | 6.200 | fato — chaves estrangeiras e métricas apenas |
| `dCalendario` | 1.096 | datas, marcada como tabela de datas |
| `dRota` | 370 | origem, destino, extensão, faixa de distância |
| `dAeroporto` | 20 | cidade, UF, região, coordenadas |
| `dMotivo` | 9 | causa, natureza (externa/interna/comercial), controlabilidade |
| `dAeronave` | 6 | modelo, fabricante, capacidade, porte |
| `dSituacao` | 3 | pontual, atrasado, cancelado — com ordem de exibição |

As únicas colunas descritivas que permanecem na fato são as **faixas derivadas da
própria linha** (faixa de atraso, faixa de ocupação, resultado do voo). Elas dependem
do valor medido naquele voo, não de um atributo compartilhado, então pertencem à fato.

A dimensão `dAeroporto` cobre origem **e** destino: a query une os dois conjuntos antes
de aplicar `Table.Distinct`, para que a dimensão descreva a malha inteira.

Todas as tabelas derivam de uma **consulta de estágio** (`Fonte`), que lê e tipa o CSV
uma única vez — o arquivo não é baixado sete vezes no refresh.
