# Metodologia Analítica

## 1. Objetivo da metodologia

A metodologia foi desenvolvida para transformar as variáveis disponíveis nas bases do desafio em uma medida interpretável de **nível de relacionamento do associado com a instituição**.

O objetivo não é avaliar risco, rentabilidade ou valor econômico do associado. O score procura representar o relacionamento observado a partir de três dimensões:

- diversidade de produtos;
- tempo de relacionamento;
- utilização financeira.

A abordagem escolhida foi um **scorecard híbrido baseado em critérios de negócio e quartis da população**.

## 2. Princípios adotados

Foram adotados os seguintes princípios:

1. **Interpretabilidade:** cada componente do score deve possuir uma regra simples e auditável.
2. **Reprodutibilidade:** o mesmo código e a mesma base devem gerar o mesmo resultado.
3. **Comparabilidade:** as diferentes variáveis precisam ser convertidas para escalas equivalentes antes da combinação.
4. **Não imputação sem evidência:** valores ausentes ou inconsistentes não recebem valores artificiais apenas para completar o cálculo.
5. **Separação entre relacionamento e potencial econômico:** renda é utilizada principalmente na análise de oportunidades, e não como componente do score de relacionamento.
6. **Uso dos dados observados:** variáveis contínuas são avaliadas de acordo com a distribuição da própria população.

## 3. Dimensões do score

### 3.1 Diversificação de produtos

A quantidade de produtos ativos por associado é calculada a partir dos seis produtos disponíveis:

- conta corrente;
- cartão;
- crédito;
- investimento;
- consórcio;
- seguro.

A variável `QTD_PRODUTOS` pode variar de 0 a 6.

Como se trata de uma variável discreta com interpretação direta de negócio, foram utilizadas faixas fixas:

| Quantidade de produtos | Score |
|---:|---:|
| 0–1 | 0 |
| 2 | 1 |
| 3–4 | 2 |
| 5–6 | 3 |

A pontuação mais alta indica maior diversificação do relacionamento por produtos.

### 3.2 Tempo de relacionamento

O tempo de relacionamento é calculado a partir de:

```text
DATA_REFERENCIA - DATA_ASSOCIACAO
```

A data de referência utilizada no projeto é **31/08/2026**.

Para os registros válidos, a distribuição observada apresentou aproximadamente:

| Estatística | Anos |
|---|---:|
| Q1 | 2,15 |
| Mediana / Q2 | 4,24 |
| Q3 | 6,61 |

O score é definido pela posição do associado na distribuição:

| Faixa | Score |
|---|---:|
| Até Q1 | 0 |
| Acima de Q1 até Q2 | 1 |
| Acima de Q2 até Q3 | 2 |
| Acima de Q3 | 3 |

Os 37 registros com `DATA_ASSOCIACAO` posterior à data de referência permanecem sinalizados e não recebem `SCORE_TEMPO`.

### 3.3 Utilização financeira

A utilização financeira considera:

- `SALDO_MEDIO`
- `PIX_MENSAL`
- `COMPRAS_CARTAO`

Essas variáveis não são somadas diretamente, pois possuem escalas diferentes.

Cada uma é transformada individualmente em um score de 0 a 3 a partir dos quartis da população:

| Posição na distribuição | Score |
|---|---:|
| Até Q1 | 0 |
| Acima de Q1 até Q2 | 1 |
| Acima de Q2 até Q3 | 2 |
| Acima de Q3 | 3 |

São gerados:

- `SCORE_SALDO`
- `SCORE_PIX`
- `SCORE_CARTAO`

## 4. Score de utilização

O score de utilização é calculado pela média simples dos três componentes:

```text
SCORE_UTILIZACAO =
média(
    SCORE_SALDO,
    SCORE_PIX,
    SCORE_CARTAO
)
```

A média mantém a dimensão final na escala de 0 a 3 e atribui peso equivalente aos três indicadores, já que não foi disponibilizada uma regra de negócio que justificasse ponderações diferentes.

## 5. Score de relacionamento

O score final combina os três pilares principais:

```text
SCORE_RELACIONAMENTO =
média(
    SCORE_PRODUTOS,
    SCORE_TEMPO,
    SCORE_UTILIZACAO
)
```

Cada pilar possui, portanto, peso equivalente na classificação.

O score varia de 0 a 3.

## 6. Tratamento de registros com data inconsistente

Foram identificados **37 associados** cuja `DATA_ASSOCIACAO` é posterior à data de referência de 31/08/2026.

Para esses registros:

- a data original é preservada;
- `FLAG_DATA_FUTURA` recebe `Sim`;
- o tempo de relacionamento não é calculado;
- `SCORE_TEMPO` permanece ausente;
- o score final é calculado com as dimensões válidas restantes.

Essa escolha evita:

- excluir associados que possuem outras informações válidas;
- substituir a data por um valor artificial;
- penalizar o associado com score zero por um problema de qualidade da informação.

A coluna `QTD_DIMENSOES_SCORE` permite identificar quantas dimensões participaram do score final.

## 7. Classificação dos associados

Após análise da distribuição do `SCORE_RELACIONAMENTO`, foram definidas faixas conceituais para a classificação final.

Não foram utilizados quartis novamente nessa etapa, pois isso forçaria aproximadamente 25% da população em cada categoria, independentemente do comportamento real do score.

| Score | Classificação técnica |
|---:|---|
| `< 1,00` | Inicial |
| `1,00 a < 1,50` | Em Desenvolvimento |
| `1,50 a < 2,00` | Maduro |
| `>= 2,00` | Engajado |

Distribuição observada:

| Classificação | Associados | Participação |
|---|---:|---:|
| Inicial | 114 | 11,4% |
| Em Desenvolvimento | 348 | 34,8% |
| Maduro | 306 | 30,6% |
| Engajado | 232 | 23,2% |

## 8. Segmentos executivos

Para a camada de apresentação foi criada uma nomenclatura executiva equivalente à classificação técnica:

| Classificação técnica | Segmento executivo |
|---|---|
| Inicial | Vínculo Inicial |
| Em Desenvolvimento | Em Expansão |
| Maduro | Consolidado |
| Engajado | Alta Vinculação |

A coluna técnica é preservada para aderência ao desafio, enquanto `SEGMENTO_RELACIONAMENTO` pode ser utilizada na apresentação executiva do dashboard.

## 9. Regras de oportunidades

As oportunidades são sinalizações independentes. Um mesmo associado pode atender a mais de uma regra.

### 9.1 Cross-sell

Objetivo: identificar associados com maior capacidade econômica relativa, mas baixa diversificação de produtos.

Regra:

```text
RENDA_MENSAL >= Q3 da renda
E
QTD_PRODUTOS <= 2
```

Na população analisada:

**87 associados** atendem à regra.

### 9.2 Baixa utilização

Objetivo: identificar associados cuja utilização financeira está na parte inferior da população.

Regra:

```text
SCORE_UTILIZACAO < Q1 do score de utilização
```

Foi utilizado `< Q1`, em vez de `<= Q1`, para evitar que empates exatamente no primeiro quartil ampliassem excessivamente o grupo.

Na população analisada:

**159 associados** atendem à regra.

### 9.3 Relacionamento subaproveitado

Objetivo: identificar associados com relacionamento longo, porém baixa diversificação de produtos.

Regra:

```text
TEMPO_RELACIONAMENTO_ANOS >= Q3
E
QTD_PRODUTOS <= 2
```

Na população analisada:

**96 associados** atendem à regra.

## 10. Limitações da metodologia

- O score é relativo à população analisada e seus quartis.
- Em outra população, os limites dos scores baseados em quartis podem mudar.
- Não existe informação explícita de competência na base de movimentação.
- A metodologia utiliza somente as variáveis disponibilizadas no desafio.
- Não foi utilizada renda no score de relacionamento para evitar confundir capacidade econômica com intensidade de vínculo.
- O score não representa risco de crédito, rentabilidade, fidelidade, causalidade ou propensão estatística.
- Pesos iguais foram utilizados por ausência de critérios de negócio que justificassem ponderações diferentes.
