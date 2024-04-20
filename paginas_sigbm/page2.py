import time
import warnings

import pandas as pd
import requests as r
from bs4 import BeautifulSoup
from requests.exceptions import ConnectTimeout

from . import key_id

warnings.filterwarnings('ignore')


def scrap_id_info(id: str) -> dict:
    print(f'{id} Extraindo dados Coordenadas do Centro da Crista...')
    id_url = f'https://app.anm.gov.br/SIGBM/CentroCristaPublico/BuscarPartial?idDeclaracao={id}'

    for attempt in range(6):  # Número máximo de tentativas
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
    id_dict = {tag.get('name'): tag.get('value') for tag in tag1}

    # Para as informações de escolha
    tag2 = soup.find_all(checked='checked')
    id_dict2 = {tag.get('name'): tag.get('value') for tag in tag2}

    dict = {**id_dict, **id_dict2}

    dict['ID'] = id

    return dict


# Obter as informações acima, agora para todas as barragens
id_page2 = [scrap_id_info(id) for id in key_id.ids]

# Limpeza dos dados
df_page2 = pd.DataFrame(id_page2)

# Mapear valores numéricos para textos
coordenadas_mapping = {
    '1': 'Norte do Equador',
    '2': 'Sul do Equador',
}
df_page2['CoordenadasInformadasSirga'] = df_page2[
    'CoordenadasInformadasSirga'
].map(coordenadas_mapping)


# Formatar as coordenadas
def format_coordinates(coord):
    degrees = int(coord[:2])
    minutes = int(coord[2:4])
    seconds = int(coord[4:6])
    fraction = int(coord[6:])

    dd = degrees + minutes / 60 + seconds / 3600 + fraction / 360000
    return round(-dd, 6)


df_page2['Latitude'] = df_page2['Latitude'].apply(format_coordinates)
df_page2['Longitude'] = df_page2['Longitude'].apply(format_coordinates)

# Juntar os ids ao dataframe
df_page2 = pd.merge(df_page2, key_id.df_state_id, how='inner', on='ID')

# Reordenar colunas e remover a coluna "ID"
df_page2 = df_page2[
    [
        'ID Barragem',
        'NomeBarragem',
        'CoordenadasInformadasSirga',
        'Latitude',
        'Longitude',
    ]
]
