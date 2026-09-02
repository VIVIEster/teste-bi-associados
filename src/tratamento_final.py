"""
Tratamento e consolidação das bases do desafio de BI.

Valida as fontes, aplica as regras de qualidade definidas no diagnóstico,
consolida as bases, cria indicadores, score, segmentação e oportunidades
e exporta uma base limpa para consumo no Power BI.
"""

from pathlib import Path

import pandas as pd



# 1. CONFIGURAÇÃO
RAIZ_PROJETO = Path(__file__).resolve().parent.parent
CAMINHO_BASE = RAIZ_PROJETO / "data" / "raw" / "teste_bi_base_crua.xlsx"
CAMINHO_SAIDA = RAIZ_PROJETO / "data" / "processed" / "base_consolidada.xlsx"
DATA_REFERENCIA = pd.Timestamp("2026-08-31")

COLUNAS_PRODUTOS = [
    "CONTA_CORRENTE",
    "CARTAO",
    "CREDITO",
    "INVESTIMENTO",
    "CONSORCIO",
    "SEGURO",
]

MAPA_CIDADES = {
    "P. Branco": "Pato Branco",
    "Pato Branco": "Pato Branco",
    "PATO BRANCO": "Pato Branco",
    "Cascavel": "Cascavel",
    "Chapeco": "Chapecó",
    "Toledo": "Toledo",
    "Maringa": "Maringá",
}

MAPA_PRODUTOS = {"S": "Sim", "N": "Não"}

MAPA_SEGMENTOS = {
    "Inicial": "Vínculo Inicial",
    "Em Desenvolvimento": "Em Expansão",
    "Maduro": "Consolidado",
    "Engajado": "Alta Vinculação",
}



# 2. FUNÇÕES AUXILIARES
def validar_chave(df: pd.DataFrame, nome_base: str) -> None:
    """Valida presença, preenchimento e unicidade da coluna CHAVE."""
    if "CHAVE" not in df.columns:
        raise ValueError(f"A base {nome_base} não possui a coluna CHAVE.")
    if df["CHAVE"].isna().any():
        raise ValueError(f"A base {nome_base} possui CHAVE nula.")
    if not df["CHAVE"].is_unique:
        raise ValueError(f"A base {nome_base} possui CHAVE duplicada.")


def validar_produtos(df: pd.DataFrame) -> None:
    """Garante que as colunas de produtos usem apenas S/N na fonte."""
    valores_validos = {"S", "N"}
    for coluna in COLUNAS_PRODUTOS:
        encontrados = set(df[coluna].dropna().unique())
        if not encontrados.issubset(valores_validos):
            raise ValueError(
                f"A coluna {coluna} possui categorias inválidas: {encontrados}."
            )


def criar_score_quartis(serie: pd.Series) -> pd.Series:
    """Converte uma variável numérica em score de 0 a 3 pelos quartis."""
    q1, q2, q3 = serie.quantile([0.25, 0.50, 0.75]).tolist()

    if not q1 < q2 < q3:
        raise ValueError(
            "Os quartis não geraram limites distintos para criação do score."
        )

    return pd.cut(
        serie,
        bins=[float("-inf"), q1, q2, q3, float("inf")],
        labels=[0, 1, 2, 3],
        include_lowest=True,
    ).astype("Int64")



# 3. LEITURA E VALIDAÇÃO DAS BASES
if not CAMINHO_BASE.exists():
    raise FileNotFoundError(f"Base de dados não encontrada: {CAMINHO_BASE}")

associados = pd.read_excel(CAMINHO_BASE, sheet_name="Associados")
produtos = pd.read_excel(CAMINHO_BASE, sheet_name="Produtos")
movimentacao = pd.read_excel(CAMINHO_BASE, sheet_name="Movimentacao")

for nome, df in {
    "Associados": associados,
    "Produtos": produtos,
    "Movimentacao": movimentacao,
}.items():
    validar_chave(df, nome)

validar_produtos(produtos)

if not (
    set(associados["CHAVE"])
    == set(produtos["CHAVE"])
    == set(movimentacao["CHAVE"])
):
    raise ValueError("As bases não possuem o mesmo conjunto de CHAVES.")

associados_tratados = associados.copy()
produtos_tratados = produtos.copy()



# 4. TRATAMENTO DAS BASES
# D01 - Cidades padronizadas para uma nomenclatura única.
associados_tratados["CIDADE"] = (
    associados_tratados["CIDADE"].astype("string").str.strip()
)
cidades_nao_mapeadas = (
    set(associados_tratados["CIDADE"].dropna().unique()) - set(MAPA_CIDADES)
)
if cidades_nao_mapeadas:
    raise ValueError(
        "Foram encontradas cidades sem regra de padronização: "
        f"{sorted(cidades_nao_mapeadas)}"
    )
associados_tratados["CIDADE"] = associados_tratados["CIDADE"].replace(
    MAPA_CIDADES
)

# D02 - Agência tratada como código categórico e preservada com dois dígitos.
associados_tratados["AGENCIA"] = (
    associados_tratados["AGENCIA"].astype("string").str.strip().str.zfill(2)
)

# D03 - RENDA_MENSAL ausente é preservada sem imputação artificial.

# D04 - Data original é preservada e datas futuras são sinalizadas.
associados_tratados["DATA_ASSOCIACAO"] = pd.to_datetime(
    associados_tratados["DATA_ASSOCIACAO"], errors="raise"
).dt.normalize()
associados_tratados["FLAG_DATA_FUTURA"] = (
    associados_tratados["DATA_ASSOCIACAO"] > DATA_REFERENCIA
)

# Produtos continuam categóricos, mas a saída usa rótulos legíveis.
for coluna in COLUNAS_PRODUTOS:
    produtos_tratados[coluna] = (
        produtos_tratados[coluna]
        .astype("string")
        .str.strip()
        .str.upper()
        .map(MAPA_PRODUTOS)
    )

if produtos_tratados[COLUNAS_PRODUTOS].isna().any().any():
    raise ValueError("A padronização dos produtos gerou categorias nulas.")



# 5. CONSOLIDAÇÃO
base_consolidada = associados_tratados.merge(
    produtos_tratados,
    on="CHAVE",
    how="left",
    validate="one_to_one",
    indicator="_merge_produtos",
)
if (base_consolidada["_merge_produtos"] != "both").any():
    raise ValueError("Existem associados sem correspondência em Produtos.")
base_consolidada.drop(columns="_merge_produtos", inplace=True)

base_consolidada = base_consolidada.merge(
    movimentacao,
    on="CHAVE",
    how="left",
    validate="one_to_one",
    indicator="_merge_movimentacao",
)
if (base_consolidada["_merge_movimentacao"] != "both").any():
    raise ValueError("Existem associados sem correspondência em Movimentacao.")
base_consolidada.drop(columns="_merge_movimentacao", inplace=True)



# 6. INDICADORES
base_consolidada["QTD_PRODUTOS"] = (
    base_consolidada[COLUNAS_PRODUTOS].eq("Sim").sum(axis=1)
)
if not base_consolidada["QTD_PRODUTOS"].between(0, len(COLUNAS_PRODUTOS)).all():
    raise ValueError("QTD_PRODUTOS apresentou valor fora do intervalo esperado.")

base_consolidada["FAIXA_RENDA"] = (
    pd.cut(
        base_consolidada["RENDA_MENSAL"],
        bins=[float("-inf"), 3000, 8000, 15000, float("inf")],
        labels=[
            "Até R$ 3.000",
            "R$ 3.001 a R$ 8.000",
            "R$ 8.001 a R$ 15.000",
            "Acima de R$ 15.000",
        ],
    )
    .astype("string")
    .fillna("Não informado")
)

base_consolidada["TEMPO_RELACIONAMENTO_DIAS"] = (
    DATA_REFERENCIA - base_consolidada["DATA_ASSOCIACAO"]
).dt.days.astype("Float64")
base_consolidada.loc[
    base_consolidada["FLAG_DATA_FUTURA"], "TEMPO_RELACIONAMENTO_DIAS"
] = pd.NA

base_consolidada["TEMPO_RELACIONAMENTO_ANOS"] = (
    base_consolidada["TEMPO_RELACIONAMENTO_DIAS"] / 365.25
)

if base_consolidada["TEMPO_RELACIONAMENTO_DIAS"].dropna().lt(0).any():
    raise ValueError("Foram gerados tempos de relacionamento negativos.")



# 7. SCORE E SEGMENTAÇÃO
base_consolidada["SCORE_PRODUTOS"] = pd.cut(
    base_consolidada["QTD_PRODUTOS"],
    bins=[-1, 1, 2, 4, 6],
    labels=[0, 1, 2, 3],
).astype("Int64")

base_consolidada["SCORE_TEMPO"] = criar_score_quartis(
    base_consolidada["TEMPO_RELACIONAMENTO_ANOS"]
)
base_consolidada["SCORE_SALDO"] = criar_score_quartis(
    base_consolidada["SALDO_MEDIO"]
)
base_consolidada["SCORE_PIX"] = criar_score_quartis(base_consolidada["PIX_MENSAL"])
base_consolidada["SCORE_CARTAO"] = criar_score_quartis(
    base_consolidada["COMPRAS_CARTAO"]
)

base_consolidada["SCORE_UTILIZACAO"] = base_consolidada[
    ["SCORE_SALDO", "SCORE_PIX", "SCORE_CARTAO"]
].mean(axis=1)

base_consolidada["SCORE_RELACIONAMENTO"] = base_consolidada[
    ["SCORE_PRODUTOS", "SCORE_TEMPO", "SCORE_UTILIZACAO"]
].mean(axis=1)

base_consolidada["QTD_DIMENSOES_SCORE"] = base_consolidada[
    ["SCORE_PRODUTOS", "SCORE_TEMPO", "SCORE_UTILIZACAO"]
].notna().sum(axis=1)

if not base_consolidada["SCORE_RELACIONAMENTO"].between(0, 3).all():
    raise ValueError("SCORE_RELACIONAMENTO fora do intervalo esperado de 0 a 3.")

base_consolidada["CLASSIFICACAO"] = pd.cut(
    base_consolidada["SCORE_RELACIONAMENTO"],
    bins=[float("-inf"), 1.0, 1.5, 2.0, float("inf")],
    labels=["Inicial", "Em Desenvolvimento", "Maduro", "Engajado"],
    right=False,
)
base_consolidada["SEGMENTO_RELACIONAMENTO"] = (
    base_consolidada["CLASSIFICACAO"].astype("string").map(MAPA_SEGMENTOS)
)



# 8. OPORTUNIDADES
q3_renda = base_consolidada["RENDA_MENSAL"].quantile(0.75)
q1_utilizacao = base_consolidada["SCORE_UTILIZACAO"].quantile(0.25)
q3_tempo = base_consolidada["TEMPO_RELACIONAMENTO_ANOS"].quantile(0.75)

base_consolidada["OPORT_CROSS_SELL"] = (
    base_consolidada["RENDA_MENSAL"].ge(q3_renda)
    & base_consolidada["QTD_PRODUTOS"].le(2)
)
base_consolidada["OPORT_BAIXA_UTILIZACAO"] = (
    base_consolidada["SCORE_UTILIZACAO"] < q1_utilizacao
)
base_consolidada["OPORT_RELACIONAMENTO_SUBAPROVEITADO"] = (
    base_consolidada["TEMPO_RELACIONAMENTO_ANOS"].ge(q3_tempo)
    & base_consolidada["QTD_PRODUTOS"].le(2)
)



# 9. PREPARAÇÃO DA SAÍDA
# A classificação usa a precisão integral. O arredondamento abaixo é apenas
# para tornar a base final legível e adequada ao consumo analítico.
base_saida = base_consolidada.copy()
base_saida["TEMPO_RELACIONAMENTO_ANOS"] = base_saida[
    "TEMPO_RELACIONAMENTO_ANOS"
].round(2)
base_saida["SCORE_UTILIZACAO"] = base_saida["SCORE_UTILIZACAO"].round(2)
base_saida["SCORE_RELACIONAMENTO"] = base_saida["SCORE_RELACIONAMENTO"].round(2)

# TEMPO_RELACIONAMENTO_DIAS é auxiliar de cálculo e não precisa ir ao Power BI.
base_saida.drop(columns="TEMPO_RELACIONAMENTO_DIAS", inplace=True)

# Flags são exportadas em português para facilitar leitura e filtros no BI.
colunas_flags = [
    "FLAG_DATA_FUTURA",
    "OPORT_CROSS_SELL",
    "OPORT_BAIXA_UTILIZACAO",
    "OPORT_RELACIONAMENTO_SUBAPROVEITADO",
]
for coluna in colunas_flags:
    base_saida[coluna] = base_saida[coluna].map({True: "Sim", False: "Não"})

# A data continua sendo um valor de data, mas sem componente de horário na saída.
base_saida["DATA_ASSOCIACAO"] = base_saida["DATA_ASSOCIACAO"].dt.date

# Organização lógica das colunas da base entregue.
ORDEM_COLUNAS = [
    "CHAVE",
    "NOME",
    "AGENCIA",
    "CIDADE",
    "DATA_ASSOCIACAO",
    "RENDA_MENSAL",
    "FAIXA_RENDA",
    "CONTA_CORRENTE",
    "CARTAO",
    "CREDITO",
    "INVESTIMENTO",
    "CONSORCIO",
    "SEGURO",
    "QTD_PRODUTOS",
    "SALDO_MEDIO",
    "PIX_MENSAL",
    "COMPRAS_CARTAO",
    "FLAG_DATA_FUTURA",
    "TEMPO_RELACIONAMENTO_ANOS",
    "SCORE_PRODUTOS",
    "SCORE_TEMPO",
    "SCORE_SALDO",
    "SCORE_PIX",
    "SCORE_CARTAO",
    "SCORE_UTILIZACAO",
    "SCORE_RELACIONAMENTO",
    "QTD_DIMENSOES_SCORE",
    "CLASSIFICACAO",
    "SEGMENTO_RELACIONAMENTO",
    "OPORT_CROSS_SELL",
    "OPORT_BAIXA_UTILIZACAO",
    "OPORT_RELACIONAMENTO_SUBAPROVEITADO",
]
base_saida = base_saida[ORDEM_COLUNAS]



# 10. VALIDAÇÕES FINAIS E EXPORTAÇÃO
if len(base_saida) != len(associados):
    raise ValueError("A base final não preservou a quantidade de associados.")
if not base_saida["CHAVE"].is_unique:
    raise ValueError("A base final possui CHAVE duplicada.")
if base_saida["CLASSIFICACAO"].isna().any():
    raise ValueError("A base final possui associados sem classificação.")
if base_saida["SEGMENTO_RELACIONAMENTO"].isna().any():
    raise ValueError("A base final possui associados sem segmento de relacionamento.")

CAMINHO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
with pd.ExcelWriter(CAMINHO_SAIDA, engine="openpyxl") as writer:
    base_saida.to_excel(writer, index=False, sheet_name="Base Consolidada")

    # Formatação visual mínima sem alterar os tipos numéricos da base.
    planilha = writer.sheets["Base Consolidada"]
    planilha.freeze_panes = "A2"
    planilha.auto_filter.ref = planilha.dimensions

    for celula in planilha["E"][1:]:
        celula.number_format = "DD/MM/YYYY"

    for coluna in ("F", "O", "Q"):
        for celula in planilha[coluna][1:]:
            celula.number_format = 'R$ #,##0.00'

    for coluna in ("S", "Y", "Z"):
        for celula in planilha[coluna][1:]:
            celula.number_format = "0.00"

if not CAMINHO_SAIDA.exists():
    raise FileNotFoundError("A base consolidada não foi gerada.")

print("\nProcessamento concluído com sucesso.")
print(f"Arquivo gerado: {CAMINHO_SAIDA}")
print(f"Associados processados: {len(base_saida)}")
print(f"Colunas finais: {len(base_saida.columns)}")
