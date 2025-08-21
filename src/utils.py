import pandas as pd


def get_operations_excel(input_file_excel) -> list:
    """Возвращает список транзакций, загруженный из файла excel"""
    df = pd.read_excel(input_file_excel)
    operations = df.where(pd.notnull(df), None).to_dict(orient='records')
    return operations



