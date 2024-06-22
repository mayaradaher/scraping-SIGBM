import time
import warnings

import pandas as pd
import requests as r
from bs4 import BeautifulSoup
from requests.exceptions import ConnectTimeout

from . import key_id

warnings.filterwarnings("ignore")


def scrap_id_info(id: str) -> dict:
    print(f"{id} Extraindo dados Características Técnicas...")
    id_url = f"https://app.anm.gov.br/SIGBM/CaracteristicaTecnicaPublico/BuscarPartial?idDeclaracao={id}"

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

    # Para as informações digitadas
    tag1 = soup.find_all("input", {"class": "form-control"})
    id_dict1 = {tag.get("name"): tag.get("value") for tag in tag1}

    # Para as informações de escolha
    tag2 = soup.find_all(checked="checked")
    id_dict2 = {tag.get("name"): tag.get("value") for tag in tag2}

    dict = {**id_dict1, **id_dict2}

    dict["ID"] = id

    # Definir possíveis colunas com valores vazios
    missing_columns = [
        "AlturaMaximaProjetos",
        "AlturaMaximaAtual",
        "ComprimentoCristaProjeto",
        "ComprimentoAtualCrista",
        "DescargaMaximaVertedouro",
        "AreaReservatorio",
        "BarragemMaterialConstrucao",
        "TipoFundacao",
        "Fundacao",
        "VazaoProjeto",
        "DrenagemInterna",
        "ControleCompactacao",
        "InclinacaoMediaTaludesSecaoPrincipal",
        "MetodoConstrutivoBarragem",
        "TipoAlteamento",
        "TipoAuscultacao",
        "PossuiMantaImpermeabilizante",
    ]
    for col in missing_columns:
        if col not in dict:
            dict[col] = ""

    return dict


# Obter as informações acima, agora para todas as barragens
id_page4 = [scrap_id_info(id) for id in key_id.ids]

# Limpeza dos dados
df_page4 = pd.DataFrame(id_page4)


# Função para substituir valores dos parâmetros
def replace_column_values(df, column_name, value_mapping):
    df[column_name] = df[column_name].replace(value_mapping)


# Dicionário para mapear os valores a serem substituídos
value_mappings = {
    "BarragemMaterialConstrucao": {
        "1": "Concreto",
        "2": "Rejeito",
        "3": "Terra Homogênea",
        "4": "Terra / Enrocamento",
        "5": "Enrocamento",
    },
    "TipoFundacao": {
        "1": "Rocha sã",
        "2": "Rocha alterada / Saprolito",
        "3": "Solo residual / Aluvião",
        "4": "Aluvião arenoso espesso / Solo orgânico / Rejeito / Desconhecido",
    },
    "Fundacao": {
        "1": "0 - Fundação investigada conforme projeto",
        "2": "6 - Fundação parcialmente investigada",
        "3": "10 - Fundação desconhecida/ Estudo não confiável",
    },
    "VazaoProjeto": {
        "1": "0 - CMP (Cheia Máxima Provável) ou Decamilenar",
        "2": "2 - Milenar",
        "3": "5 - TR = 500 anos",
        "4": "10 - TR inferior a 500 anos ou Desconhecida/ Estudo não confiável",
    },
    "MetodoConstrutivoBarragem": {
        "1": "0 - Etapa única",
        "2": "2 - Alteamento a jusante",
        "3": "5 - Alteamento por linha de centro",
        "4": "10 - Alteamento a montante ou desconhecido",
    },
    "TipoAlteamento": {
        "1": "Etapa única",
        "2": "Contínuo",
    },
    "TipoAuscultacao": {
        "1": "0 - Existe instrumentação de acordo com o projeto técnico",
        "2": "2 - Existe instrumentação em desacordo com o projeto, porém em processo de instalação de instrumentos para adequação ao projeto",
        "3": "6 - Existe instrumentação em desacordo com o projeto sem processo de instalação de instrumentos para adequação ao projeto",
        "4": "8 - Barragem não instrumentada em desacordo com o projeto",
    },
    "DrenagemInterna": {
        "1": "0 - Existem documentos que comprovam o controle de compactação conforme projeto e que comprovam o acompanhamento e controle tecnológico durante a execução",
        "2": "4 - Existem estudos geotécnicos que comprovam o grau de compactação de acordo com projeto",
        "3": "10 - Não houve controle tecnológico e/ou não há informação e/ou compactação em desacordo com projeto",
    },
    "ControleCompactacao": {
        "1": "0 - Drenagem construída conforme projeto ou não existe drenagem em projeto",
        "2": "4 - Drenagem corretiva construída posteriormente a conclusão da barragem",
        "3": "10 - Sistema de drenagem em desacordo com projeto ou inexistente ou desconhecida ou estudo não confiável ou inoperante",
    },
    "InclinacaoMediaTaludesSecaoPrincipal": {
        "1": "0 - Suave (Inclinação média dos taludes na seção principal <= 1V:3H) Ou Barragem de Concreto",
        "2": "3 - Intermediário (1V:2H >= Inclinação média dos taludes na seção principal > 1V:3H)",
        "3": "6 - Ingrime (Inclinação média dos taludes na seção principal > 1V:2H)",
    },
}

# Aplicar mapeamento de valores para os parâmetros
for column_name, value_mapping in value_mappings.items():
    replace_column_values(df_page4, column_name, value_mapping)


# Trocar a vírgula por ponto, depois converter para numérico e inserir duas casas decimais
numeric_columns = [
    "AlturaMaximaProjetos",
    "AlturaMaximaAtual",
    "ComprimentoCristaProjeto",
    "ComprimentoAtualCrista",
    "DescargaMaximaVertedouro",
    "AreaReservatorio",
]


def format_numeric(df, column_names):
    for column_name in column_names:
        df[column_name] = df[column_name].apply(lambda x: str(x).replace(",", "."))
        df[column_name] = pd.to_numeric(df[column_name], errors="ignore").map(
            "{:,.2f}".format
        )


format_numeric(df_page4, numeric_columns)

# Juntar os ids ao dataframe
df_page4 = pd.merge(df_page4, key_id.df_state_id, how="inner", on="ID")

# Reordenar colunas e remover a coluna "ID"
df_page4 = df_page4[
    [
        "ID Barragem",
        "NomeBarragem",
        "AlturaMaximaProjetos",
        "AlturaMaximaAtual",
        "ComprimentoCristaProjeto",
        "ComprimentoAtualCrista",
        "DescargaMaximaVertedouro",
        "AreaReservatorio",
        "BarragemMaterialConstrucao",
        "TipoFundacao",
        "Fundacao",
        "VazaoProjeto",
        "DrenagemInterna",
        "ControleCompactacao",
        "InclinacaoMediaTaludesSecaoPrincipal",
        "MetodoConstrutivoBarragem",
        "TipoAlteamento",
        "TipoAuscultacao",
        "PossuiMantaImpermeabilizante",
    ]
]

# Substituir True/False para Sim/Não
df_page4 = df_page4.replace(["True", "False"], ["Sim", "Não"])

# Substituir NaN por em branco (tanto em branco, como NaN significam que não houve preenchimento)
df_page4 = df_page4.fillna("")

# Renomear colunas
df_page4.rename(
    columns={
        "AlturaMaximaProjetos": "AlturaMaximaProjetos_m",
        "AlturaMaximaAtual": "AlturaMaximaAtual_m",
        "ComprimentoCristaProjeto": "ComprimentoCristaProjeto_m",
        "ComprimentoAtualCrista": "ComprimentoAtualCrista_m",
        "DescargaMaximaVertedouro": "DescargaMaximaVertedouro_m3_seg",
        "AreaReservatorio": "AreaReservatorio_m2",
    },
    inplace=True,
)
