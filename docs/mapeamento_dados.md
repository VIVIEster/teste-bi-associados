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
- Foram identificados 37 registros cuja `DATA_ASSOCIACAO` é posterior à data de referência do projeto, 31/08/2026.
- As datas futuras identificadas estão compreendidas entre 17/09/2026 e 26/12/2026.

#### Potencial analítico

Considerando apenas esta base, ela parece permitir análises relacionadas a:

- quantidade de associados;
- distribuição por agência;
- distribuição por cidade;
- perfil e faixas de renda;
- tempo de relacionamento;
- evolução das associações ao longo do tempo.


---

### 3.2 Produtos

#### Granularidade

Cada linha representa o portfólio dos seis produtos disponíveis na base para um associado.

#### Campos disponíveis

- `CHAVE`: identificador do associado.
- `CONTA_CORRENTE`: indica se o associado possui conta corrente.
- `CARTAO`: indica se o associado possui cartão.
- `CREDITO`: indica se o associado possui produto de crédito.
- `INVESTIMENTO`: indica se o associado possui investimento.
- `CONSORCIO`: indica se o associado possui consórcio.
- `SEGURO`: indica se o associado possui seguro.

#### Qualidade identificada

- `CHAVE` é única nos 1.000 registros.
- Não foram identificadas linhas completamente duplicadas.
- Não foram encontrados valores nulos.
- As seis colunas de produtos apresentam exclusivamente `S` e `N` na fonte.
- Foram encontrados 13 associados com todos os seis produtos marcados como `N`.

#### Potencial analítico

Considerando apenas esta base, ela parece permitir análises relacionadas a:

- quantidade de produtos por associado;
- produtos mais frequentes;
- produtos menos frequentes;
- combinações de produtos;
- diversificação do portfólio;
- associados sem produtos ativos entre os produtos representados na base.

#### Interpretação

Os 13 associados sem produtos ativos foram mantidos como registros válidos, pois não existe evidência de erro e suas demais informações cadastrais e de movimentação permanecem disponíveis.

Na camada final de saída, os valores `S/N` foram padronizados para `Sim/Não`.

---

### 3.3 Movimentação

#### Granularidade

Cada linha representa um resumo de indicadores de movimentação financeira de um associado.

A tabela possui uma única linha por `CHAVE` e não apresenta granularidade transacional.

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

#### Limitação de interpretação

O nome `PIX_MENSAL` sugere uma medida mensal, mas a base não informa sua competência. Da mesma forma, não foi fornecido dicionário adicional especificando formalmente as unidades de `PIX_MENSAL` e `COMPRAS_CARTAO`.

Esses campos foram, portanto, utilizados respeitando a estrutura e os nomes fornecidos, sem criação de premissas adicionais sobre sua origem.

#### Potencial analítico

Considerando apenas esta base, ela parece permitir análises relacionadas a:

- distribuição do saldo médio;
- utilização de PIX;
- utilização do cartão;
- intensidade de utilização dos serviços financeiros;
- padrões de relacionamento entre saldo, PIX e compras no cartão.

---

## 4. Relacionamento entre as bases

### 4.1 Chave de relacionamento

A coluna `CHAVE` está presente nas três bases e representa o identificador comum do associado.

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

### 4.4 Consolidação

A base consolidada preserva:

**1 linha = 1 associado**

Foram mantidos exatamente **1.000 registros**, sem multiplicação ou perda de associados durante os merges.

O pipeline utiliza validação `one_to_one` para impedir consolidações incompatíveis com a cardinalidade identificada.


---

## 5. Problemas de qualidade identificados

### 5.1 Valores ausentes

| Base | Campo | Quantidade | Observação |
|---|---|---:|---|
| Associados | `RENDA_MENSAL` | 12 | Preservados como nulos; faixa derivada recebe `Não informado` |
| Produtos | — | 0 | Nenhum tratamento necessário |
| Movimentação | — | 0 | Nenhum tratamento necessário |

### 5.2 Padronização

| Campo | Problema | Tratamento |
|---|---|---|
| `CIDADE` | abreviações, caixa e ausência de acentos | nomenclatura canônica |
| `AGENCIA` | lida como número, apesar de ser código | conversão para texto e dois dígitos |
| Produtos | `S/N` | saída padronizada para `Sim/Não` |

### 5.3 Consistência temporal

Foram identificados 37 registros com `DATA_ASSOCIACAO` posterior à data de referência de **31/08/2026**.

Esses registros:

- permanecem na base;
- mantêm a data original;
- recebem `FLAG_DATA_FUTURA = Sim`;
- não recebem tempo de relacionamento válido;
- não recebem `SCORE_TEMPO`.

### 5.4 Integridade

- linhas completamente duplicadas: 0;
- chaves duplicadas: 0;
- registros órfãos: 0;
- cobertura de chaves: integral;
- cardinalidade: `1:1`;
- registros após consolidação: 1.000.

### 5.5 Consistência lógica

- Foram identificados 37 registros com `DATA_ASSOCIACAO` posterior à data de referência de 31/08/2026.
- Essas datas variam entre 17/09/2026 e 26/12/2026.
- Esses registros precisam de uma regra de tratamento antes do cálculo de tempo de relacionamento.
- Foram identificados 13 associados sem nenhum dos seis produtos ativos. Esse comportamento será mantido como válido até que exista evidência para classificá-lo como inconsistência.

### 6 Estatísticas exploratórias iniciais

#### Renda Mensal

- Registros válidos: 988.
- Média: R$ 15.790,71.
- Mediana: R$ 15.235,00.
- Mínimo: R$ 2.010,00.
- Q1: R$ 8.984,75.
- Q3: R$ 22.911,75.
- Máximo: R$ 29.972,00.

#### Saldo Médio

- Registros válidos: 1.000.
- Média: R$ 123.365,02.
- Mediana: R$ 122.643,50.
- Mínimo: R$ 744,00.
- Q1: R$ 61.923,25.
- Q3: R$ 183.294,75.
- Máximo: R$ 249.864,00.

#### PIX Mensal

- Registros válidos: 1.000.
- Média: 50,275.
- Mediana: 48.
- Mínimo: 0.
- Q1: 25.
- Q3: 76.
- Máximo: 100.

#### Compras no Cartão

- Registros válidos: 1.000.
- Média: R$ 10.040,05.
- Mediana: R$ 9.826,50.
- Mínimo: R$ 50,00.
- Q1: R$ 4.990,50.
- Q3: R$ 15.029,25.
- Máximo: R$ 19.994,00.

As estatísticas serviram como apoio à análise exploratória e à definição das regras baseadas em quartis. Valores extremos não foram removidos apenas por sua posição estatística, pois não foi encontrada evidência de que representassem erros de origem.

---

## 7. Hipóteses e validações

| ID | Hipótese / dúvida | Resultado | Status |
|---|---|---|---|
| H01 | `CHAVE` é única nas três bases | Confirmado programaticamente | Confirmado |
| H02 | As três bases possuem o mesmo conjunto de chaves | Cobertura integral | Confirmado |
| H03 | Grafias diferentes de cidade representam categorias equivalentes | Padronização definida e aplicada | Confirmado / Tratado |
| H04 | Existem datas de associação futuras | 37 registros | Confirmado / Tratado |
| H05 | Produtos utilizam apenas categorias binárias válidas | Apenas `S` e `N` na fonte | Confirmado |
| H06 | Existem associados sem produtos ativos | 13 registros, mantidos como válidos | Confirmado |
| H07 | Valores extremos exigem remoção | Não houve evidência de erro que justificasse exclusão | Não aplicado |
| H08 | Rendas ausentes exigem imputação | Não houve evidência para atribuir valores artificiais | Não aplicado |
| H09 | A consolidação preserva um registro por associado | 1.000 entradas e 1.000 saídas | Confirmado |

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

---

## 8. Decisões de tratamento

| ID | Decisão | Justificativa | Impacto |
|---|---|---|---|
| D01 | Padronizar `CIDADE` por nomenclatura canônica. | Evita que uma mesma localidade seja contabilizada como categorias diferentes. | Melhora agrupamentos e filtros sem alterar a população. |
| D02 | Tratar `AGENCIA` como código textual de dois dígitos. | O campo é identificador nominal e não medida numérica. | Evita agregações matemáticas indevidas e preserva o formato de código. |
| D03 | Preservar os 12 nulos de `RENDA_MENSAL`. | Não há evidência suficiente para imputar renda artificialmente. | Mantém os associados e evita distorção nas métricas de renda. |
| D04 | Preservar datas futuras e sinalizar a inconsistência. | Excluir ou substituir datas alteraria informação original sem evidência. | Mantém rastreabilidade e impede tempo de relacionamento negativo. |
| D05 | Utilizar 31/08/2026 como data fixa de referência. | Garante reprodutibilidade do cálculo de relacionamento. | O mesmo código e a mesma base produzem o mesmo resultado em execuções futuras. |
| D06 | Padronizar produtos e flags para `Sim/Não` na saída. | Facilita leitura e filtros no Power BI. | Melhora a camada de consumo sem alterar a regra lógica. |
| D07 | Arredondar indicadores de apresentação somente após os cálculos. | A classificação precisa utilizar a precisão completa. | Mantém a precisão da regra e melhora a legibilidade da base entregue. |

---

## 9. Indicadores derivados

Foram criados:

- `QTD_PRODUTOS`
- `FAIXA_RENDA`
- `FLAG_DATA_FUTURA`
- `TEMPO_RELACIONAMENTO_ANOS`
- `SCORE_PRODUTOS`
- `SCORE_TEMPO`
- `SCORE_SALDO`
- `SCORE_PIX`
- `SCORE_CARTAO`
- `SCORE_UTILIZACAO`
- `SCORE_RELACIONAMENTO`
- `QTD_DIMENSOES_SCORE`
- `CLASSIFICACAO`
- `SEGMENTO_RELACIONAMENTO`
- `OPORT_CROSS_SELL`
- `OPORT_BAIXA_UTILIZACAO`
- `OPORT_RELACIONAMENTO_SUBAPROVEITADO`

As regras completas dos scores e oportunidades estão documentadas em [`metodologia_analitica.md`](metodologia_analitica.md).

---

## 10. Resultado final do tratamento

### Estrutura

- registros recebidos em Associados: 1.000;
- registros recebidos em Produtos: 1.000;
- registros recebidos em Movimentação: 1.000;
- registros consolidados: **1.000**;
- granularidade final: **1 linha por associado**.

### Qualidade

- duplicidades de linha: 0;
- chaves duplicadas: 0;
- registros órfãos: 0;
- rendas ausentes preservadas: 12;
- datas futuras sinalizadas: 37;
- associados sem produtos ativos preservados: 13.

### Padronizações

As categorias originais de cidade:

- `P. Branco`
- `Pato Branco`
- `PATO BRANCO`

foram consolidadas em:

- `Pato Branco`

Também foram corrigidos:

- `Chapeco` → `Chapecó`
- `Maringa` → `Maringá`

Após a padronização, a base possui cinco localidades:

- Cascavel;
- Chapecó;
- Maringá;
- Pato Branco;
- Toledo.

### Saída

A versão final é exportada para:

```text
data/processed/base_consolidada.xlsx
```

A base é preparada para consumo no Power BI com:

- datas sem componente de horário na apresentação;
- valores monetários preservados como numéricos;
- categorias de produtos e flags em `Sim/Não`;
- score e tempo de relacionamento com precisão de apresentação controlada;
- colunas organizadas por contexto analítico.

---

## 11. Perguntas analíticas para o dashboard

A base consolidada permite explorar, entre outras, as seguintes perguntas:

- Como a carteira está distribuída por agência e cidade?
- Qual é o perfil de renda dos associados?
- Qual é o tempo médio de relacionamento?
- Quantos produtos os associados possuem em média?
- Qual é a distribuição dos níveis de relacionamento?
- Quais associados possuem alta renda e poucos produtos?
- Onde existe baixa utilização dos serviços financeiros?
- Quais associados possuem relacionamento longo, mas baixa diversificação de produtos?
- Como os perfis e oportunidades variam por agência, cidade e faixa de renda?

---

## 12. Observações e limitações

- A base de movimentação não contém competência explícita.
- Não foi fornecido dicionário adicional com as unidades formais de `PIX_MENSAL` e `COMPRAS_CARTAO`.
- Os dados são fictícios e destinados ao desafio técnico.
- O score utiliza quartis da população analisada e não deve ser generalizado automaticamente para outra base.
- As relações identificadas são descritivas e não representam causalidade.
