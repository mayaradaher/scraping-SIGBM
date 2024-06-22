import warnings
import pandas as pd
import requests as r
from pandas import json_normalize

warnings.filterwarnings("ignore")

# Definir URL base
url = "https://app.anm.gov.br/SIGBM/Publico/GerenciarPublico"

# Headers
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
}

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

# Solicitar GET para obter os cookies
try:
    res = r.get(url, headers=headers, verify=False)
    res.raise_for_status()  # Verificar se a solicitação GET foi bem-sucedida
    search_cookies = res.cookies
except r.RequestException as e:
    print(f"Falha na solicitação GET: {e}")
    exit()

# Solicitar POST com os dados e cookies
try:
    res_post = r.post(
        url, data=post_data, cookies=search_cookies, headers=headers, verify=False
    )
    res_post.raise_for_status()  # Verificar se a solicitação POST foi bem-sucedida
except r.RequestException as e:
    print(f"Falha na solicitação POST: {e}")
    exit()

# Verificar o conteúdo da resposta POST
try:
    values = res_post.json().get("Entities", [])
    if not values:
        print("Nenhum dado encontrado.")
        exit()
except ValueError as e:
    print(f"Erro ao converter resposta para JSON: {e}")
    exit()

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

print(df_state_id)
