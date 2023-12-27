import re
import time
import warnings
from collections import Counter

import pandas as pd
import requests as r
from bs4 import BeautifulSoup
from requests.exceptions import ConnectTimeout
from unidecode import unidecode

from . import key_id

warnings.filterwarnings('ignore')


def scrap_id_info(id: str) -> dict:
    print(f'{id} Extraindo dados Tipo de Rejeito Armazenado...')
    id_url = f'https://app.anm.gov.br/SIGBM/RejeitoArmazenadoPublico?idDeclaracao={id}'

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

    # Para as informações selecionadas
    tag1 = soup.find_all(selected='selected')
    id_dict1 = {
        ('MinerioPrincipalReservatorio'): tag.get_text('value') for tag in tag1
    }

    # Para as informações de escolha
    tag2 = soup.find_all(checked='checked')
    id_dict2 = {tag.get('name'): tag.get('value') for tag in tag2}

    # Para as informações digitadas
    tag3 = soup.find_all('input', {'class': 'form-control'})
    id_dict3 = {tag.get('name'): tag.get('value') for tag in tag3}

    # Regex para capturar nomes em JavaScript
    tag4 = soup.find_all('script', {'type': 'text/javascript'})[0].text
    name_pattern = re.compile(
        r'((?<=DescricaoProcessoBeneficiamento":")(.*?)")', flags=re.M
    )
    tag4 = name_pattern.findall(tag4)
    id_dict4 = {('ProcessoBeneficiamento'): tag4 for tag in tag4}

    tag5 = soup.find_all('script', {'type': 'text/javascript'})[0].text
    name_pattern = re.compile(r'((?<=Descricao":")(.*?)")', flags=re.M)
    tag5 = name_pattern.findall(tag5)
    id_dict5 = {('ProdutosQuimicosUtilizados'): tag5 for tag in tag5}

    tag6 = soup.find_all('script', {'type': 'text/javascript'})[0].text
    name_pattern = re.compile(
        r'((?<=DescricaoSubstancia":")(.*?)")|((?<="Teor":)(.*?)")', flags=re.M
    )
    tag6 = name_pattern.findall(tag6)
    id_dict6 = {('OutrasSubstanciasPresentes'): tag6 for tag in tag6}

    dict = {
        **id_dict1,
        **id_dict2,
        **id_dict3,
        **id_dict4,
        **id_dict5,
        **id_dict6,
    }

    dict['ID'] = id

    # Definir possíveis colunas com valores vazios
    missing_columns = [
        'MinerioPrincipalReservatorio',
        'ExisteProcessoBeneficiamento',
        'ProcessoBeneficiamento',
        'ProdutosQuimicosUtilizados',
        'BarragemArmazenaCianeto',
        'TeorMinerioInseridoRejeito',
        'OutrasSubstanciasPresentes',
    ]
    for col in missing_columns:
        if col not in dict:
            dict[col] = ''

    return dict


# Obter as informações acima, agora para todas as barragens
id_page3 = [scrap_id_info(id) for id in key_id.ids]

# Limpeza dos dados
df_page3 = pd.DataFrame(id_page3)

# Remover caracteres extraídos em javascript - ProcessoBeneficiamento e ProdutosQuimicosUtilizados
columns_to_clean = ['ProcessoBeneficiamento', 'ProdutosQuimicosUtilizados']

for column in columns_to_clean:
    df_page3[column] = df_page3[column].apply(
        lambda x: re.sub(r'[,\[\]()\\"]', '', str(x))
    )


# Remover blocos duplicados que vieram do javascript
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


df_page3['ProcessoBeneficiamento'] = df_page3['ProcessoBeneficiamento'].apply(
    remove_repeated_blocks
)

df_page3['ProdutosQuimicosUtilizados'] = df_page3[
    'ProdutosQuimicosUtilizados'
].apply(remove_repeated_blocks)

df_page3['ProdutosQuimicosUtilizados'] = (
    df_page3['ProdutosQuimicosUtilizados']
    .str.replace(r" '", "'")
    .str.replace(r"' ", "'")
    .str.replace(r"''", "'")
    .str.strip("'")
    .str.replace(r"'", ', ')
)

df_page3['ProcessoBeneficiamento'] = (
    df_page3['ProcessoBeneficiamento']
    .str.replace(r" '", "'")
    .str.replace(r"' ", "'")
    .str.replace(r"''", "'")
    .str.strip("'")
    .str.replace(r"'", ', ')
)

# Remover caracteres extraídos em javascript - OutrasSubstanciasPresentes
from unidecode import unidecode

df_page3['OutrasSubstanciasPresentes'] = df_page3[
    'OutrasSubstanciasPresentes'
].apply(lambda x: re.sub(r'[!=,\[\](){}\\"]', '', unidecode(str(x))))


def extract_between_single_quotes_and_equal(s):
    matches = re.findall(r'([^]+=[^]+)', s)
    return ' '.join(matches)


df_page3['OutrasSubstanciasPresentes'] = df_page3[
    'OutrasSubstanciasPresentes'
].apply(extract_between_single_quotes_and_equal)

df_page3['OutrasSubstanciasPresentes'] = (
    df_page3['OutrasSubstanciasPresentes']
    .str.replace(r"' '' '' '' '' '", ' = ')
    .str.replace(r"'' ''", '')
)


def extract_words(text):
    matches = re.findall(r'([A-Za-z\s]+ = \d+\.\d+)', text)
    return ', '.join(matches)


df_page3['OutrasSubstanciasPresentes'] = df_page3[
    'OutrasSubstanciasPresentes'
].apply(extract_words)


# Remover blocos duplicados que vieram do javascript
def remove_repeated_blocks(text):
    blocks = text.split(', ')
    block_counts = Counter(blocks)
    result_blocks = []

    for block in blocks:
        if block_counts[block] == 1:
            result_blocks.append(block)
        elif block not in result_blocks:
            result_blocks.append(block)

    return ', '.join(result_blocks)


df_page3['OutrasSubstanciasPresentes'] = df_page3[
    'OutrasSubstanciasPresentes'
].apply(remove_repeated_blocks)

# Trocar a vírgula por ponto, converter para numérico e inserir duas casas decimais
df_page3['TeorMinerioInseridoRejeito'] = df_page3[
    'TeorMinerioInseridoRejeito'
].apply(lambda x: str(x).replace(',', '.'))

df_page3['TeorMinerioInseridoRejeito'] = pd.to_numeric(
    df_page3['TeorMinerioInseridoRejeito'], errors='coerce'
).map('{:,.2f}'.format)

# Juntar os ids ao dataframe
df_page3 = pd.merge(df_page3, key_id.df_state_id, how='inner', on='ID')

# Reordenar colunas e remover a coluna "ID"
df_page3 = df_page3[
    [
        'ID Barragem',
        'NomeBarragem',
        'MinerioPrincipalReservatorio',
        'ExisteProcessoBeneficiamento',
        'ProcessoBeneficiamento',
        'ProdutosQuimicosUtilizados',
        'BarragemArmazenaCianeto',
        'TeorMinerioInseridoRejeito',
        'OutrasSubstanciasPresentes',
    ]
]

# Substituir True/False para Sim/Não
df_page3 = df_page3.replace(['True', 'False'], ['Sim', 'Não'])

# Substituir "nan" por ""
df_page3 = df_page3.replace({'nan': ''})

# Renomear colunas
df_page3.rename(
    columns={'TeorMinerioInseridoRejeito': 'TeorMinerioInseridoRejeito_%'},
    inplace=True,
)
