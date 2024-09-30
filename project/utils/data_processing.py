# utils/data_processing.py
import pandas as pd

def clean_data(df, unused_columns):
    df = df.dropna(how="all")
    df = df.replace('#N/A ()', 0)
    df = df.drop(unused_columns, axis=1, errors='ignore')
    return df

def is_year(column_name):
    try:
        int(column_name)
        return True
    except ValueError:
        return False
