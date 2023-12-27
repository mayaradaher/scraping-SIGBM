import time
import warnings

import pandas as pd
import requests as r
from bs4 import BeautifulSoup
from requests.exceptions import ConnectTimeout

from . import key_id

warnings.filterwarnings('ignore')


def scrap_id_info(id: str) -> dict:
    print(f'{id} Extraindo dados Dano Potencial Associado...')
    id_url = f'https://app.anm.gov.br/SIGBM/DanoPotencialPublico/BuscarPartial?idDeclaracao={id}'

    for attempt in range(5):  # Número máximo de tentativas
        try:
            page = r.get(
                id_url, timeout=10
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
        'VolumeProjetoReservatorio',
        'VolumeAtualReservatorio',
        'CapacidadeTotalReservatorio' 'ExistenciaPopulacaoJusante',
        'NumeroPessoasAfetadasCasoRompimento',
        'ImpactoAmbiental',
        'ImpactoSocioEconomico',
    ]
    for col in missing_columns:
        if col not in dict:
            dict[col] = ''

    return dict


# Obter as informações acima, agora para todas as barragens
id_page7 = [scrap_id_info(id) for id in key_id.ids]

# Limpeza dos dados
df_page7 = pd.DataFrame(id_page7)


# Função para substituir valores dos parâmetros
def replace_column_values(df, column_name, value_mapping):
    df[column_name] = df[column_name].replace(value_mapping)


# Dicionário para mapear os valores a serem substituídos
value_mappings_page7 = {
    'ExistenciaPopulacaoJusante': {
        '1': '0 - Inexistente (Não existem pessoas permanentes/residentes ou temporárias/transitando na área afetada a jusante da barragem)',
        '2': '3 - Pouco Frequente (Não existem pessoas ocupando permanentemente a área afetada a jusante da barragem, mas existe estrada vicinal de uso local)',
        '3': '5 - Frequente (Não existem pessoas ocupando permanentemente a área afetada a jusante da barragem, mas existe rodovia municipal ou estadual ou federal ou outro local e/ou empreendimento de permanência eventual de pessoas que poderão ser atingidas)',
        '4': '10 - Existente (Existem pessoas ocupando permanentemente a área afetada a jusante da barragem, portanto, vidas humanas poderão ser atingidas)',
    },
    'NumeroPessoasAfetadasCasoRompimento': {
        '1': '1-100',
        '2': '101-500',
        '3': '501-1000',
        '4': '1001-5000',
        '5': 'acima de 5001',
    },
    'ImpactoAmbiental': {
        '1': '0 - Insignificante (Área afetada a jusante da barragem encontra-se totalmente descaracterizada de suas condições naturais e a estrutura armazena apenas resíduos Classe II B - Inertes, segundo a NBR 10004/2004 da ABNT)',
        '2': '2 - Pouco Significativo (Área afetada a jusante da barragem não apresenta área de interesse ambiental relevante ou áreas protegidas em legislação específica (excluídas APPs) e armazena apenas resíduos Classe II B - Inertes, segundo a NBR 10004/2004 da ABNT)',
        '3': '6 - Significativo (Área afetada a jusante da barragem apresenta área de interesse ambiental relevante ou áreas protegidas em legislação específica (excluídas APPs)) e armazena apenas resíduos Classe II B - Inertes, segundo a NBR 10004/2004 da ABNT)',
        '4': '8 - Muito Significativo (Barragem armazena rejeitos ou resíduos sólidos classificados na Classe II A - Não Inertes, segundo a NBR 10004/2004)',
        '5': '10 - Muito Significativo Agravado (Barragem armazena rejeitos ou resíduos sólidos classificados na Classe I - Perigosos segundo a NBR 10004/2004)',
    },
    'ImpactoSocioEconomico': {
        '1': '0 - Inexistente (Não existem quaisquer instalações na área afetada a jusante da barragem)',
        '2': '1 - BAIXO (Existe pequena concentração de instalações residenciais, agrícolas, industriais ou de infraestrutura de relevância sócio-econômico-cultural na área afetada a jusante da barragem)',
        '3': '3 - MÉDIO (Existe moderada concentração de instalações residenciais, agrícolas, industriais ou de infraestrutura de relevância sócio-econômico-cultural na área afetada a jusante da barragem)',
        '4': '5 - ALTO (Existe alta concentração de instalações residenciais, agrícolas, industriais ou de infraestrutura de relevância sócio-econômico-cultural na área afetada a jusante da barragem)',
    },
}

# Aplicar mapeamento de valores para os parâmetros
for column_name, value_mapping in value_mappings_page7.items():
    replace_column_values(df_page7, column_name, value_mapping)


# Trocar a vírgula por ponto, depois converter para numérico e inserir duas casas decimais
numeric_columns = [
    'VolumeProjetoReservatorio',
    'VolumeAtualReservatorio',
    'CapacidadeTotalReservatorio',
]


def format_numeric(df, column_names):
    for column_name in column_names:
        df[column_name] = df[column_name].apply(
            lambda x: str(x).replace(',', '.')
        )
        df[column_name] = pd.to_numeric(df[column_name], errors='ignore').map(
            '{:,.2f}'.format
        )


format_numeric(df_page7, numeric_columns)

# Juntar os ids ao dataframe
df_page7 = pd.merge(df_page7, key_id.df_state_id, how='inner', on='ID')

# Reordenar colunas e remover a coluna "ID"
df_page7 = df_page7[
    [
        'ID Barragem',
        'NomeBarragem',
        'VolumeProjetoReservatorio',
        'VolumeAtualReservatorio',
        'CapacidadeTotalReservatorio',
        'ExistenciaPopulacaoJusante',
        'NumeroPessoasAfetadasCasoRompimento',
        'ImpactoAmbiental',
        'ImpactoSocioEconomico',
    ]
]

# Substituir NaN por em branco (tanto em branco, como NaN significam que não houve preenchimento)
df_page7 = df_page7.fillna('')

# Renomear colunas
df_page7.rename(
    columns={
        'VolumeProjetoReservatorio': 'VolumeProjetoReservatorio_m3',
        'VolumeAtualReservatorio': 'VolumeAtualReservatorio_m3',
        'CapacidadeTotalReservatorio': 'CapacidadeTotalReservatorio_m3',
    },
    inplace=True,
)
