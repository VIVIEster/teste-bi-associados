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

Cada linha representa um associado e seus respectivos dados cadastrais e de relacionamento.

#### Campos disponíveis

- `CHAVE`: identificador do associado.
- `NOME`: nome do associado.
- `AGENCIA`: agência relacionada ao associado.
- `CIDADE`: cidade relacionada ao associado.
- `DATA_ASSOCIACAO`: data de início da associação.
- `RENDA_MENSAL`: renda mensal informada para o associado.

#### Qualidade identificada

- A coluna `CHAVE` é única nos 1.000 registros.
- Não foram identificadas linhas completamente duplicadas.
- Foram identificados 12 valores nulos em `RENDA_MENSAL`, restando 988 rendas válidas.
- Foram identificadas inconsistências de padronização no campo `CIDADE`.
- O campo `AGENCIA` foi interpretado pelo pandas como `int64`, embora represente uma categoria/código de identificação e não uma medida numérica.
- `DATA_ASSOCIACAO` foi corretamente interpretada como data.
- Foram identificados 37 registros cuja `DATA_ASSOCIACAO` é posterior à data de referência do diagnóstico, 01/09/2026.
- As datas futuras identificadas estão compreendidas entre 17/09/2026 e 26/12/2026.

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

- Investigar se os 12 registros sem `RENDA_MENSAL` apresentam algum padrão relacionado a agência, cidade, tempo de relacionamento ou demais características.
- Definir posteriormente a regra mais adequada para os valores ausentes de renda, evitando imputação sem justificativa.
- Padronizar as diferentes representações de uma mesma cidade somente após definir uma nomenclatura canônica.
- Avaliar o tratamento adequado para as 37 datas de associação futuras, pois elas resultariam em tempo de relacionamento negativo.
- Avaliar a conversão de `AGENCIA` para um tipo categórico/textual durante o tratamento, preservando seu significado de código identificador.

---

### 3.2 Produtos

#### Granularidade

Cada linha representa o portfólio de produtos de um associado.

#### Campos disponíveis

- `CHAVE`: identificador do associado.
- `CONTA_CORRENTE`: indica se o associado possui conta corrente.
- `CARTAO`: indica se o associado possui cartão.
- `CREDITO`: indica se o associado possui produto de crédito.
- `INVESTIMENTO`: indica se o associado possui investimento.
- `CONSORCIO`: indica se o associado possui consórcio.
- `SEGURO`: indica se o associado possui seguro.

#### Qualidade identificada

- A coluna `CHAVE` é única nos 1.000 registros.
- Não foram identificadas linhas completamente duplicadas.
- Não foram identificados valores nulos.
- Todas as seis colunas de produtos apresentam exclusivamente as categorias `S` e `N`.
- Não foram identificadas inconsistências de padronização nas categorias dos produtos.
- Foram identificados 13 associados com todos os seis produtos marcados como `N`.

#### Potencial analítico

Considerando apenas esta base, ela parece permitir análises relacionadas a:

- quantidade de produtos por associado;
- produtos mais frequentes;
- produtos menos frequentes;
- combinações de produtos;
- diversificação do portfólio;
- associados sem produtos ativos entre os produtos representados na base.

#### Dúvidas e hipóteses

- Os 13 associados sem nenhum dos seis produtos ativos serão inicialmente considerados registros válidos, mas seu perfil deverá ser analisado após a consolidação das bases.
- Esses associados podem representar um grupo relevante para a análise de oportunidades, caso os demais indicadores sustentem essa interpretação.
- Não é possível afirmar, apenas com esta base, que os seis produtos representam todo o portfólio disponível pela instituição.

---

### 3.3 Movimentação

#### Granularidade

Cada linha representa um resumo de indicadores de movimentação financeira de um associado.

Não foram identificadas múltiplas linhas por `CHAVE` na inspeção inicial, portanto a tabela não aparenta possuir granularidade transacional.

#### Campos disponíveis

- `CHAVE`: identificador do associado.
- `SALDO_MEDIO`: indicador de saldo médio.
- `PIX_MENSAL`: indicador relacionado à utilização mensal de PIX.
- `COMPRAS_CARTAO`: indicador relacionado às compras realizadas com cartão.

#### Qualidade identificada

- A coluna `CHAVE` é única nos 1.000 registros.
- Não foram identificadas linhas completamente duplicadas.
- Não foram identificados valores nulos.
- `SALDO_MEDIO`, `PIX_MENSAL` e `COMPRAS_CARTAO` foram interpretados como campos numéricos inteiros.
- Não existe coluna explícita de competência ou período de referência da movimentação.
- A análise inicial das distribuições numéricas não apresentou, apenas pelos valores mínimo e máximo, evidência suficiente para classificar registros como inválidos. A investigação de possíveis valores extremos será complementada por análise estatística.

#### Potencial analítico

Considerando apenas esta base, ela parece permitir análises relacionadas a:

- distribuição do saldo médio;
- utilização de PIX;
- utilização do cartão;
- intensidade de utilização dos serviços financeiros;
- padrões de relacionamento entre saldo, PIX e compras no cartão.

#### Dúvidas e hipóteses

- O período de referência dos indicadores de movimentação não está explicitamente informado na base.
- O nome `PIX_MENSAL` sugere uma medida mensal, mas a base não informa a competência correspondente.
- A unidade de `PIX_MENSAL` deve ser interpretada com cautela, pois o campo pode representar quantidade de transações e não valor financeiro.
- A unidade de `COMPRAS_CARTAO` também deverá ser considerada na interpretação analítica.
- As distribuições de `SALDO_MEDIO`, `PIX_MENSAL` e `COMPRAS_CARTAO` deverão ser consideradas antes da definição de critérios de baixa, média ou alta movimentação.

---

## 4. Relacionamento entre as bases

### 4.1 Chave de relacionamento

A coluna `CHAVE` está presente nas três bases e aparenta representar o mesmo associado.

### 4.2 Cardinalidade observada

As três bases apresentam `CHAVE` única, sem duplicidades.

Foi confirmada programaticamente uma correspondência de um registro por associado em cada uma das três tabelas. Portanto, para a base recebida, os relacionamentos observados são de cardinalidade `1:1`.

### 4.3 Cobertura das chaves

A comparação programática dos conjuntos de `CHAVE` confirmou cobertura integral entre as três bases.

Resultados:

- Associados × Produtos: conjuntos de chaves idênticos.
- Associados × Movimentação: conjuntos de chaves idênticos.
- Produtos × Movimentação: conjuntos de chaves idênticos.
- Associados sem Produtos: 0.
- Produtos sem Associados: 0.
- Associados sem Movimentação: 0.
- Movimentação sem Associados: 0.

Portanto, não foram identificados registros órfãos entre as bases.

### 4.4 Estrutura esperada após consolidação

Como as três bases possuem 1.000 registros, `CHAVE` única e cobertura integral entre as populações, espera-se que a consolidação mantenha a granularidade de:

**1 linha = 1 associado**

A base consolidada deverá, portanto, possuir 1.000 registros caso o relacionamento seja realizado corretamente.

Essa quantidade será utilizada como controle de reconciliação após os merges.

---

## 5. Problemas de qualidade identificados

### 5.1 Valores ausentes

| Base | Campo | Quantidade | Observação |
|---|---|---:|---|
| Associados | `RENDA_MENSAL` | 12 | Valores de renda não informados. |
| Produtos | — | 0 | Nenhum valor nulo identificado. |
| Movimentação | — | 0 | Nenhum valor nulo identificado. |

### 5.2 Padronização

| Base | Campo | Observação |
|---|---|---|
| Associados | `CIDADE` | Foram identificadas diferentes representações para localidades aparentemente equivalentes, incluindo variações de abreviação e caixa. |

### 5.3 Tipos de dados

- `AGENCIA` foi interpretada como `int64`, embora semanticamente represente um código categórico.
- `DATA_ASSOCIACAO` foi corretamente interpretada como `datetime`.
- `RENDA_MENSAL` foi interpretada como `float64`, o que é compatível com a presença de valores ausentes.
- Os indicadores de movimentação foram interpretados como numéricos inteiros.

### 5.4 Integridade

- Não foram identificadas linhas completamente duplicadas.
- Não foram identificadas `CHAVE`s duplicadas.
- Todas as `CHAVE`s estão presentes nas três bases.
- Não foram identificados registros órfãos.
- A cardinalidade observada entre as três bases é `1:1`.

### 5.5 Consistência lógica

- Foram identificados 37 registros com `DATA_ASSOCIACAO` posterior à data de referência de 01/09/2026.
- Essas datas variam entre 17/09/2026 e 26/12/2026.
- Esses registros precisam de uma regra de tratamento antes do cálculo de tempo de relacionamento.
- Foram identificados 13 associados sem nenhum dos seis produtos ativos. Esse comportamento será mantido como válido até que exista evidência para classificá-lo como inconsistência.

### 5.6 Distribuições numéricas iniciais

#### Renda Mensal

- Registros válidos: 988.
- Média: R$ 15.790,71.
- Mediana: R$ 15.235,00.
- Mínimo: R$ 2.010,00.
- Máximo: R$ 29.972,00.

#### Saldo Médio

- Média: R$ 123.365,02.
- Mediana: R$ 122.643,50.
- Mínimo: R$ 744,00.
- Máximo: R$ 249.864,00.

#### PIX Mensal

- Média: 50,275.
- Mediana: 48.
- Mínimo: 0.
- Máximo: 100.

#### Compras no Cartão

- Média: R$ 10.040,05.
- Mediana: R$ 9.826,50.
- Mínimo: R$ 50,00.
- Máximo: R$ 19.994,00.

As estatísticas acima representam uma análise exploratória inicial e ainda não definem, isoladamente, limites para classificação de baixa, média ou alta movimentação.

---

## 6. Hipóteses e pontos a validar

| ID | Hipótese / dúvida | Como validar | Status |
|---|---|---|---|
| H01 | A `CHAVE` é única nas três bases. | Verificação programática de duplicidades. | Confirmado |
| H02 | As três bases possuem exatamente o mesmo conjunto de chaves. | Comparação dos conjuntos de `CHAVE`. | Confirmado |
| H03 | As diferentes grafias de `CIDADE` representam localidades que podem ser padronizadas. |  Análise dos valores únicos e frequências de `CIDADE`. | Parcialmente confirmado - definir padrão |
| H04 | Existem registros de associação com datas temporalmente inconsistentes. | Comparação de `DATA_ASSOCIACAO` com a data de referência. | Confirmado - 37 registros |
| H05 | Os produtos utilizam apenas categorias binárias válidas. | Análise dos valores únicos das seis colunas de produto. | Confirmado - apenas 'S' e 'N' |
| H06 | Associados sem produtos ativos representam uma situação válida. | Verificação conjunta das seis colunas de produto. | Confirmado - 13 registros |
| H07 | Os indicadores de movimentação não possuem valores extremos relevantes. | Estatísticas descritivas e método IQR. | Em avaliação |
| H08 | Os valores ausentes de renda não apresentam um padrão evidente. | Investigar os 12 registros e comparar características. | Em avaliação |
| H09 | A consolidação poderá preservar exatamente um registro por associado. | Executar merges e reconciliar a quantidade final. | Evidência - validar após o merge |

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

O diagnóstico inicial foi concluído, porém as regras de tratamento ainda não foram aplicadas.

Os principais pontos que exigem decisão são:

- padronização de `CIDADE`;
- tratamento semântico de `AGENCIA`;
- tratamento dos 12 valores ausentes de `RENDA_MENSAL`;
- tratamento das 37 datas futuras de `DATA_ASSOCIACAO`;
- manutenção ou sinalização dos 13 associados sem produtos ativos;
- definição posterior das regras para indicadores derivados e classificação.

As decisões serão registradas somente após a análise de cada situação e sua respectiva justificativa.

| ID | Decisão | Justificativa | Impacto |
|---|---|---|---|
| D01 | A definir | Tratamento de `CIDADE`. | A definir |
| D02 | A definir | Tipo adequado para `AGENCIA`. | A definir |
| D03 | A definir | Tratamento da renda ausente. | A definir |
| D04 | A definir | Tratamento das datas futuras. | A definir |

---

## 9. Próximos passos

1. Concluir a investigação dos registros com renda ausente.
2. Validar possíveis valores extremos nos campos numéricos.
3. Definir e documentar as regras de tratamento dos problemas identificados.
4. Implementar o processo de limpeza e padronização em Python.
5. Consolidar as três bases através da `CHAVE`.
6. Reconciliar a base consolidada com a população original de 1.000 associados.
7. Criar os indicadores derivados exigidos pelo desafio.
8. Desenvolver e documentar a metodologia de classificação dos associados.
9. Preparar a base final para utilização no Power BI.

---

## 10. Observações de trabalho

Este documento deverá ser atualizado durante o desenvolvimento do projeto.

A separação utilizada é:

- **Fato:** algo observado ou comprovado nos dados.
- **Hipótese:** algo que parece plausível, mas ainda precisa ser validado.
- **Pergunta:** algo que ainda precisa ser investigado.
- **Decisão:** regra adotada após análise e justificativa.

Essa distinção deverá ser preservada durante as próximas etapas para evitar que hipóteses sejam tratadas como fatos ou que alterações sejam realizadas sem justificativa.
