# Dashboard Executivo — Companhia Aérea

Projeto Power BI (formato **PBIP/PBIR**) pronto para sincronizar no **Microsoft Fabric** via Git.
Contém o modelo semântico completo (44 medidas DAX) e o relatório com 5 páginas já montadas.

```
CompanhiaAerea.pbip                  ← abre no Power BI Desktop (se você tiver acesso a um)
CompanhiaAerea.SemanticModel/        ← modelo: tabelas, relações, 44 medidas DAX
CompanhiaAerea.Report/               ← relatório: 5 páginas, 90 objetos
```

---

## Passo a passo (Fabric online)

### 1. Publicar o CSV no OneDrive
Suba `companhia_aerea_voos.csv` no seu **OneDrive corporativo do CEUB**.
Sugestão: crie a pasta `Documentos/PowerBI/` e coloque o arquivo lá.

Copie a **URL raiz** do seu OneDrive — não o link do arquivo. Ela tem este formato:

```
https://SEUTENANT-my.sharepoint.com/personal/usuario_dominio_com/
```

> Para descobrir: abra o OneDrive no navegador e olhe a barra de endereços.
> Pegue tudo até o `/` que vem logo depois de `personal/seu_usuario`.

### 2. Criar o repositório no GitHub
Crie um repositório (pode ser privado) e envie **a pasta `PowerBI/` inteira** para a raiz dele.
Pelo terminal, a partir da pasta do exercício:

```bash
cd PowerBI
git init
git add .
git commit -m "Dashboard executivo da companhia aérea"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/SEU_REPO.git
git push -u origin main
```

### 3. Conectar o workspace do Fabric ao Git
No workspace: **Configurações do workspace → Integração com o Git**

| Campo | Valor |
|---|---|
| Provedor | GitHub |
| Repositório | o que você criou |
| Branch | `main` |
| Pasta | deixe vazio (ou o caminho, se não colocou na raiz) |

Clique em **Conectar** e depois em **Atualizar tudo**.
O Fabric vai criar dois itens: o semantic model `CompanhiaAerea` e o relatório `CompanhiaAerea`.

### 4. Apontar o modelo para o seu OneDrive
No workspace, no **semantic model** → `...` → **Configurações** → **Parâmetros**:

| Parâmetro | O que preencher |
|---|---|
| `pUrlOneDrive` | a URL raiz que você copiou no passo 1 |
| `pNomeArquivo` | `companhia_aerea_voos.csv` |

Ainda nas configurações, em **Credenciais da fonte de dados** → **Editar credenciais**:
escolha **OAuth2 / Conta organizacional** e entre com sua conta do CEUB.
Não é necessário gateway.

### 5. Atualizar
No semantic model → **Atualizar agora**. Leva cerca de 1 minuto.
Abra o relatório: as 5 páginas já estarão preenchidas.

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
