# visualisasi_model.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from utils.data_access import load_pickle, load_model_cached
from utils.data_processing import is_year

def visualisasi_model():
    df = load_pickle('data/existing_djm.pickle')
    if df is None:
        st.error("Data tidak ditemukan. Silakan muat ulang data.")
        return

    df = df.dropna(how="all")
    df = df.replace('#N/A ()', 0)

    year_columns = [col for col in df.columns if is_year(col)]

    tahun = st.selectbox('Pilih Tahun', year_columns[:-1])  # Menghapus tahun terakhir untuk menjaga agar ada data 'setelahnya'
    tahun_selanjutnya = str(int(tahun) + 1)

    df_tahun = df[['Prodi', str(tahun), tahun_selanjutnya]].copy()
    df_tahun.columns = ['Program Studi', 'Jumlah Mahasiswa Saat Ini', 'Jumlah Mahasiswa Setelahnya']

    df_tahun = df_tahun.dropna(subset=['Jumlah Mahasiswa Setelahnya'])

    model = load_model_cached("models/next_year_students_prediction.sav")

    X = df_tahun['Jumlah Mahasiswa Saat Ini'].values.reshape(-1, 1)
    y = df_tahun['Jumlah Mahasiswa Setelahnya'].values

    y_pred = model.predict(X)

    plt.figure(figsize=(10, 6))
    plt.scatter(X, y, color='blue', label='Data Sebenarnya')
    plt.plot(X, y_pred, color='red', linewidth=2, label='Garis Prediksi')
    plt.title(f"Scatter Plot Linear Regression\nTahun: {tahun}", fontsize=18)
    plt.xlabel('Jumlah Mahasiswa Saat Ini', fontsize=12)
    plt.ylabel('Jumlah Mahasiswa Setelahnya', fontsize=12)
    plt.grid(False)
    plt.legend()
    st.pyplot(plt)

    # Matriks Korelasi
    st.write("Matriks Korelasi")
    correlation_df = df_tahun[['Jumlah Mahasiswa Saat Ini', 'Jumlah Mahasiswa Setelahnya']]
    corr = correlation_df.corr()

    plt.figure(figsize=(8, 6))
    sns.heatmap(corr, annot=True, cmap="Blues", vmin=0, vmax=1, linewidths=0.5)
    st.pyplot(plt)

    # Tabel Detail Data
    st.write('Tabel Detail Data')
    st.dataframe(df_tahun)
