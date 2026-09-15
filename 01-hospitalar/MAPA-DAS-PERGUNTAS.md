# Cobertura — pergunta → visual → justificativa

Este painel aplica os **cinco tipos de visualização especializada** da aula 05
(*Visualizações Especializadas: Além dos Gráficos Tradicionais*) à base de 100 mil
atendimentos hospitalares.

> O exercício original (`../Enunciado.pdf`) pedia os cinco gráficos **tradicionais** —
> barras, colunas, linhas, área e pizza/rosca. Aqueles já foram entregues em
> `../dashboard-hospitalar.html`. Este projeto é o complemento: os cinco formatos que a
> aula 05 apresenta como alternativa, cada um respondendo ao tipo de pergunta para o
> qual foi criado.

## Os cinco tipos e as perguntas que respondem

| # | Tipo | Pergunta principal da aula | Página | Como foi aplicado |
|---|---|---|---|---|
| 1 | **Cartões / KPIs** | Qual é o valor atual do indicador mais importante? | 1 | 8 cartões de leitura rápida + 3 cartões com a anatomia completa (valor, meta, variação, período anterior, tendência) |
| 2 | **Treemap** | Quais categorias possuem maior participação no conjunto? | 2 | Bloco assistencial → Especialidade → Diagnóstico, com drill-down; e um segundo treemap de receita por fonte pagadora |
| 3 | **Mapa** | Onde determinado fenômeno está acontecendo? | 3 | As 4 unidades da rede no DF, bolha proporcional ao volume |
| 4 | **Matriz** | Como os valores se comportam ao cruzar categorias? | 4 | Unidade → Especialidade → Diagnóstico → Procedimento nas linhas × tipo de atendimento nas colunas |
| 5 | **Tabela** | Qual é exatamente o valor de cada informação? | 5 | 12 métricas por especialidade e 7 por unidade |

## Perguntas de negócio respondidas

| # | Pergunta | Página | Visual | Por que essa escolha |
|---|---|---|---|---|
| 1 | Como está a rede hoje, num olhar só? | 1 | 8 cartões | Um cartão é a "primeira leitura": o gestor vê o que importa antes de explorar detalhes |
| 2 | A espera está dentro da meta? | 1 | Cartão com meta e tendência | O número sozinho não decide nada; com meta de 30 min e a curva mensal ao lado, decide |
| 3 | A satisfação está onde deveria? | 1 | Cartão com meta e tendência | Mesma lógica, meta de 4,0 |
| 4 | A operação se paga? | 1 | Cartão com meta e tendência | Margem contra a meta de 30% |
| 5 | O volume está crescendo ou é ruído? | 1 | Linha + média móvel 3M | Série temporal; a média móvel separa tendência de oscilação mensal |
| 6 | Quais especialidades absorvem mais recursos? | 2 | Treemap | Participação proporcional entre 9 especialidades e 32 diagnósticos — a área comunica peso relativo sem exigir leitura de eixo |
| 7 | Dentro da especialidade, qual diagnóstico pesa mais? | 2 | Treemap (drill-down) | A hierarquia está nos dados; o treemap navega nela sem trocar de visual |
| 8 | De onde vem a receita? | 2 | Treemap de convênio | Composição por natureza da fonte pagadora |
| 9 | Onde a rede está instalada e qual unidade concentra volume? | 3 | Mapa de bolhas | A pergunta é de localização; a bolha codifica volume |
| 10 | Quanto exatamente cada unidade atendeu? | 3 | Tabela ao lado do mapa | O mapa aproxima, a tabela precisa — as duas juntas respondem melhor que qualquer uma sozinha |
| 11 | Como cada especialidade se comporta por tipo de atendimento? | 4 | Matriz | Cruzamento de duas dimensões simultâneas, que nenhum gráfico de barras faz sem virar poluição |
| 12 | Do hospital até o procedimento, onde está o gargalo? | 4 | Matriz (drill-down) | Do nível mais agregado ao mais granular sem sair da visualização |
| 13 | Quais os números exatos por especialidade? | 5 | Tabela | 12 métricas por linha; comparação precisa é trabalho de tabela |
| 14 | Quais os números exatos por unidade? | 5 | Tabela | Consulta linha a linha, exportável |
| 15 | Que decisão tirar de tudo isso? | 6 | Textos com os números da base | O *Desafio Final* do enunciado: três insights com a decisão que cada um apoia |

## Requisitos do enunciado

| Exigido | Entregue |
|---|---|
| Importar o dataset | Power Query: consulta de estágio única, tipagem coluna a coluna, cultura pt-BR (decimal com vírgula) |
| Cada gráfico responde a uma pergunta diferente | 15 perguntas mapeadas acima |
| Título que explique claramente o que é apresentado | Todo visual autônomo tem título **e** subtítulo dizendo qual pergunta responde |
| Evitar excesso de cores | Paleta de 5 cores funcionais; categorias sem julgamento (especialidade, mês, unidade) recebem uma cor só |
| Evitar poluição visual | Sem grades verticais nas tabelas, sem legendas redundantes, rótulos de eixo desligados nos sparklines |
| Destacar somente o importante | Semáforo de cor reservado aos 3 indicadores com meta |
| Organizar de forma clara | Toda página segue: título e filtros → KPIs → visual principal → apoio |
| Cores adequadas ao público hospitalar | Azul-petróleo institucional, verde/âmbar/vermelho só com significado clínico ou de meta |
| Desafio final: insight de gestor | Página 6, três insights com números extraídos da própria base |

## Psicologia das cores aplicada

| Cor | Significa | Onde aparece |
|---|---|---|
| Azul-petróleo `#134E5C` | institucional, neutro | títulos, cabeçalhos, KPIs sem carga de julgamento |
| Verde `#2E9B6B` | dentro da meta | margem, indicadores no alvo |
| Âmbar `#E8A33D` | atenção | espera acima da meta, pressão de não programado |
| Vermelho `#C8414F` | negativo | mortalidade, indicadores fora da meta |
| Cinza `#63768A` | secundário | subtítulos, textos de apoio, rótulos de contexto |

Nenhuma série recebe cor só para diferenciar visualmente.

## Modelagem dimensional

Star schema: uma fato cercada por dez dimensões, todas filtrando no sentido único (1 → *).

| Tabela | Linhas | Papel |
|---|---|---|
| `fAtendimento` | 100.000 | fato — chaves estrangeiras e métricas apenas |
| `dCalendario` | 1.096 | datas, marcada como tabela de datas |
| `dHospital` | 4 | unidade, município, UF e coordenadas |
| `dEspecialidade` | 9 | especialidade e bloco assistencial |
| `dDiagnostico` | 32 | condição clínica |
| `dProcedimento` | 17 | procedimento e natureza |
| `dTipoAtendimento` | 3 | eletivo, urgência, emergência |
| `dConvenio` | 5 | fonte pagadora e natureza |
| `dDesfecho` | 4 | alta, retorno, transferência, óbito |
| `dPaciente` | 12 | sexo × faixa etária |
| `dInternacao` | 2 | com e sem internação |
| `_Medidas` | — | 49 medidas DAX, sem dados |

**Por que `Diagnostico` não é filho de `Especialidade`.** Nos dados, o mesmo diagnóstico
aparece em mais de uma área: "Infecção respiratória" ocorre em Clínica Médica e em Pediatria,
"Hipertensão" em Clínica Médica e em Cardiologia. A dependência funcional não existe, então
as duas são dimensões independentes — o treemap usa a hierarquia de exibição, não de modelo.

**O que fica na fato mesmo sendo texto.** `Faixa de Espera`, `Percepção do Paciente` e
`Resultado Financeiro` derivam do valor medido **naquela linha**, não de um atributo
compartilhado. Por isso são colunas calculadas da fato, não dimensões.

## Ressalva honesta sobre o mapa

A própria aula avisa: *"a presença de uma coluna Cidade no dataset não justifica, por si só,
a criação de uma visualização cartográfica."*

Nesta base a geografia é rasa — **4 unidades, 2 municípios, 1 UF** — e o CSV de origem não
traz coordenadas. Duas consequências, ambas declaradas no próprio painel (página 3):

1. As **coordenadas foram atribuídas por unidade** na consulta `dHospital`, dentro do DF.
   Três das quatro unidades ficam em Brasília e colapsariam no mesmo ponto se usássemos
   apenas o município. Elas posicionam a rede de forma plausível; não vieram da fonte.
2. O mapa responde bem a *"onde a rede está instalada e qual unidade concentra volume"* —
   que é um dos usos legítimos citados pela aula (*localização de unidades de atendimento*).
   Ele **não** é o melhor formato para *"qual unidade atende mais"*: para isso a tabela ao
   lado é mais precisa, e é exatamente por isso que ela está ali.
