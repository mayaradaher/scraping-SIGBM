import warnings

import pandas as pd
import requests as r
from bs4 import BeautifulSoup

from . import key_id

warnings.filterwarnings("ignore")


# Dados extraídos somente para barragens em Descaracterização
def scrap_id_info(id: str) -> dict:
    print(f"{id} Extraindo dados Descaracterização...")
    id_url = f"https://app.anm.gov.br/SIGBM/DescaracterizacaoPublico/BuscarPartial?idDeclaracao={id}"

    page = r.get(id_url)

    soup = BeautifulSoup(page.content, "html.parser")

    # Para as informações digitadas
    tag1 = soup.find_all("input", {"class": "form-control"})
    id_dict = {tag.get("name"): tag.get("value") for tag in tag1}

    # Para as informações de escolha
    tag2 = soup.find_all(checked="checked")
    id_dict2 = {tag.get("name"): tag.get("value") for tag in tag2}

    tag3 = soup.find_all("textarea", {"id": "textoEstruturaRemanescente"})
    id_dict3 = {"EstruturaRemanescente": tag.get_text(strip=True) for tag in tag3}

    dict = {**id_dict, **id_dict2, **id_dict3}

    dict["ID"] = id

    # Definir possíveis colunas com valores vazios
    missing_columns = [
        "FaseAtualProjeto",
        "ElaboracaoProjeto",
        "DataDeEmissaoProjetoBasico",
        "DataEstimadaEmissaoProjeto",
        "DataDeEmissaoProjetoExecutivo",
        "SolucaoDescaracterizacao",
        "EstruturaRemanescente",
        "EstabilizacaoOuDescaracterizacao",
        "DataInicioEstabilizacaoOuDescaracterizacao",
        "DuracaoEstimadaEmMeses",
        "DataConlusaoEstabilizacaoOuDescaracterizacao",
        "MonitoramentoAtivo",
        "DataInicioMonitoramentoAtivo",
        "DuracaoMonitoramentoAtivoEmMeses",
        "DataEstimadaEmissaoProjeto",
        "DataInicioMonitoramentoPassivo",
        "DataConclusaoMonitoramentoPassivo",
    ]

    for col in missing_columns:
        if col not in dict:
            dict[col] = ""

    return dict


# Obter as informações acima, agora para todas as barragens
id_page1_2 = [scrap_id_info(id) for id in key_id.ids]

# Limpeza dos dados
df_page1_2 = pd.DataFrame(id_page1_2)


# Função para substituir valores dos parâmetros
def replace_column_values(df, column_name, value_mapping):
    df[column_name] = df[column_name].replace(value_mapping)


# Dicionário para mapear os valores a serem substituídos
value_mappings = {
    "ElaboracaoProjeto": {
        "1": "Conceitual",
        "2": "Básico",
        "3": "Executivo",
        "4": "Sem informação de projeto",
    },
    "SolucaoDescaracterizacao": {
        "1": "Remoção total dos rejeitos",
        "2": "Estrutura remanescente",
    },
}

# Aplicar mapeamento de valores para os parâmetros
for column_name, value_mapping in value_mappings.items():
    replace_column_values(df_page1_2, column_name, value_mapping)

# Converter para formato data
date_columns = [
    "DataEstimadaEmissaoProjeto",
    "DataDeEmissaoProjetoBasico",
    "DataDeEmissaoProjetoExecutivo",
    "DataInicioMonitoramentoAtivo",
    "DataInicioMonitoramentoPassivo",
    "DataConclusaoMonitoramentoPassivo",
    "DataInicioEstabilizacaoOuDescaracterizacao",
    "DataConlusaoEstabilizacaoOuDescaracterizacao",
]
for column in date_columns:
    df_page1_2[column] = pd.to_datetime(
        df_page1_2[column], errors="coerce"
    ).dt.strftime("%d/%m/%Y")

# Converter para formato numérico
numeric_columns = [
    "DuracaoMonitoramentoAtivoEmMeses",
    "DuracaoEstimadaEmMeses",
]
df_page1_2[numeric_columns] = df_page1_2[numeric_columns].apply(
    pd.to_numeric, errors="coerce"
)

# Substituir true pela correspondência
df_page1_2["FaseAtualProjeto"] = df_page1_2["FaseAtualProjeto"].replace(
    ["true"], ["Fase Atual do projeto"]
)

df_page1_2["EstabilizacaoOuDescaracterizacao"] = df_page1_2[
    "EstabilizacaoOuDescaracterizacao"
].replace(["true"], ["Fase de obras de estabilização ou descaracterização"])

df_page1_2["MonitoramentoAtivo"] = df_page1_2["MonitoramentoAtivo"].replace(
    ["true"], ["Em monitoramento ativo"]
)

# Juntar os ids ao dataframe
df_page1_2 = pd.merge(df_page1_2, key_id.df_state_id, how="inner", on="ID")

# Quando a coluna "FaseAtualProjeto" estiver vazia, remover todas as linhas
df_page1_2 = df_page1_2[df_page1_2["FaseAtualProjeto"].notna()]

# Quando as linhas da coluna "ElaboracaoProjeto" estiver vazia, remova
df_page1_2 = df_page1_2[df_page1_2["ElaboracaoProjeto"] != ""]

# Reordenar colunas e remover a coluna "ID"
df_page1_2 = df_page1_2[
    [
        "ID Barragem",
        "NomeBarragem",
        "FaseAtualProjeto",
        "ElaboracaoProjeto",
        "DataDeEmissaoProjetoBasico",
        "DataEstimadaEmissaoProjeto",
        "DataDeEmissaoProjetoExecutivo",
        "SolucaoDescaracterizacao",
        "EstruturaRemanescente",
        "EstabilizacaoOuDescaracterizacao",
        "DataInicioEstabilizacaoOuDescaracterizacao",
        "DuracaoEstimadaEmMeses",
        "DataConlusaoEstabilizacaoOuDescaracterizacao",
        "MonitoramentoAtivo",
        "DataInicioMonitoramentoAtivo",
        "DuracaoMonitoramentoAtivoEmMeses",
        "DataEstimadaEmissaoProjeto",
        "DataInicioMonitoramentoPassivo",
        "DataConclusaoMonitoramentoPassivo",
    ]
]
