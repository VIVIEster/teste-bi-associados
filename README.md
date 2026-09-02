# Desafio Técnico de BI

Projeto desenvolvido como parte de um desafio técnico para a vaga de Assistente de BI.

A solução consolida dados cadastrais, produtos e movimentação financeira de associados, realiza tratamento e validação de qualidade em Python, cria indicadores de relacionamento, uma metodologia própria de segmentação e critérios de oportunidades comerciais. A camada analítica é apresentada em um dashboard executivo desenvolvido no Power BI.

## Status do projeto

- [x] Diagnóstico e mapeamento das bases
- [x] Tratamento e padronização dos dados
- [x] Consolidação das três fontes
- [x] Criação de indicadores derivados
- [x] Criação do score de relacionamento
- [x] Segmentação dos associados
- [x] Identificação de oportunidades
- [x] Geração da base consolidada
- [x] Dashboard Power BI

## Objetivo

Construir uma solução de Business Intelligence capaz de transformar três bases independentes em uma visão consolidada por associado, com foco em:

- qualidade e consistência dos dados;
- perfil dos associados;
- quantidade e diversidade de produtos;
- tempo de relacionamento;
- utilização financeira;
- segmentação por nível de relacionamento;
- identificação de oportunidades de aprofundamento do vínculo.

## Estrutura do projeto

```text
teste-bi-associados/
│
├── data/
│   ├── raw/
│   │   └── teste_bi_base_crua.xlsx
│   └── processed/
│       └── base_consolidada.xlsx
│
├── docs/
│   ├── mapeamento_dados.md
│   └── metodologia_analitica.md
│
├── src/
│   ├── diagnostico.py
│   ├── tratamento_inicial.py
│   └── tratamento_final.py
│
├── dashboard/
│   └── Dashboard.pbix
│
├── .gitignore
├── README.md
└── requirements.txt
```

## Papel dos principais arquivos

- `src/diagnostico.py`: inspeção inicial e validação programática das bases recebidas.
- `src/tratamento_inicial.py`: versão intermediária preservada para evidenciar a evolução do tratamento.
- `src/tratamento_final.py`: pipeline final de validação, tratamento, consolidação, indicadores, score, oportunidades e exportação.
- `data/processed/base_consolidada.xlsx`: base final utilizada como fonte do Power BI.
- `docs/mapeamento_dados.md`: diagnóstico das fontes, problemas encontrados, decisões de tratamento e resultado final.
- `docs/metodologia_analitica.md`: documentação do score de relacionamento, segmentação e regras de oportunidades.

## Tecnologias utilizadas

- Python 3
- pandas
- openpyxl
- Excel
- Git / GitHub
- Power BI Desktop

As versões das dependências Python utilizadas estão registradas em `requirements.txt`.

## Pipeline dos dados

O fluxo implementado segue as seguintes etapas:

```text
Base bruta
    ↓
Diagnóstico de qualidade
    ↓
Validações de integridade
    ↓
Tratamento e padronização
    ↓
Consolidação pela CHAVE
    ↓
Indicadores derivados
    ↓
Score de relacionamento
    ↓
Segmentação
    ↓
Oportunidades
    ↓
Base consolidada
    ↓
Power BI
```

As três abas recebidas — `Associados`, `Produtos` e `Movimentacao` — possuem 1.000 registros e utilizam `CHAVE` como identificador comum. A correspondência 1:1 entre as três fontes foi validada programaticamente antes da consolidação.

## Tratamentos realizados

Os principais tratamentos aplicados foram:

- validação da presença, preenchimento e unicidade de `CHAVE`;
- validação da cobertura integral das chaves entre as três fontes;
- padronização das diferentes grafias de cidade;
- conversão de `AGENCIA` para código categórico textual com dois dígitos;
- preservação dos 12 valores ausentes de `RENDA_MENSAL`, sem imputação artificial;
- criação de `FAIXA_RENDA`, incluindo a categoria `Não informado`;
- preservação das datas originais de associação;
- sinalização dos registros com data de associação posterior à data de referência;
- padronização dos indicadores de produtos de `S/N` para `Sim/Não` na base entregue;
- consolidação 1:1 das fontes;
- validação da quantidade final de registros e da unicidade da chave;
- preparação da saída com tipos, precisão e formatação adequados para consumo analítico.

A data de referência adotada para o cálculo de relacionamento é **31/08/2026**, mantida fixa para garantir reprodutibilidade do resultado.

## Indicadores

A base consolidada contém, entre outros, os seguintes indicadores derivados:

- `QTD_PRODUTOS`
- `FAIXA_RENDA`
- `TEMPO_RELACIONAMENTO_ANOS`
- `SCORE_PRODUTOS`
- `SCORE_TEMPO`
- `SCORE_SALDO`
- `SCORE_PIX`
- `SCORE_CARTAO`
- `SCORE_UTILIZACAO`
- `SCORE_RELACIONAMENTO`
- `CLASSIFICACAO`
- `SEGMENTO_RELACIONAMENTO`
- flags de oportunidades comerciais

## Metodologia de classificação

Foi desenvolvido um **scorecard híbrido**, combinando regras interpretáveis de negócio e quartis da própria população.

A metodologia considera três dimensões principais:

1. **Diversificação de produtos**
2. **Tempo de relacionamento**
3. **Utilização financeira**

Produtos são pontuados por faixas de quantidade. Tempo, saldo médio, PIX mensal e compras no cartão são pontuados de acordo com quartis da população.

O score final varia de 0 a 3 e determina quatro níveis técnicos de classificação:

| Score | Classificação | Segmento executivo |
|---:|---|---|
| `< 1,00` | Inicial | Vínculo Inicial |
| `1,00 a < 1,50` | Em Desenvolvimento | Em Expansão |
| `1,50 a < 2,00` | Maduro | Consolidado |
| `>= 2,00` | Engajado | Alta Vinculação |

A descrição completa está disponível em [`docs/metodologia_analitica.md`](docs/metodologia_analitica.md).

## Oportunidades identificadas

Foram construídas três sinalizações analíticas:

- **Cross-sell:** renda no quartil superior e até dois produtos ativos.
- **Baixa utilização:** score de utilização abaixo do primeiro quartil.
- **Relacionamento subaproveitado:** tempo de relacionamento no quartil superior e até dois produtos ativos.

Na base analisada foram identificados:

| Oportunidade | Associados |
|---|---:|
| Cross-sell | 87 |
| Baixa utilização | 159 |
| Relacionamento subaproveitado | 96 |

Um mesmo associado pode atender a mais de uma oportunidade.

## Dashboard

O dashboard foi desenvolvido no Power BI Desktop a partir da base consolidada gerada pelo pipeline Python.

O arquivo está disponível em:

`dashboard/dashboard_associados.pbix`

A solução foi organizada em quatro páginas:

1. **Visão Geral** — principais indicadores executivos da carteira, distribuição por renda e segmento de relacionamento.
2. **Relacionamento** — análise da carteira por cidade, agência, faixa de renda e tempo de relacionamento.
3. **Classificação** — distribuição quantitativa e percentual dos segmentos e análise dos pilares que compõem o score de relacionamento.
4. **Oportunidades** — identificação de associados com potencial de cross-sell, baixa utilização e relacionamento subaproveitado, incluindo análise por agência e lista de associados prioritários.

Os principais indicadores do dashboard são calculados dinamicamente no Power BI e respondem aos filtros disponíveis em cada página.


## Como executar o projeto: 

### 1. Clonar o repositório

```bash
git clone https://github.com/VIVIEster/teste-bi-associados.git
cd teste-bi-associados
```

### 2. Criar um ambiente virtual

No Windows / PowerShell:

```powershell
python -m venv .venv
```

### 3. Ativar o ambiente virtual

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Instalar as dependências

```powershell
python -m pip install -r requirements.txt
```

### 5. Executar o diagnóstico

```powershell
python src\diagnostico.py
```

### 6. Executar o tratamento final

```powershell
python src\tratamento_final.py
```

O processo gera:

```text
data/processed/base_consolidada.xlsx
```

## Documentação técnica

- [Mapeamento e diagnóstico dos dados](docs/mapeamento_dados.md)
- [Metodologia analítica](docs/metodologia_analitica.md)

## Limitações e premissas

- Os dados utilizados no desafio são fictícios.
- A base de movimentação não contém uma coluna explícita de competência/período.
- A interpretação de `PIX_MENSAL` e `COMPRAS_CARTAO` respeita os nomes dos campos fornecidos, pois não foi disponibilizado um dicionário adicional com suas unidades.
- Os quartis utilizados no score são relativos à população analisada; em outra população, os limites podem mudar.
- A metodologia representa nível de relacionamento com base nas variáveis disponíveis e não deve ser interpretada como modelo de risco, propensão ou causalidade.
- Registros com data de associação futura permanecem sinalizados e não recebem score de tempo; as demais dimensões válidas continuam sendo consideradas.

