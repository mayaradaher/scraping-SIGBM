import time
import warnings

import pandas as pd
import requests as r
from bs4 import BeautifulSoup
from requests.exceptions import ConnectTimeout

from . import key_id

warnings.filterwarnings('ignore')


def scrap_id_info(id: str) -> dict:
    print(f'{id} Extraindo dados Estado de Conservação...')
    id_url = f'https://app.anm.gov.br/SIGBM/EstadoConservacaoPublico/BuscarPartial?idDeclaracao={id}'

    for attempt in range(5):  # Número máximo de tentativas
        try:
            page = r.get(id_url, timeout=12)  # Tempo limite
            page.raise_for_status()  # Verifica se a solicitação teve sucesso
            break  # Se bem-sucedido, saia do loop de tentativas
        except (ConnectTimeout, r.exceptions.RequestException):
            if attempt < 5 - 1:
                print(
                    f'Tentativa {attempt + 1} falhou. Tentando novamente após 5 segundos...'
                )
                time.sleep(5)  # Atraso entre as tentativas em segundos
            else:
                print(f'Atingiu o número máximo de tentativas para {id}.')
                return None  # Retorna None se as tentativas falharem

    soup = BeautifulSoup(page.content, 'html.parser')

    # Para as informações digitadas
    tag1 = soup.find_all('input', {'class': 'form-control'})
    id_dict1 = {tag.get('name'): tag.get('value') for tag in tag1}

    # Para as informações de escolha
    tag2 = soup.find_all(checked='checked')
    id_dict2 = {tag.get('name'): tag.get('value') for tag in tag2}

    dict = {**id_dict1, **id_dict2}

    dict['ID'] = id

    # Definir possíveis colunas com valores vazios
    missing_columns = [
        'ConfiabilidadeEstruturasEstravasoras',
        'Percolacao',
        'DeformacoesRecalques',
        'DeterioracaoTaludeParametro',
        'DrenagemSuperficial',
    ]
    for col in missing_columns:
        if col not in dict:
            dict[col] = ''

    return dict


# Obter as informações acima, agora para todas as barragens
id_page5 = [scrap_id_info(id) for id in key_id.ids]

# Limpeza dos dados
df_page5 = pd.DataFrame(id_page5)


# Função para substituir valores dos parâmetros
def replace_column_values(df, column_name, value_mapping):
    df[column_name] = df[column_name].replace(value_mapping)


# Dicionário para mapear os valores a serem substituídos
value_mappings = {
    'ConfiabilidadeEstruturasEstravasoras': {
        '1': '0 - Estruturas civis bem mantidas e em operação normal / barragem sem necessidade de estruturas extravasoras',
        '2': '3 - Estruturas com problemas identificados e medidas corretivas em implantação',
        '3': '6 - Estruturas com problemas identificados e sem implantação das medidas corretivas necessárias',
        '4': '10 - Estruturas com problemas identificados, com redução de capacidade vertente e sem medidas corretivas',
    },
    'Percolacao': {
        '1': '0 - Percolação totalmente controlada pelo sistema de drenagem',
        '2': '3 - Umidade ou surgência nas áreas de jusante, paramentos, taludes e ombreiras estáveis e monitorados',
        '3': '6 - Umidade ou surgência nas áreas de jusante, paramentos, taludes ou ombreiras sem implantação das medidas corretivas necessárias',
        '4': '10 - Surgência nas áreas de jusante com carreamento de material ou com vazão crescente ou infiltração do material contido, com potencial de comprometimento da segurança da estrutura',
    },
    'DeformacoesRecalques': {
        '1': '0 - Não existem deformações e recalques com potencial de comprometimento da segurança da estrutura',
        '2': '2 - Existência de trincas e abatimentos com medidas corretivas em implantação',
        '3': '6 - Existência de trincas e abatimentos sem implantação das medidas corretivas necessárias',
        '4': '10 - Existência de trincas, abatimentos ou escorregamentos, com potencial de comprometimento da segurança da estrutura',
    },
    'DeterioracaoTaludeParametro': {
        '1': '0 - Não existe deterioração de taludes e paramentos',
        '2': '2 - Falhas na proteção dos taludes e paramentos, presença de vegetação arbustiva',
        '3': '6 - Erosões superficiais, ferragem exposta, presença de vegetação arbórea, sem implantação das medidas corretivas necessárias',
        '4': '10 - Depressões acentuadas nos taludes, escorregamentos, sulcos profundos de erosão, com potencial de comprometimento da segurança da estrutura',
    },
    'DrenagemSuperficial': {
        '1': '0 - Drenagem superficial existente e operante',
        '2': '2 - Existência de trincas e/ou assoreamento e/ou abatimentos com medidas corretivas em implantação',
        '3': '4 - Existência de trincas e/ou assoreamento e/ou abatimentos sem medidas corretivas em implantação',
        '4': '5 - Drenagem superficial inexistente',
    },
}

# Aplicar mapeamento de valores para os parâmetros
for column_name, value_mapping in value_mappings.items():
    replace_column_values(df_page5, column_name, value_mapping)

# Juntar os ids ao dataframe
df_page5 = pd.merge(df_page5, key_id.df_state_id, how='inner', on='ID')

# Reordenar colunas e remover a coluna "ID"
df_page5 = df_page5[
    [
        'ID Barragem',
        'NomeBarragem',
        'ConfiabilidadeEstruturasEstravasoras',
        'Percolacao',
        'DeformacoesRecalques',
        'DeterioracaoTaludeParametro',
        'DrenagemSuperficial',
    ]
]

# Substituir NaN por em branco (tanto em branco, como NaN significam que não houve preenchimento)
df_page5 = df_page5.fillna('')
