import warnings

import pandas as pd
import requests as r
from bs4 import BeautifulSoup

from . import key_id

warnings.filterwarnings('ignore')


# Dados extraídos somente para barragens que possuem Back up dam
def scrap_id_info(id: str) -> dict:
    print(f'{id} Extraindo dados ECJ...')
    id_url = f'https://app.anm.gov.br/SIGBM/BackUpDamPublico/BuscarPartial?idDeclaracao={id}'

    page = r.get(id_url)

    soup = BeautifulSoup(page.content, 'html.parser')

    # Para as informações digitadas
    tag1 = soup.find_all('input', {'class': 'form-control'})
    id_dict = {tag.get('name'): tag.get('value') for tag in tag1}

    # Para as informações de escolha
    tag2 = soup.find_all(checked='checked')
    id_dict2 = {tag.get('name'): tag.get('value') for tag in tag2}

    # Para as informações digitadas
    tag3 = soup.find_all(
        'div', {'class': 'btn btn-default btn-sm margin-right-10'}
    )
    id_dict3 = {
        ('ProcessosAssociados'): tag.get_text('value').strip() for tag in tag3
    }

    dict = {**id_dict, **id_dict2, **id_dict3}

    dict['ID'] = id

    # Definir possíveis colunas com valores vazios
    missing_columns = [
        'Nome',
        'NomeEstado',
        'NomeMunicipio',
        'SituacaoOperacional',
        'DataInicioSituacaoOperacional',
        'VidaUtilPrevista',
        'DentroAreaProcesso',
        'ProcessosAssociados',
        'CoordenadaSirga',
        'Latitude',
        'Longitude',
        'AlturaMaximaProjeto',
        'ComprimentoCristaProjeto',
        'VolumeProjetoReservatorio',
        'DescargaMaximaVertedouro',
        'ExisteDocumentoAtesteSeguranca',
        'ExisteManualOperacao',
        'PassouAuditoriaTerceiro',
        'GaranteReducaoAreaManchaInundacaoJusante',
        'MateriaisConstrucao',
        'TipoFundacao',
        'VazaoProjeto',
        'MetodoConstrutivo',
        'TipoAuscultacao',
    ]
    for col in missing_columns:
        if col not in dict:
            dict[col] = None

    return dict


# Obter as informações acima, agora para todas as barragens
id_page1_1 = [scrap_id_info(id) for id in key_id.ids]

# Limpeza dos dados
df_page1_1 = pd.DataFrame(id_page1_1)

# Quando as linhas da coluna "ElaboracaoProjeto" estiver vazia, remova
df_page1_1 = df_page1_1[df_page1_1['Nome'].notna()]


# Função para substituir valores dos parâmetros
def replace_column_values(df, column_name, value_mapping):
    df[column_name] = df[column_name].replace(value_mapping)


# Dicionário para mapear os valores a serem substituídos
value_mappings = {
    'SituacaoOperacional': {'1': 'Em Construção', '2': 'Concluída'},
    'CoordenadaSirga': {'1': 'Norte do Equador', '2': 'Sul do Equador'},
    'MateriaisConstrucao': {
        '1': 'Concreto',
        '2': 'Rejeito',
        '3': 'Terra Homogênea',
        '4': 'Terra / Enrocamento',
        '5': 'Enrocamento',
    },
    'TipoFundacao': {
        '1': 'Rocha sã',
        '2': 'Rocha alterada / Saprolito',
        '3': 'Solo residual / Aluvião',
        '4': 'Aluvião arenoso espesso / Solo orgânico / Rejeito / Desconhecido',
    },
    'VazaoProjeto': {
        '1': '0 - CMP (Cheia Máxima Provável) ou Decamilenar',
        '2': '2 - Milenar',
        '3': '5 - TR = 500 anos',
        '4': '10 - TR inferior a 500 anos ou Desconhecida/ Estudo não confiável',
    },
    'MetodoConstrutivo': {
        '1': '0 - Etapa única',
        '2': '2 - Alteamento a jusante',
        '3': '5 - Alteamento por linha de centro',
    },
    'TipoAuscultacao': {
        '1': '0 - Existe instrumentação de acordo com o projeto técnico',
        '2': '2 - Existe instrumentação em desacordo com o projeto, porém em processo de instalação de instrumentos para adequação ao projeto',
        '3': '6 - Existe instrumentação em desacordo com o projeto sem processo de instalação de instrumentos para adequação ao projeto',
        '4': '8 - Barragem não instrumentada em desacordo com o projeto',
    },
}

# Aplicar mapeamento de valores para os parâmetros
for column_name, value_mapping in value_mappings.items():
    replace_column_values(df_page1_1, column_name, value_mapping)

# Converter para formato data
date_columns = [
    'DataInicioSituacaoOperacional',
]
for column in date_columns:
    df_page1_1[column] = pd.to_datetime(
        df_page1_1[column], errors='coerce'
    ).dt.strftime('%d/%m/%Y')


# Trocar a vírgula por ponto e depois converter para numérico (quando aplicável, inserir duas casas decimais)
numeric_columns = [
    'VidaUtilPrevista',
    'AlturaMaximaProjeto',
    'ComprimentoCristaProjeto',
    'VolumeProjetoReservatorio',
    'DescargaMaximaVertedouro',
]


def format_numeric(df, column_names):
    for column_name in column_names:
        df[column_name] = df[column_name].apply(
            lambda x: str(x).replace(',', '.')
        )
        df[column_name] = pd.to_numeric(df[column_name], errors='ignore').map(
            '{:,.2f}'.format
        )


format_numeric(df_page1_1, numeric_columns)


# Formatar as coordenadas
def format_coordinates(coord):
    degrees = int(coord[:2])
    minutes = int(coord[2:4])
    seconds = int(coord[4:6])
    fraction = int(coord[6:])

    dd = degrees + minutes / 60 + seconds / 3600 + fraction / 360000
    return round(-dd, 6)


df_page1_1['Latitude'] = df_page1_1['Latitude'].apply(format_coordinates)
df_page1_1['Longitude'] = df_page1_1['Longitude'].apply(format_coordinates)

# Juntar os ids ao dataframe
df_page1_1 = pd.merge(df_page1_1, key_id.df_state_id, how='inner', on='ID')

# Reordenar colunas e remover a coluna "ID"
df_page1_1 = df_page1_1[
    [
        'ID Barragem',
        'NomeBarragem',
        'Nome',
        'NomeEstado',
        'NomeMunicipio',
        'SituacaoOperacional',
        'DataInicioSituacaoOperacional',
        'VidaUtilPrevista',
        'DentroAreaProcesso',
        'ProcessosAssociados',
        'CoordenadaSirga',
        'Latitude',
        'Longitude',
        'AlturaMaximaProjeto',
        'ComprimentoCristaProjeto',
        'VolumeProjetoReservatorio',
        'DescargaMaximaVertedouro',
        'ExisteDocumentoAtesteSeguranca',
        'ExisteManualOperacao',
        'PassouAuditoriaTerceiro',
        'GaranteReducaoAreaManchaInundacaoJusante',
        'MateriaisConstrucao',
        'TipoFundacao',
        'VazaoProjeto',
        'MetodoConstrutivo',
        'TipoAuscultacao',
    ]
]

# Substituir True/False para Sim/Não
df_page1_1 = df_page1_1.replace(['True', 'False'], ['Sim', 'Não'])

# Renomear colunas
df_page1_1.rename(
    columns={
        'VidaUtilPrevista': 'VidaUtilPrevista_anos',
        'AlturaMaximaProjeto': 'AlturaMaximaProjeto_m',
        'ComprimentoCristaProjeto': 'ComprimentoCristaProjeto_m',
        'VolumeProjetoReservatorio': 'VolumeProjetoReservatorio_m3',
        'DescargaMaximaVertedouro': 'DescargaMaximaVertedouro_m3_seg',
    },
    inplace=True,
)
