import warnings

import pandas as pd
import requests as r

# from bs4 import BeautifulSoup
from pandas import json_normalize

warnings.filterwarnings("ignore")

# Definir URL base
url = "https://app.anm.gov.br/SIGBM/Publico/GerenciarPublico"

# Solicitar GET para obter os cookies
res = r.get(url)
search_cookies = res.cookies

# Definir dados de postagem
post_data = {
    "method": "POST",
    "startIndex": "0",
    "pageSize": "1000",
    "orderProperty": "TotalPontuacao",
    "orderAscending": "false",
    "DTOGerenciarFiltroPublico[CodigoBarragem]": "",
    "DTOGerenciarFiltroPublico[NecessitaPAEBM]": "0",
    "DTOGerenciarFiltroPublico[BarragemInseridaPNSB]": "0",
    "DTOGerenciarFiltroPublico[PossuiBackUpDam]": "0",
    "DTOGerenciarFiltroPublico[SituacaoDeclaracaoCondicaoEstabilidade]": "0",
}

# Solicitar POST com os dados e cookies
res_post = r.post(url, data=post_data, cookies=search_cookies)

# Extrair os valores do JSON
values = res_post.json()["Entities"]

# Criar um DataFrame com os valores
df = pd.json_normalize(values)

# Filtrar por estado
state_filter = "MG"
df_state = df[df["UF"] == state_filter]

# Separar os nomes das barragens ("NomeBarragem")
barragem = df_state["NomeBarragem"]

# Separar as chaves da Página 1
keys = df_state["Chave"]

# Separar os id_barragem ("Codigo") para juntar com os dados exportados do Excel SIGBM
id_barragem = df_state["Codigo"]

# Juntar com os dados exportados do Excel SIGBM
df_state_key = pd.DataFrame({"Chave": keys, "ID Barragem": id_barragem})

# Separar os ids ("CodigoDeclaracaoAtual") para as páginas 1.1 em diante
ids = df_state["CodigoDeclaracaoAtual"]

# Juntar com os dados exportados do Excel SIGBM
df_state_id = pd.DataFrame(
    {"NomeBarragem": barragem, "ID": ids, "ID Barragem": id_barragem}
)
