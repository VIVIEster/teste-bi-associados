"""
Diagnóstico inicial das bases do desafio de BI.

Este script realiza apenas leitura e validação dos dados.
Nenhum tratamento ou alteração é aplicado nesta etapa.
"""

from pathlib import Path
import pandas as pd

# configuração dos caminhos
RAIZ_PROJETO = Path(__file__).resolve().parent.parent
CAMINHO_BASE = RAIZ_PROJETO / "data" / "raw" / "teste_bi_base_crua.xlsx"

print(f"Raiz do projeto: {RAIZ_PROJETO}")
print(f"Arquivo de dados: {CAMINHO_BASE}")
print(f"Arquivo existe: {CAMINHO_BASE.exists()}") 

# leitura das bases
arquivo_excel = pd.ExcelFile(CAMINHO_BASE)
print(f"Abas encontradas: {arquivo_excel.sheet_names}") 

associados = pd.read_excel(CAMINHO_BASE, sheet_name="Associados")
produtos = pd.read_excel(CAMINHO_BASE, sheet_name="Produtos")
movimentacao = pd.read_excel(CAMINHO_BASE, sheet_name="Movimentacao")       

print("\nDimensões das bases:")
print(f"Associados: {associados.shape}")
print(f"Produtos: {produtos.shape}")
print(f"Movimentacao: {movimentacao.shape}") 

print("\nColunas:")
print(f"Associados: {associados.columns.tolist()}")
print(f"Produtos: {produtos.columns.tolist()}")
print(f"Movimentacao: {movimentacao.columns.tolist()}")

# validação estrutural
print("\nTipos das colunas:")

print("\nAssociados:")
print(associados.dtypes)

print("\nProdutos:")
print(produtos.dtypes)

print("\nMovimentacao:")
print(movimentacao.dtypes)

print("\nValores nulos:")

print("\nAssociados:")
print(associados.isna().sum())

print("\nProdutos:")
print(produtos.isna().sum())

print("\nMovimentacao:")
print(movimentacao.isna().sum())

print("\nLinhas duplicadas:")

print(f"Associados: {associados.duplicated().sum()}")
print(f"Produtos: {produtos.duplicated().sum()}")
print(f"Movimentacao: {movimentacao.duplicated().sum()}")

print("\nDuplicidade da CHAVE:")

print(f"Associados: {associados['CHAVE'].duplicated().sum()}")
print(f"Produtos: {produtos['CHAVE'].duplicated().sum()}")
print(f"Movimentacao: {movimentacao['CHAVE'].duplicated().sum()}")

print("\nA CHAVE é única?")

print(f"Associados: {associados['CHAVE'].is_unique}")
print(f"Produtos: {produtos['CHAVE'].is_unique}")
print(f"Movimentacao: {movimentacao['CHAVE'].is_unique}")

chaves_associados = set(associados["CHAVE"])
chaves_produtos = set(produtos["CHAVE"])
chaves_movimentacao = set(movimentacao["CHAVE"])

print("\nComparação das CHAVES entre as bases:")

print(
    f"Associados = Produtos: "
    f"{chaves_associados == chaves_produtos}")

print(
    f"Associados = Movimentacao: "
    f"{chaves_associados == chaves_movimentacao}")

print(
    f"Produtos = Movimentacao: "
    f"{chaves_produtos == chaves_movimentacao}")


print("\nCHAVES sem correspondência:")

print(
    "Associados sem Produtos:",
    len(chaves_associados - chaves_produtos))

print(
    "Produtos sem Associados:",
    len(chaves_produtos - chaves_associados))

print(
    "Associados sem Movimentacao:",
    len(chaves_associados - chaves_movimentacao))

print(
    "Movimentacao sem Associados:",
    len(chaves_movimentacao - chaves_associados))

# validação de campos categóricos
print("\nValores encontrados em CIDADE:")
print(associados["CIDADE"].value_counts(dropna=False))

print("\nValores encontrados em AGENCIA:")
print(associados["AGENCIA"].value_counts(dropna=False).sort_index())

colunas_produtos = [
    "CONTA_CORRENTE",
    "CARTAO",
    "CREDITO",
    "INVESTIMENTO",
    "CONSORCIO",
    "SEGURO",
]
print("\nValores encontrados nas colunas de produtos:")

for coluna in colunas_produtos:
    print(f"\n{coluna}:")
    print(produtos[coluna].value_counts(dropna=False))

sem_produtos = (produtos[colunas_produtos] == "N").all(axis=1)
print(
    "\nAssociados sem nenhum dos produtos ativos:",
    sem_produtos.sum(),
)

print("\nPeríodo das datas de associação:")
print(f"Data mínima: {associados['DATA_ASSOCIACAO'].min()}")
print(f"Data máxima: {associados['DATA_ASSOCIACAO'].max()}")

data_referencia = pd.Timestamp.today().normalize()
datas_futuras = associados[
    associados["DATA_ASSOCIACAO"] > data_referencia]

print(f"\nData de referência: {data_referencia.date()}")
print(f"Registros com data futura: {len(datas_futuras)}")

if not datas_futuras.empty:
    print(
        "Primeira data futura:",
        datas_futuras["DATA_ASSOCIACAO"].min(),
    )

    print(
        "Última data futura:",
        datas_futuras["DATA_ASSOCIACAO"].max(),
    )

# estatisticas descritivas
print("\nEstatísticas de RENDA_MENSAL:")
print(associados["RENDA_MENSAL"].describe())

print("\nEstatísticas de SALDO_MEDIO:")
print(movimentacao["SALDO_MEDIO"].describe())

print("\nEstatísticas de PIX_MENSAL:")
print(movimentacao["PIX_MENSAL"].describe())

print("\nEstatísticas de COMPRAS_CARTAO:")
print(movimentacao["COMPRAS_CARTAO"].describe())

# investigando os registros com renda ausente
associados_sem_renda = associados[
    associados["RENDA_MENSAL"].isna()
]

print("\nAssociados sem renda informada:")
print(
    associados_sem_renda[
        ["CHAVE", "AGENCIA", "CIDADE", "DATA_ASSOCIACAO"]
    ]
)

def contar_outliers_iqr(serie):
    q1 = serie.quantile(0.25)
    q3 = serie.quantile(0.75)

    iqr = q3 - q1

    limite_inferior = q1 - 1.5 * iqr
    limite_superior = q3 + 1.5 * iqr

    outliers = serie[
        (serie < limite_inferior)
        | (serie > limite_superior)
    ]

    return len(outliers)

print("\nPossíveis outliers pelo método IQR:")

print(
    "RENDA_MENSAL:",
    contar_outliers_iqr(associados["RENDA_MENSAL"].dropna()),)

print(
    "SALDO_MEDIO:",
    contar_outliers_iqr(movimentacao["SALDO_MEDIO"]),)

print(
    "PIX_MENSAL:",
    contar_outliers_iqr(movimentacao["PIX_MENSAL"]),)

print(
    "COMPRAS_CARTAO:",
    contar_outliers_iqr(movimentacao["COMPRAS_CARTAO"]),)