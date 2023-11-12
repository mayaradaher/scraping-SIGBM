import re
import time
import warnings
from collections import Counter

import pandas as pd
import requests as r
from bs4 import BeautifulSoup
from requests.exceptions import ConnectTimeout

from . import key_id

warnings.filterwarnings('ignore')


def scrap_key_info(key: str) -> dict:
    print(f'{key} Extraindo dados Disposição de Rejeitos com Barramento...')
    key_url = f'https://app.anm.gov.br/SIGBM/BarragemPublico/Detalhar/{key}'

    for attempt in range(5):  # Número máximo de tentativas
        try:
            page = r.get(
                key_url, timeout=10
            )  # Aumentar o tempo limite, se necessário
            page.raise_for_status()  # Verifica se a solicitação teve sucesso
            break  # Se bem-sucedido, saia do loop de tentativas
        except (ConnectTimeout, r.exceptions.RequestException):
            if attempt < 5 - 1:
                print(
                    f'Tentativa {attempt + 1} falhou. Tentando novamente após 5 segundos...'
                )
                time.sleep(5)  # Atraso entre as tentativas em segundos
            else:
                print(f'Attingiu o número máximo de tentativas para {key}.')
                return None  # Retorna None se as tentativas falharem

    soup = BeautifulSoup(page.content, 'html.parser')

    # Para as informações digitadas
    tag1 = soup.find_all('input', {'class': 'form-control'})
    key_dict1 = {tag.get('name'): tag.get('value') for tag in tag1}

    # Para as informações de escolha
    tag2 = soup.find_all(checked='checked')
    key_dict2 = {tag.get('name'): tag.get('value') for tag in tag2}

    # Para as informações de lista
    tag3 = soup.find(selected='selected')
    key_dict3 = {('Estado'): tag.get_text('value') for tag in tag3}

    # Para as informações de lista, mas o valor da lista
    tag4 = soup.find_all(selected='selected')
    key_dict4 = {('Municipio'): tag.get_text('value') for tag in tag4}

    # Regex para capturar o parâmetro "NomeUsina" em Javascript
    tag5 = soup.find_all('script', {'type': 'text/javascript'})[2].text
    name_pattern = re.compile(r'(?<=NomeUsina":")(.*?)",', flags=re.M)
    tag5 = name_pattern.findall(tag5)
    key_dict5 = {('NomeUsina'): tag5 for tag in tag5}

    dict = {**key_dict1, **key_dict2, **key_dict3, **key_dict4, **key_dict5}

    dict['Chave'] = key

    # Definir possíveis colunas com valores vazios
    missing_columns = [
        'Estado',
        'Municipio',
        'BackUpDamOperandoPosRompimento',
        'SituacaoNivelEmergencialIndeterminadaInicioConstrucao',
        'NomeUsina',
    ]

    for col in missing_columns:
        if col not in dict:
            dict[col] = ''

    return dict


# Obter as informações acima, agora para todas as barragens
key_page1 = [scrap_key_info(key) for key in key_id.keys]

# Limpeza dos dados
df_page1 = pd.DataFrame(key_page1)

# Verificar se o parâmetro "NomeUsina" existe na página
if 'NomeUsina' in df_page1.columns:
    # Remover caracteres extraídos em javascript (parâmetro "NomeUsina")
    df_page1['NomeUsina'] = df_page1['NomeUsina'].apply(
        lambda x: re.sub(r'u0027', '', re.sub(r'[,\[\]()\\]', '', str(x)))
    )


# Remover blocos duplicados que vieram do javascript (parâmetro "NomeUsina")
def remove_repeated_blocks(text):
    blocks = text.split("'")
    block_counts = Counter(blocks)
    result_blocks = []

    for block in blocks:
        if block_counts[block] == 1:
            result_blocks.append(block)
        elif block not in result_blocks:
            result_blocks.append(block)

    return "'".join(result_blocks)


df_page1['NomeUsina'] = df_page1['NomeUsina'].apply(remove_repeated_blocks)


# Remover prefixos desnecessários
df_page1.columns = df_page1.columns.str.replace(
    r'DisposicaoRejeitosBarramento.', ''
)


# Função para substituir valores dos parâmetros
def replace_column_values(df, column_name, value_mapping):
    df[column_name] = df[column_name].replace(value_mapping)


# Dicionário para mapear os valores a serem substituídos
value_mappings = {
    'TipoBarragemMineracao': {
        '1': 'Barragem/Barramento/Dique',
        '2': 'Cava com Barramento Construído',
        '3': 'Empilhamento drenado construído hidraulicamente e suscetível à liquefação',
    },
    'SituacaoOperacional': {
        '1': 'Em Construção',
        '2': 'Ativa',
        '3': 'Inativa',
        '4': 'Em descaracterização (projeto/obras/monitoramento)',
    },
    'EstruturaObjetivoContencao': {
        '1': 'Rejeitos',
        '2': 'Sedimentos',
    },
}

# Aplicar mapeamento de valores para os parâmetros
for column_name, value_mapping in value_mappings.items():
    replace_column_values(df_page1, column_name, value_mapping)

# Converter para formato numérico
numeric_columns = [
    'QuantidadeDiqueInterno',
    'QuantidadeDiqueSelante',
]
df_page1[numeric_columns] = df_page1[numeric_columns].apply(
    pd.to_numeric, errors='coerce'
)

# Substituir true por Indeterminada
df_page1['SituacaoNivelEmergencialIndeterminadaInicioConstrucao'] = df_page1[
    'SituacaoNivelEmergencialIndeterminadaInicioConstrucao'
].replace(['true'], ['Indeterminada'])

# Substituir True/False para Sim/Não
df_page1 = df_page1.replace({'True': 'Sim', 'False': 'Não'})

# Juntar os ids ao dataframe
df_page1 = pd.merge(df_page1, key_id.df_state_key, how='inner', on='Chave')

# Reordenar colunas e remover a coluna "Chave"
df_page1 = df_page1[
    [
        'ID Barragem',
        'NomeBarragem',
        'Estado',
        'Municipio',
        'TipoBarragemMineracao',
        'BarragemInternaSelante',
        'QuantidadeDiqueInterno',
        'QuantidadeDiqueSelante',
        'BarragemPossuiBackUpDam',
        'BackUpDamOperandoPosRompimento',
        'SituacaoOperacional',
        'DataInicioConstrucao',
        'SituacaoNivelEmergencialIndeterminadaInicioConstrucao',
        'DataInicioOperacao',
        'DataInicioDescaracterizacao',
        'EstruturaObjetivoContencao',
        'BaragemDentroAreaProcesso',
        'AlimentoUsina',
        'NomeUsina',
        'DataDesativacao',
    ]
]

# Substituir "nan" por ""
df_page1 = df_page1.replace({'nan': ''})
