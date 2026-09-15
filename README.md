# Dashboard Executivo — Companhia Aérea

Projeto Power BI (formato **PBIP/PBIR**) pronto para sincronizar no **Microsoft Fabric** via Git.
Contém o modelo semântico completo (44 medidas DAX) e o relatório com 5 páginas já montadas.

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

## Se algo não sincronizar

| Sintoma | Causa provável | O que fazer |
|---|---|---|
| Itens não aparecem após o sync | Pasta errada na configuração do Git | Confirme que `CompanhiaAerea.Report/` está na raiz do repo (ou ajuste o campo Pasta) |
| Erro "arquivo não encontrado" no refresh | `pUrlOneDrive` incorreto | Deve terminar com `/` e ser a raiz, não o link do arquivo |
| Falha de credencial | Fonte não autenticada | Configurações do semantic model → Editar credenciais → OAuth2 |
| Tema não aplicou | Custom theme não carregou | Exibir → Temas → Procurar temas → `StaticResources/RegisteredResources/tema-executivo.json` |

As cores de cada gráfico estão definidas visual a visual, então o dashboard fica correto mesmo se o tema não carregar.
