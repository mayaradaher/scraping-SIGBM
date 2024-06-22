import time
import warnings

import pandas as pd
import requests as r
from bs4 import BeautifulSoup
from requests.exceptions import ConnectTimeout

from . import key_id

warnings.filterwarnings("ignore")


def scrap_id_info(id: str) -> dict:
    print(f"{id} Extraindo dados Plano de Segurança...")
    id_url = f"https://app.anm.gov.br/SIGBM/PlanoSegurancaPublico/BuscarPartial?idDeclaracao={id}"

    for attempt in range(6):  # Número máximo de tentativas
        try:
            page = r.get(id_url, timeout=12)  # Tempo limite
            page.raise_for_status()  # Verifica se a solicitação teve sucesso
            break  # Se bem-sucedido, saia do loop de tentativas
        except (ConnectTimeout, r.exceptions.RequestException):
            if attempt < 5 - 1:
                print(
                    f"Tentativa {attempt + 1} falhou. Tentando novamente após 5 segundos..."
                )
                time.sleep(5)  # Atraso entre as tentativas em segundos
            else:
                print(f"Atingiu o número máximo de tentativas para {id}.")
                return None  # Retorna None se as tentativas falharem

    soup = BeautifulSoup(page.content, "html.parser")

    # Para as informações de escolha
    tag1 = soup.find_all(checked="checked")
    id_dict1 = {tag.get("name"): tag.get("value") for tag in tag1}

    dict = {**id_dict1}

    dict["ID"] = id

    # Definir possíveis colunas com valores vazios
    missing_columns = [
        "DocumentacaoProjeto",
        "EstruturaOrgTecSegBarragem",
        "ManuaisProcSegMonitoramento",
        "PlanoAcaoEmergencial",
        "CopiaFisicaPAEBM",
        "RelMonitoramentoInspAnaliseSeg",
    ]
    for col in missing_columns:
        if col not in dict:
            dict[col] = ""

    return dict


# Obter as informações acima, agora para todas as barragens
id_page6 = [scrap_id_info(id) for id in key_id.ids]

# Limpeza dos dados
df_page6 = pd.DataFrame(id_page6)


# Função para substituir valores dos parâmetros
def replace_column_values(df, column_name, value_mapping):
    df[column_name] = df[column_name].replace(value_mapping)


# Dicionário para mapear os valores a serem substituídos
value_mappings = {
    "DocumentacaoProjeto": {
        "1": '0 - Projeto executivo e "como construído"',
        "2": '2 - Projeto executivo ou "como construído"',
        "3": '3 - Projeto "como está"',
        "4": "5 - Projeto básico",
        "5": "8 - Projeto conceitual",
        "6": "10 - Não há documentação de projeto",
    },
    "EstruturaOrgTecSegBarragem": {
        "1": "0 - Possui unidade administrativa com profissional técnico qualificado responsável pela segurança da barragem ou é barragem não enquadrada nos incisos I, II, III ou IV, parágrafo único do art. 1º da Lei nº 12.334/2010",
        "2": "1 - Possui profissional técnico qualificado (próprio ou contratado) responsável pela segurança da barragem",
        "3": "3 - Possui unidade administrativa sem profissional técnico qualificado responsável pela segurança da barragem",
        "4": "6 - Não possui unidade administrativa e responsável técnico qualificado pela segurança da barragem",
    },
    "ManuaisProcSegMonitoramento": {
        "1": "0 - Possui manuais de procedimentos para inspeção, monitoramento e operação ou é barragem não enquadrada nos incisos I, II, III ou IV, parágrafo único do art. 1º da Lei nº 12.334/2010",
        "2": "2 - Possui apenas manual de procedimentos de monitoramento",
        "3": "4 - Possui apenas manual de procedimentos de inspeção",
        "4": "8 - Não possui manuais ou procedimentos formais para monitoramento e inspeções",
    },
    "PlanoAcaoEmergencial": {
        "1": "0 - Possui PAE",
        "2": "2 - Não possui PAE (não é exigido pelo órgão fiscalizador)",
        "3": "4 - PAE em elaboração",
        "4": "8 - Não possui PAE (quando for exigido pelo órgão fiscalizador)",
    },
    "RelMonitoramentoInspAnaliseSeg": {
        "1": "0 - Emite regularmente relatórios de inspeção e monitoramento com base na instrumentação e de Análise de Segurança ou é barragem não enquadrada nos incisos I, II, III ou IV, parágrafo único do art. 1º da Lei nº 12.334/201",
        "2": "2 - Emite regularmente APENAS relatórios de Análise de Segurança",
        "3": "4 - Emite regularmente APENAS relatórios de inspeção e monitoramento",
        "4": "6 - Emite regularmente APENAS relatórios de inspeção visual",
        "5": "8 - Não emite regularmente relatórios de inspeção e monitoramento e de Análise de Segurança",
    },
}

# Aplicar mapeamento de valores para os parâmetros
for column_name, value_mapping in value_mappings.items():
    replace_column_values(df_page6, column_name, value_mapping)

# Substituir NaN por em branco (tanto em branco, como NaN significam que não houve preenchimento)
df_page6 = df_page6.fillna("")

# Juntar os ids ao dataframe
df_page6 = pd.merge(df_page6, key_id.df_state_id, how="inner", on="ID")

# Reordenar colunas e remover a coluna "ID"
df_page6 = df_page6[
    [
        "ID Barragem",
        "NomeBarragem",
        "DocumentacaoProjeto",
        "EstruturaOrgTecSegBarragem",
        "ManuaisProcSegMonitoramento",
        "PlanoAcaoEmergencial",
        "CopiaFisicaPAEBM",
        "RelMonitoramentoInspAnaliseSeg",
    ]
]

# Substituir True/False para Sim/Não
df_page6 = df_page6.replace(["true", "false"], ["Sim", "Não"])
