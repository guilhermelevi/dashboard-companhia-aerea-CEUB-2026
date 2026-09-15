# Roteiro — gerar um painel do zero

Playbook para produzir um dashboard completo a partir de um enunciado.
Escrito depois de construir o painel da companhia aérea; as armadilhas listadas aqui
são as que realmente apareceram, não as que a documentação avisa.

---

## 1. O que me mandar

O mínimo:

- **O enunciado** (PDF, print ou texto colado). Eu leio inteiro antes de começar.
- **Os dados**, se já existirem. Se não, eu gero — diga o tema e o volume.

Se souber, diga também:

| Informação | Por que muda o resultado |
|---|---|
| Onde vai rodar | Fabric online, Desktop, ou só um HTML local — muda tudo |
| Se precisa entregar `.pbix` | Define se dá para publicar por API ou precisa de Desktop |
| Prazo | Define se vale caprichar no visual ou entregar o essencial |
| Se a interface está em inglês | Para eu dar os nomes certos dos botões |

Se não disser nada, eu assumo Fabric online e pergunto só o que for bloqueante.

---

## 2. O que eu faço, em ordem

### Etapa 1 — Ler e mapear

Leio o enunciado e monto uma **tabela de cobertura**: cada pergunta → qual visual
responde → por quê. Essa tabela vira um `.md` na entrega, porque a justificativa da
escolha do gráfico costuma valer nota.

Também extraio a lista de requisitos técnicos (mínimo de visuais, de KPIs, de filtros)
e trato como checklist.

### Etapa 2 — Dados

Se o dataset não existe, eu gero com variação realista: sazonalidade, outliers,
categorias com pesos diferentes, alguns valores extremos. Datasets onde tudo se
comporta igual não respondem perguntas analíticas.

Se já existe, **eu valido antes de modelar**: contagem, período, distribuições,
percentual de nulos, cardinalidade. Isso evita descobrir na última hora que 30% de
uma coluna está vazia.

### Etapa 3 — Modelo

Star schema de verdade: **a fato guarda apenas chaves estrangeiras e métricas**. Todo
atributo descritivo vai para uma dimensão.

O teste é simples: se a coluna descreve *o que a entidade é* (cidade, região, fabricante,
porte, natureza da causa), ela pertence à dimensão. Se ela mede *o que aconteceu naquela
linha* (passageiros, receita, atraso), fica na fato.

A exceção são as **faixas derivadas da própria linha** — faixa de atraso, faixa de
ocupação, resultado do voo. Dependem do valor medido naquele registro, não de um atributo
compartilhado, então ficam na fato mesmo sendo texto.

> É fácil produzir uma flat table e chamá-la de star schema. Se a fato tem 40 colunas e
> só duas dimensões penduradas, não é star schema — é uma tabela larga. O sinal mais claro
> é encontrar `cidade`, `uf`, `região` ou `ano/mês/dia` dentro da fato.

Demais regras:

- Calendário próprio, marcado como tabela de datas (nunca a hierarquia automática)
- Uma **consulta de estágio** que lê e tipa o arquivo **uma vez só**; a fato e as dimensões
  derivam dela. Sem isso, sete tabelas baixam o mesmo arquivo sete vezes no refresh
- Dimensão de local deve cobrir origem **e** destino: unir os dois conjuntos antes do
  `Table.Distinct`
- Medidas em DAX, agrupadas em pastas por assunto
- Descrição em toda medida e coluna — vira tooltip e ajuda na apresentação
- Colunas de ordenação (`sortByColumn`) nas dimensões: fazem legendas e eixos saírem na
  ordem lógica em vez de alfabética, de graça

### Etapa 4 — Visual

Layout em camadas, de cima para baixo: **título e filtros → KPIs → análises → detalhamento**.

Cores com função, não decoração:

| Cor | Significa |
|---|---|
| Azul escuro | institucional, neutro |
| Verde | positivo (lucro, pontualidade) |
| Âmbar | atenção (atrasos) |
| Vermelho | negativo (cancelamento, prejuízo) |
| Cinza | secundário, apoio |

Quando a categoria não carrega julgamento (região, mês, modelo), uso **uma cor só**.

Todo visual leva título e subtítulo dizendo **qual pergunta responde**.

Medidas que valem lembrar: um slicer em dropdown precisa de **~50px de altura** para o
cabeçalho e a caixa caberem — com menos, o dropdown sai cortado. A faixa de título que
os abriga precisa de ~80px.

### Etapa 5 — Publicar

No Fabric, pela REST API — não precisa de Git integration nem de Desktop:

```
POST /v1/workspaces/{ws}/semanticModels     ← cria o modelo (TMDL em base64)
POST /v1/workspaces/{ws}/reports            ← cria o relatório (PBIR em base64)
PATCH /v1.0/myorg/gateways/{gw}/datasources/{ds}   ← credencial
POST /v1.0/myorg/groups/{ws}/datasets/{id}/refreshes
```

Autenticação sem instalar nada, via device code:

```bash
curl -X POST "https://login.microsoftonline.com/common/oauth2/v2.0/devicecode" \
  -d "client_id=04b07795-8ddb-461a-bbee-02f9e1bf7b46" \
  -d "scope=https://api.fabric.microsoft.com/.default offline_access"
```

Você abre o link, digita o código, e eu sigo daí.

### Etapa 6 — Validar de verdade

Publicar sem erro **não significa que funciona**. Três checagens:

1. **Consulta DAX** (`/executeQueries`) — confere se os números batem com a análise local.
   Depois de refatorar o modelo, rodar os mesmos KPIs antes e depois: se algum número
   mudou, a refatoração quebrou alguma relação
2. **Export PDF** (`/ExportTo`) — se travar em 0%, o relatório está quebrado
3. **Eu leio o PDF** e olho cada visual

A terceira é a que pega mais coisa. No painel aéreo ela revelou o mapa com erro,
formas com a cor errada e categorias esmagando o gráfico — nada disso aparece em log.

---

## 3. Armadilhas (custaram tempo de verdade)

### Formato PBIR

Schemas `1.0.0` **são aceitos no import e não renderizam**. O relatório abre em branco,
com skeleton infinito, e o export trava em 0% sem mensagem de erro.

| Arquivo | Versão que funciona |
|---|---|
| `definition.pbir` | `report/definitionProperties/2.0.0` — sem `/definition/` no caminho |
| `definition/version.json` | campo `version: "2.0.0"` |
| `definition/report.json` | `report/3.3.0` |
| `pages/<p>/page.json` | `page/2.1.0` |
| `visuals/<v>/visual.json` | `visualContainer/2.12.0` |
| `pages/pages.json` | `pagesMetadata/1.1.0` |

> **Como descobrir a versão certa a qualquer momento:** criar um relatório trivial pela
> interface do Fabric e baixar sua definição com
> `POST /v1/workspaces/{ws}/reports/{id}/getDefinition`. Esse é o gabarito. Não confie
> na documentação, que fica atrás da versão em produção.

### Outras que quebram em silêncio

- `themeCollection` é obrigatório. O `baseTheme` precisa do **arquivo físico** em
  `StaticResources/SharedResources/BaseThemes/`, e `reportVersionAtImport` é um
  **objeto** `{visual, report, page}`, não uma string.
- `byConnection` moderno tem só `connectionString`, terminando em `semanticmodelid=<guid>`.
- Visuais `shape` **ignoram** a cor que você define. Use `textbox` com
  `visualContainerObjects.background`.
- Mapas exigem Latitude/Longitude como **agregação Average**, não coluna direta.
- No TMDL, `variation` numa coluna de data exige `showAsVariationsOnly` na tabela alvo —
  mais simples remover a variation.
- Em f-string de Python, `{{tag()}}` vira o literal `{tag()}` no arquivo. Isso derrubou
  o primeiro import.

### No TMDL do modelo

- **`relationship` não aceita descrição.** Um comentário `///` acima de um relacionamento
  faz o import inteiro falhar com `Property 'description' is unknown` — e a mensagem não
  diz onde está o problema. Descrição só em tabela, coluna, medida e parâmetro.
- **`sourceColumn` usa o nome depois do rename.** Se a query M faz
  `Table.RenameColumns(…, {{"motivo_original","Motivo"}})`, a coluna precisa de
  `sourceColumn: Motivo`. Com o nome antigo o modelo importa sem erro e só o **refresh**
  falha, com `column does not exist in the rowset`.

### Fonte de dados na nuvem

`File.Contents` com caminho local **não funciona** no Service. Opções, da mais simples:

1. **URL pública** (`Web.Contents` com `RelativePath`) + credencial anônima — eu configuro tudo por API
2. **OneDrive/SharePoint** (`SharePoint.Files`) — você precisa autorizar o OAuth2 na interface
3. **Dados embutidos** no código M — autossuficiente, mas pesado

### Ambiente

- Git integration **não existe** em "My workspace", tenha a capacidade que tiver
- Workspace precisa de capacidade Fabric (Trial serve); Pro sozinho não basta
- O tenant do CEUB tem **GitHub desabilitado** no Git integration (só Azure DevOps) —
  irrelevante se publicar por API
- Export PNG está bloqueado no tenant; **PDF funciona**

---

## 4. Entregáveis padrão

```
<NN>-<Exercicio>/
├── Enunciado.pdf
├── ENTREGA/                    ← o que enviar ao professor
│   ├── <Projeto>.pbix
│   └── <dados>.csv
└── projeto-powerbi/            ← repo git
    ├── <Projeto>.SemanticModel/    modelo em TMDL
    ├── <Projeto>.Report/           páginas e visuais em PBIR
    ├── README.md                   como publicar e republicar
    └── MAPA-DAS-PERGUNTAS.md       pergunta → visual → justificativa
```

Para baixar o `.pbix` pronto do Service (funciona mesmo quando o botão da interface está cinza):

```
GET /v1.0/myorg/groups/{ws}/reports/{id}/Export
```

---

## 5. Quando o Power BI não é a melhor escolha

Se o enunciado não exigir Power BI, um **HTML único com os dados embutidos** costuma ser
melhor: abre com duplo clique, não depende de licença, de nuvem nem de refresh, e roda em
qualquer máquina. Foi a abordagem do exercício hospitalar, em `01-Hospitalar/`.

Diga qual dos dois você quer — ou me deixe recomendar depois de ler o enunciado.
