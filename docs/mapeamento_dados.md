# Mapeamento e Diagnóstico Inicial dos Dados

> Documento de trabalho referente à inspeção inicial das bases recebidas para o desafio de BI.  
> Nesta etapa, o objetivo é registrar a estrutura dos dados, problemas observados, hipóteses e pontos que ainda precisam ser validados antes da aplicação de tratamentos.

## 1. Objetivo

Mapear a estrutura, a granularidade, a qualidade e o relacionamento das bases recebidas, identificando problemas e pontos que precisam ser investigados antes da consolidação dos dados.

O diagnóstico servirá como base para a etapa de tratamento em Python, definição dos indicadores, construção da metodologia de classificação dos associados e posterior desenvolvimento do dashboard no Power BI.

---

## 2. Inventário das bases

| Base | Registros | Colunas | Granularidade observada | Chave candidata |
|---|---:|---:|---|---|
| Associados | 1.000 | 6 | Um registro por associado | `CHAVE` |
| Produtos | 1.000 | 7 | Um registro com o portfólio de produtos de cada associado | `CHAVE` |
| Movimentação | 1.000 | 4 | Um registro com indicadores resumidos de movimentação de cada associado | `CHAVE` |

> **Observação:** os quantitativos acima consideram apenas os registros de dados, sem a linha de cabeçalho do Excel.

---

## 3. Diagnóstico por base

### 3.1 Associados

#### Granularidade

Aparentemente, cada linha representa um associado e seus respectivos dados cadastrais e de relacionamento.

#### Campos disponíveis

- `CHAVE`: identificador do associado.
- `NOME`: nome do associado.
- `AGENCIA`: agência relacionada ao associado.
- `CIDADE`: cidade relacionada ao associado.
- `DATA_ASSOCIACAO`: data de início da associação.
- `RENDA_MENSAL`: renda mensal informada para o associado.

#### Qualidade identificada

- A coluna `CHAVE` não apresentou duplicidades na inspeção inicial.
- Foram observados valores ausentes em `RENDA_MENSAL`.
- Foram observadas diferenças de padronização no campo `CIDADE`.
- A apresentação/formatação de alguns campos precisa ser revisada.
- Existem registros de `DATA_ASSOCIACAO` que precisam ser validados quanto à consistência temporal.

#### Potencial analítico

Considerando apenas esta base, ela parece permitir análises relacionadas a:

- quantidade de associados;
- distribuição dos associados por agência;
- distribuição dos associados por cidade;
- perfil de renda;
- faixas de renda;
- tempo de relacionamento;
- evolução dos cadastros/associações ao longo do tempo.

#### Dúvidas e hipóteses

- Como tratar os associados sem renda mensal informada?
- As diferentes grafias encontradas em `CIDADE` representam as mesmas localidades?
- Existem datas de associação inconsistentes ou futuras?
- A ausência de renda representa dado não informado, valor desconhecido ou alguma outra situação?

---

### 3.2 Produtos

#### Granularidade

Aparentemente, cada linha representa o portfólio de produtos de um associado.

#### Campos disponíveis

- `CHAVE`: identificador do associado.
- Demais colunas: indicadores dos produtos disponibilizados na base, informando se o associado possui ou não cada produto.

#### Qualidade identificada

- A coluna `CHAVE` não apresentou duplicidades na inspeção inicial.
- Não foram percebidos valores nulos na inspeção manual.
- Os campos de produtos parecem utilizar categorias binárias, que ainda deverão ser verificadas programaticamente.
- Foram observados associados para os quais todos os produtos disponíveis na base aparecem como não ativos.

#### Potencial analítico

Considerando apenas esta base, ela parece permitir análises relacionadas a:

- quantidade de produtos por associado;
- produtos mais frequentes;
- produtos menos frequentes;
- combinações de produtos;
- diversificação do portfólio;
- associados sem produtos ativos entre os produtos representados na base.

#### Dúvidas e hipóteses

- Os valores dos campos de produto seguem exclusivamente um padrão binário?
- Os associados com todos os produtos marcados como não ativos representam uma situação válida de negócio?
- Os produtos representados nesta tabela correspondem a todo o portfólio disponível ou apenas a um subconjunto?
- Existem padrões de associação entre determinados produtos?

---

### 3.3 Movimentação

#### Granularidade

Aparentemente, cada linha representa um resumo de indicadores de movimentação financeira de um associado.

Não foram identificadas múltiplas linhas por `CHAVE` na inspeção inicial, portanto a tabela não aparenta possuir granularidade transacional.

#### Campos disponíveis

- `CHAVE`: identificador do associado.
- `SALDO_MEDIO`: indicador de saldo médio.
- `PIX_MENSAL`: indicador relacionado à utilização mensal de PIX.
- `COMPRAS_CARTAO`: indicador relacionado às compras realizadas com cartão.

#### Qualidade identificada

- A coluna `CHAVE` não apresentou duplicidades na inspeção inicial.
- Não foram percebidos valores nulos durante a inspeção manual.
- Não existe, aparentemente, uma coluna de competência ou período de referência da movimentação.
- Os tipos, intervalos e possíveis valores extremos dos indicadores ainda precisam ser verificados programaticamente.

#### Potencial analítico

Considerando apenas esta base, ela parece permitir análises relacionadas a:

- distribuição do saldo médio;
- utilização de PIX;
- utilização do cartão;
- intensidade de utilização dos serviços financeiros;
- padrões de relacionamento entre saldo, PIX e compras no cartão.

#### Dúvidas e hipóteses

- Qual é o período de referência dos indicadores de movimentação?
- `PIX_MENSAL` representa quantidade de transações, valor financeiro ou outro indicador?
- `COMPRAS_CARTAO` representa quantidade ou valor financeiro?
- Existem valores extremos que possam distorcer médias ou critérios de classificação?

---

## 4. Relacionamento entre as bases

### 4.1 Chave de relacionamento

A coluna `CHAVE` está presente nas três bases e aparenta representar o mesmo associado.

### 4.2 Cardinalidade observada

Na inspeção inicial, cada base apresentou apenas um registro por `CHAVE`.

Isso sugere relacionamentos de cardinalidade `1:1` entre as tabelas, mas essa conclusão deverá ser confirmada programaticamente.

### 4.3 Cobertura das chaves

Ainda deverá ser validado em Python se todas as chaves presentes em uma base também existem nas demais.

Validações previstas:

- Associados × Produtos;
- Associados × Movimentação;
- Produtos × Movimentação.

### 4.4 Estrutura esperada após consolidação

A consolidação deverá preservar a granularidade de um registro por associado, reunindo em uma única visão os dados cadastrais, produtos e indicadores de movimentação correspondentes à mesma `CHAVE`.

A quantidade final de registros deverá ser reconciliada com a população original das bases.

---

## 5. Problemas de qualidade identificados

### 5.1 Valores ausentes

| Base | Campo | Observação |
|---|---|---|
| Associados | `RENDA_MENSAL` | Existem registros sem renda informada. |

### 5.2 Padronização

| Base | Campo | Observação |
|---|---|---|
| Associados | `CIDADE` | Foram observadas grafias/formatações sem padrão consistente. |

### 5.3 Integridade

- Não foram identificadas duplicidades de `CHAVE` durante a inspeção manual.
- A correspondência completa das chaves entre as três bases ainda precisa ser validada programaticamente.
- A existência de duplicidades completas de linha também deverá ser testada em Python.

### 5.4 Consistência lógica

- `DATA_ASSOCIACAO` deverá ser validada para identificar datas impossíveis ou posteriores à data de referência da análise.
- Associados sem nenhum produto ativo entre os produtos disponíveis na base deverão ser investigados antes de serem tratados como erro.

### 5.5 Formatação e tipos

- Campos monetários deverão ser mantidos como valores numéricos durante o tratamento; a formatação em moeda deverá ser aplicada apenas na camada de apresentação quando necessário.
- Datas deverão ser verificadas quanto ao tipo de dado.
- Campos categóricos deverão ser avaliados quanto à consistência de grafia, espaços, caixa e demais variações.

---

## 6. Hipóteses e pontos a validar

| ID | Hipótese / dúvida | Como validar | Status |
|---|---|---|---|
| H01 | A `CHAVE` é única nas três bases. | Verificar duplicidades programaticamente. | Pendente |
| H02 | As três bases possuem exatamente o mesmo conjunto de chaves. | Comparar os conjuntos de `CHAVE` entre as tabelas. | Pendente |
| H03 | As diferentes grafias de `CIDADE` representam localidades que podem ser padronizadas. | Listar valores únicos e frequências. | Pendente |
| H04 | Existem registros de associação com datas temporalmente inconsistentes. | Comparar `DATA_ASSOCIACAO` com a data de referência. | Pendente |
| H05 | Os produtos utilizam apenas categorias binárias válidas. | Listar valores únicos de cada campo de produto. | Pendente |
| H06 | Associados sem produtos ativos representam uma situação válida. | Quantificar os casos e avaliar o contexto dos demais campos. | Pendente |
| H07 | Os indicadores de movimentação não possuem valores extremos relevantes. | Analisar estatísticas descritivas e distribuição. | Pendente |
| H08 | Os valores ausentes de renda não apresentam um padrão evidente. | Comparar os registros ausentes com agência, cidade, produtos e movimentação. | Pendente |
| H09 | A consolidação poderá preservar exatamente um registro por associado. | Realizar merges controlados e reconciliar a quantidade de registros. | Pendente |

---

## 7. Perguntas analíticas

### 7.1 Perguntas respondidas por uma única base

#### Associados

- Como os associados estão distribuídos entre as agências?
- Como os associados estão distribuídos geograficamente?
- Qual é o perfil de renda dos associados?
- Como se distribui o tempo de relacionamento?
- Como as associações se distribuem ao longo do tempo?

#### Produtos

- Quais produtos são mais e menos presentes na carteira?
- Quantos produtos cada associado possui?
- Quais combinações de produtos aparecem com maior frequência?
- Quantos associados não possuem produtos ativos entre os produtos representados?

#### Movimentação

- Como se distribui o saldo médio?
- Como se distribui a utilização de PIX?
- Como se distribui a utilização do cartão?
- Existem associados com utilização significativamente maior ou menor que o restante da população?

### 7.2 Perguntas que dependem da consolidação

As perguntas abaixo deverão ser refinadas após a validação e consolidação das bases:

- Existe relação entre renda e quantidade de produtos?
- Existem associados com alta renda e poucos produtos?
- O tempo de relacionamento está associado à quantidade ou diversificação de produtos?
- Associados com maior utilização financeira também possuem maior quantidade de produtos?
- Existem associados com relacionamento longo, mas baixa utilização dos serviços?
- Quais perfis apresentam maior potencial de crescimento?
- Existem diferenças relevantes de perfil entre agências ou cidades?
- Quais características distinguem associados com maior nível de relacionamento?

> Estas perguntas representam hipóteses analíticas iniciais. A existência de uma relação estatística não deverá ser interpretada automaticamente como causalidade.

---

## 8. Decisões de tratamento

Nenhuma regra definitiva de tratamento foi aplicada nesta etapa.

Os tratamentos serão definidos após a validação programática dos achados e deverão ser documentados nesta seção.

| ID | Decisão | Justificativa | Impacto |
|---|---|---|---|
| D01 | A definir | Aguardando diagnóstico programático. | A definir |

---

## 9. Próximos passos

1. Criar a estrutura inicial do projeto e iniciar o versionamento com Git.
2. Desenvolver um diagnóstico reproduzível das bases utilizando Python.
3. Validar programaticamente granularidade, tipos, nulos, duplicidades, chaves, categorias, valores numéricos e datas.
4. Atualizar este documento com os resultados confirmados pelo diagnóstico.
5. Definir e documentar as regras de tratamento.
6. Criar a base consolidada mantendo a granularidade de um registro por associado.
7. Validar a base tratada antes da construção dos indicadores e da classificação.

---

## 10. Observações de trabalho

Este documento deverá ser atualizado durante o desenvolvimento do projeto.

A separação utilizada é:

- **Fato:** algo observado ou comprovado nos dados.
- **Hipótese:** algo que parece plausível, mas ainda precisa ser validado.
- **Pergunta:** algo que ainda precisa ser investigado.
- **Decisão:** regra adotada após análise e justificativa.

Essa distinção deverá ser preservada durante as próximas etapas para evitar que hipóteses sejam tratadas como fatos ou que alterações sejam realizadas sem justificativa.
