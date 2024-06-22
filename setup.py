from datetime import datetime

import pandas as pd

# Inserir a data atual no final do arquivo
DATE = datetime.now().strftime("%Y-%m-%d")

from paginas_sigbm import (
    page1,
    page1_1,
    page1_2,
    page2,
    page3,
    page4,
    page5,
    page6,
    page7,
)

# Definir o caminho do arquivo Excel
EXCEL_FILE_PATH = f"data/download_sigbm_{DATE}.xlsx"

# Criar dicionário que mapeia o nome da página para o DataFrame correspondente
page_dataframes = {
    "1": page1.df_page1,
    "1.1": page1_1.df_page1_1,
    "1.2": page1_2.df_page1_2,
    "2": page2.df_page2,
    "3": page3.df_page3,
    "4": page4.df_page4,
    "5": page5.df_page5,
    "6": page6.df_page6,
    "7": page7.df_page7,
}

with pd.ExcelWriter(EXCEL_FILE_PATH) as writer:
    for sheet_name, df in page_dataframes.items():
        df.to_excel(writer, sheet_name=sheet_name, index=False)
