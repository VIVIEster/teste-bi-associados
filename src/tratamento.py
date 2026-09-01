"""
Tratamento e consolidação das bases do desafio de BI.

Este script aplica as regras de tratamento definidas após o
diagnóstico inicial, preserva os dados brutos e prepara as bases
para posterior consolidação e criação dos indicadores.
"""

from pathlib import Path
import pandas as pd

# 1. configuração
RAIZ_PROJETO = Path(__file__).resolve().parent.parent
CAMINHO_BASE = RAIZ_PROJETO / "data" / "raw" / "teste_bi_base_crua.xlsx"
CAMINHO_SAIDA = RAIZ_PROJETO / "data" / "processed" / "base_consolidada.xlsx"
DATA_REFERENCIA = pd.Timestamp("2026-08-31")

if not CAMINHO_BASE.exists():
    raise FileNotFoundError(
        f"Base de dados não encontrada: {CAMINHO_BASE}"
    )

# 2. leitura das bases
associados = pd.read_excel(
    CAMINHO_BASE,
    sheet_name="Associados",
)

produtos = pd.read_excel(
    CAMINHO_BASE,
    sheet_name="Produtos",
)

movimentacao = pd.read_excel(
    CAMINHO_BASE,
    sheet_name="Movimentacao",
)

# preservar os DataFrames carregados como referência do dado bruto.
associados_tratados = associados.copy()
produtos_tratados = produtos.copy()
movimentacao_tratada = movimentacao.copy()

# 3. validações antes do tratamento
def validar_chave(df, nome_base):
    """Valida a presença, preenchimento e unicidade da CHAVE."""

    if "CHAVE" not in df.columns:
        raise ValueError(
            f"A base {nome_base} não possui a coluna CHAVE."
        )

    if df["CHAVE"].isna().any():
        raise ValueError(
            f"A base {nome_base} possui CHAVE nula."
        )

    if not df["CHAVE"].is_unique:
        raise ValueError(
            f"A base {nome_base} possui CHAVE duplicada."
        )


validar_chave(associados, "Associados")
validar_chave(produtos, "Produtos")
validar_chave(movimentacao, "Movimentacao")

chaves_associados = set(associados["CHAVE"])
chaves_produtos = set(produtos["CHAVE"])
chaves_movimentacao = set(movimentacao["CHAVE"])

if not (
    chaves_associados
    == chaves_produtos
    == chaves_movimentacao
):
    raise ValueError(
        "As bases não possuem o mesmo conjunto de CHAVES."
    )

# 4. tratamento de associados

# D01 - padronização das cidades
MAPA_CIDADES = {
    "P. Branco": "Pato Branco",
    "Pato Branco": "Pato Branco",
    "PATO BRANCO": "Pato Branco",
    "Cascavel": "Cascavel",
    "Chapeco": "Chapecó",
    "Toledo": "Toledo",
    "Maringa": "Maringá",
}

cidades_origem = set(
    associados_tratados["CIDADE"].dropna().unique()
)

cidades_nao_mapeadas = cidades_origem - set(MAPA_CIDADES)

if cidades_nao_mapeadas:
    raise ValueError(
        "Foram encontradas cidades sem regra de padronização: "
        f"{sorted(cidades_nao_mapeadas)}"
    )

associados_tratados["CIDADE"] = (
    associados_tratados["CIDADE"]
    .replace(MAPA_CIDADES)
)

print("\nCidades após padronização:")
print(
    associados_tratados["CIDADE"]
    .value_counts()
    .sort_index()
)

# D02 - agência é um código categórico, não uma medida numérica.
associados_tratados["AGENCIA"] = (
    associados_tratados["AGENCIA"]
    .astype("string")
    .str.zfill(2)
)

print("\nAgências após tratamento:")
print(
    associados_tratados["AGENCIA"]
    .value_counts()
    .sort_index()
)

# D03 - preservar renda ausente sem imputação artificial.
nulos_renda_antes = associados["RENDA_MENSAL"].isna().sum()
nulos_renda_depois = (
    associados_tratados["RENDA_MENSAL"]
    .isna()
    .sum()
)

if nulos_renda_antes != nulos_renda_depois:
    raise ValueError(
        "A quantidade de rendas nulas foi alterada indevidamente."
    )

# D04 - preservar a data original e sinalizar inconsistências.
associados_tratados["FLAG_DATA_FUTURA"] = (
    associados_tratados["DATA_ASSOCIACAO"]
    > DATA_REFERENCIA
)

print("\nRegistros sinalizados com data futura:")
print(
    associados_tratados["FLAG_DATA_FUTURA"]
    .value_counts()
)


# 5. consolidação das bases
base_consolidada = associados_tratados.merge(
    produtos_tratados,
    on="CHAVE",
    how="left",
    validate="one_to_one",
    indicator="STATUS_PRODUTOS",
)
if not (
    base_consolidada["STATUS_PRODUTOS"] == "both"
).all():
    raise ValueError(
        "Existem associados sem correspondência na base de Produtos."
    )

base_consolidada = base_consolidada.drop(
    columns="STATUS_PRODUTOS"
)

base_consolidada = base_consolidada.merge(
    movimentacao_tratada,
    on="CHAVE",
    how="left",
    validate="one_to_one",
    indicator="STATUS_MOVIMENTACAO",
)
if not (
    base_consolidada["STATUS_MOVIMENTACAO"] == "both"
).all():
    raise ValueError(
        "Existem associados sem correspondência na base de Movimentação."
    )

base_consolidada = base_consolidada.drop(
    columns="STATUS_MOVIMENTACAO"
)

registros_esperados = len(associados_tratados)

if len(base_consolidada) != registros_esperados:
    raise ValueError(
        "A consolidação alterou a quantidade de associados. "
        f"Esperado: {registros_esperados}. "
        f"Obtido: {len(base_consolidada)}."
    )
if not base_consolidada["CHAVE"].is_unique:
    raise ValueError(
        "A base consolidada possui CHAVE duplicada."
    )

print("\nBase consolidada criada com sucesso.")

print(
    f"Dimensões: {base_consolidada.shape}"
)

print("\nColunas da base consolidada:")
print(
    base_consolidada.columns.tolist()
)

# 6. criação dos indicadores

colunas_produtos = [
    "CONTA_CORRENTE",
    "CARTAO",
    "CREDITO",
    "INVESTIMENTO",
    "CONSORCIO",
    "SEGURO",
]

base_consolidada["QTD_PRODUTOS"] = (
    base_consolidada[colunas_produtos]
    .eq("S")
    .sum(axis=1)
)
print("\nDistribuição da quantidade de produtos:")
print(
    base_consolidada["QTD_PRODUTOS"]
    .value_counts()
    .sort_index()
)

quantidade_sem_produtos = (
    base_consolidada["QTD_PRODUTOS"] == 0
).sum()

if quantidade_sem_produtos != 13:
    raise ValueError(
        "A quantidade de associados sem produtos "
        "não corresponde ao diagnóstico inicial."
    )

if not base_consolidada["QTD_PRODUTOS"].between(0, 6).all():
    raise ValueError(
        "QTD_PRODUTOS apresentou valor fora do intervalo esperado."
    )

faixas_renda = [
    float("-inf"),
    3000,
    8000,
    15000,
    float("inf"),
]

rotulos_renda = [
    "Até R$ 3.000",
    "R$ 3.001 a R$ 8.000",
    "R$ 8.001 a R$ 15.000",
    "Acima de R$ 15.000",
]

base_consolidada["FAIXA_RENDA"] = pd.cut(
    base_consolidada["RENDA_MENSAL"],
    bins=faixas_renda,
    labels=rotulos_renda,
)

base_consolidada["FAIXA_RENDA"] = (
    base_consolidada["FAIXA_RENDA"]
    .cat.add_categories("Não informado")
    .fillna("Não informado")
)

print("\nDistribuição por faixa de renda:")
print(
    base_consolidada["FAIXA_RENDA"]
    .value_counts(dropna=False)
)

quantidade_renda_nao_informada = (
    base_consolidada["FAIXA_RENDA"] == "Não informado"
).sum()

if quantidade_renda_nao_informada != 12:
    raise ValueError(
        "A quantidade de rendas não informadas "
        "não corresponde ao diagnóstico."
    )

base_consolidada["TEMPO_RELACIONAMENTO_DIAS"] = (
    DATA_REFERENCIA
    - base_consolidada["DATA_ASSOCIACAO"]
).dt.days

base_consolidada.loc[
    base_consolidada["FLAG_DATA_FUTURA"],
    "TEMPO_RELACIONAMENTO_DIAS",
] = pd.NA

base_consolidada["TEMPO_RELACIONAMENTO_ANOS"] = (
    base_consolidada["TEMPO_RELACIONAMENTO_DIAS"]
    / 365.25
)

if (
    base_consolidada["TEMPO_RELACIONAMENTO_DIAS"]
    .dropna()
    .lt(0)
    .any()
):
    raise ValueError(
        "Foram gerados tempos de relacionamento negativos."
    )

tempos_nao_calculados = (
    base_consolidada["TEMPO_RELACIONAMENTO_ANOS"]
    .isna()
    .sum()
)

if tempos_nao_calculados != 37:
    raise ValueError(
        "A quantidade de tempos de relacionamento ausentes "
        "não corresponde às datas futuras identificadas."
    )

print("\nTempo de relacionamento em anos:")
print(
    base_consolidada["TEMPO_RELACIONAMENTO_ANOS"]
    .describe()
)

print("\nIndicadores criados:")
print(
    base_consolidada[
        [
            "CHAVE",
            "QTD_PRODUTOS",
            "FAIXA_RENDA",
            "TEMPO_RELACIONAMENTO_ANOS",
        ]
    ].head(10)
)

# 7. score de relacionamento

# Pilar 1 - diversificação de produtos
base_consolidada["SCORE_PRODUTOS"] = pd.cut(
    base_consolidada["QTD_PRODUTOS"],
    bins=[-1, 1, 2, 4, 6],
    labels=[0, 1, 2, 3],
).astype("Int64")

print("\nDistribuição do SCORE_PRODUTOS:")
print(
    base_consolidada["SCORE_PRODUTOS"]
    .value_counts()
    .sort_index()
)


def criar_score_quartis(serie):
    """Converte uma variável numérica em score de 0 a 3 pelos quartis."""

    q1 = serie.quantile(0.25)
    q2 = serie.quantile(0.50)
    q3 = serie.quantile(0.75)

    if not q1 < q2 < q3:
        raise ValueError(
        "Os quartis não geraram limites distintos "
        "para criação do score."
    )

    return pd.cut(
        serie,
        bins=[
            float("-inf"),
            q1,
            q2,
            q3,
            float("inf"),
        ],
        labels=[0, 1, 2, 3],
        include_lowest=True,
    ).astype("Int64")


base_consolidada["SCORE_TEMPO"] = criar_score_quartis(
    base_consolidada["TEMPO_RELACIONAMENTO_ANOS"]
)

print("\nDistribuição do SCORE_TEMPO:")
print(
    base_consolidada["SCORE_TEMPO"]
    .value_counts(dropna=False)
    .sort_index()
)

base_consolidada["SCORE_SALDO"] = criar_score_quartis(
    base_consolidada["SALDO_MEDIO"]
)

base_consolidada["SCORE_PIX"] = criar_score_quartis(
    base_consolidada["PIX_MENSAL"]
)

base_consolidada["SCORE_CARTAO"] = criar_score_quartis(
    base_consolidada["COMPRAS_CARTAO"]
)

base_consolidada["SCORE_UTILIZACAO"] = (
    base_consolidada[
        [
            "SCORE_SALDO",
            "SCORE_PIX",
            "SCORE_CARTAO",
        ]
    ]
    .mean(axis=1)
)

base_consolidada["SCORE_RELACIONAMENTO"] = (
    base_consolidada[
        [
            "SCORE_PRODUTOS",
            "SCORE_TEMPO",
            "SCORE_UTILIZACAO",
        ]
    ]
    .mean(axis=1)
)

base_consolidada["QTD_DIMENSOES_SCORE"] = (
    base_consolidada[
        [
            "SCORE_PRODUTOS",
            "SCORE_TEMPO",
            "SCORE_UTILIZACAO",
        ]
    ]
    .notna()
    .sum(axis=1)
)

print("\nDistribuição do SCORE_RELACIONAMENTO:")
print(
    base_consolidada["SCORE_RELACIONAMENTO"]
    .describe()
)

print("\nDimensões utilizadas no score:")
print(
    base_consolidada["QTD_DIMENSOES_SCORE"]
    .value_counts()
    .sort_index()
)

print("\nExemplo dos scores:")
print(
    base_consolidada[
        [
            "CHAVE",
            "SCORE_PRODUTOS",
            "SCORE_TEMPO",
            "SCORE_SALDO",
            "SCORE_PIX",
            "SCORE_CARTAO",
            "SCORE_UTILIZACAO",
            "SCORE_RELACIONAMENTO",
            "QTD_DIMENSOES_SCORE",
        ]
    ].head(15)
)

if not (
    base_consolidada["SCORE_RELACIONAMENTO"]
    .between(0, 3)
    .all()
):
    raise ValueError(
        "SCORE_RELACIONAMENTO fora do intervalo esperado de 0 a 3."
    )


# classificação final baseada no score agregado.
base_consolidada["CLASSIFICACAO"] = pd.cut(
    base_consolidada["SCORE_RELACIONAMENTO"],
    bins=[
        float("-inf"),
        1.0,
        1.5,
        2.0,
        float("inf"),
    ],
    labels=[
        "Inicial",
        "Em Desenvolvimento",
        "Maduro",
        "Engajado",
    ],
    right=False,
)

print("\nDistribuição da classificação:")
print(
    base_consolidada["CLASSIFICACAO"]
    .value_counts()
    .sort_index()
)

print("\nDistribuição percentual da classificação:")
print(
    base_consolidada["CLASSIFICACAO"]
    .value_counts(normalize=True)
    .sort_index()
    .mul(100)
    .round(2)
)

if base_consolidada["CLASSIFICACAO"].isna().any():
    raise ValueError(
        "Existem associados sem classificação."
    )

classificacoes_esperadas = {
    "Inicial",
    "Em Desenvolvimento",
    "Maduro",
    "Engajado",
}

classificacoes_encontradas = set(
    base_consolidada["CLASSIFICACAO"]
    .astype("string")
    .unique()
)

if classificacoes_encontradas != classificacoes_esperadas:
    raise ValueError(
        "As classificações encontradas diferem das esperadas."
    )

mapa_segmentos = {
    "Inicial": "Vínculo Inicial",
    "Em Desenvolvimento": "Em Expansão",
    "Maduro": "Consolidado",
    "Engajado": "Alta Vinculação",
}

base_consolidada["SEGMENTO_RELACIONAMENTO"] = (
    base_consolidada["CLASSIFICACAO"]
    .astype("string")
    .map(mapa_segmentos)
)

if base_consolidada["SEGMENTO_RELACIONAMENTO"].isna().any():
    raise ValueError(
        "Existem associados sem segmento de relacionamento."
    )

print("\nDistribuição dos segmentos de relacionamento:")
print(
    base_consolidada["SEGMENTO_RELACIONAMENTO"]
    .value_counts()
)


# 8. oportunidades
q3_renda = base_consolidada["RENDA_MENSAL"].quantile(0.75)

base_consolidada["OPORT_CROSS_SELL"] = (
    base_consolidada["RENDA_MENSAL"].ge(q3_renda)
    & base_consolidada["QTD_PRODUTOS"].le(2)
)

q1_utilizacao = base_consolidada["SCORE_UTILIZACAO"].quantile(0.25)

base_consolidada["OPORT_BAIXA_UTILIZACAO"] = (
    base_consolidada["SCORE_UTILIZACAO"] < q1_utilizacao
)

q3_tempo = base_consolidada[
    "TEMPO_RELACIONAMENTO_ANOS"
].quantile(0.75)

base_consolidada["OPORT_RELACIONAMENTO_SUBAPROVEITADO"] = (
    base_consolidada["TEMPO_RELACIONAMENTO_ANOS"].ge(q3_tempo)
    & base_consolidada["QTD_PRODUTOS"].le(2)
)

colunas_oportunidades = [
    "OPORT_CROSS_SELL",
    "OPORT_BAIXA_UTILIZACAO",
    "OPORT_RELACIONAMENTO_SUBAPROVEITADO",
]

print("\nOportunidades identificadas:")

for coluna in colunas_oportunidades:
    print(
        f"{coluna}: "
        f"{base_consolidada[coluna].sum()}"
    )

