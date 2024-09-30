# pages/visualisasi.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from data.gsheets import read_worksheet
import pickle

def visualisasi_model():
    df = read_worksheet("Data Jumlah Mahasiswa")
    df = df.dropna(how="all")
    df = df.replace('#N/A ()', 0)

    # Mengidentifikasi kolom tahun
    def is_year(column_name):
        try:
            int(column_name)
            return True
        except ValueError:
            return False

    year_columns = [col for col in df.columns if is_year(col)]

    # Filter dropdown untuk memilih tahun
    tahun = st.selectbox('Pilih Tahun', year_columns[:-1])  # Menghapus tahun terakhir untuk menjaga agar ada data 'setelahnya'

    # Menentukan kolom tahun selanjutnya untuk 'Jumlah Mahasiswa Setelahnya'
    tahun_selanjutnya = str(int(tahun) + 1)

    # Menampilkan data berdasarkan tahun yang dipilih
    df_tahun = df[['Prodi', str(tahun), tahun_selanjutnya]].copy()
    df_tahun.columns = ['Program Studi', 'Jumlah Mahasiswa Saat Ini', 'Jumlah Mahasiswa Setelahnya']

    # Menghapus baris dengan NaN pada 'Jumlah Mahasiswa Setelahnya'
    df_tahun = df_tahun.dropna(subset=['Jumlah Mahasiswa Setelahnya'])

    # Memuat model
    model_path = 'models/next_year_students_prediction.sav'
    try:
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
    except FileNotFoundError:
        st.error(f"Model file tidak ditemukan di {model_path}")
        return

    # Membuat scatter plot berdasarkan tahun yang dipilih
    X = df_tahun['Jumlah Mahasiswa Saat Ini'].values.reshape(-1, 1)  # Jumlah Mahasiswa Saat Ini
    y = df_tahun['Jumlah Mahasiswa Setelahnya'].values  # Jumlah Mahasiswa Setelahnya

    y_pred = model.predict(X)

    plt.figure(figsize=(10, 6))

    # Scatter plot jumlah mahasiswa saat ini vs jumlah mahasiswa setelahnya
    plt.scatter(X, y, color='blue', label='Mahasiswa Sebenarnya')

    # Plot garis regresi merah
    plt.plot(X, y_pred, color='red', linewidth=2, label='Garis Prediksi')

    # Menghitung garis tren untuk Mahasiswa Sebenarnya
    z = np.polyfit(df_tahun['Jumlah Mahasiswa Saat Ini'], y, 1)
    p = np.poly1d(z)
    plt.plot(df_tahun['Jumlah Mahasiswa Saat Ini'], p(df_tahun['Jumlah Mahasiswa Saat Ini']), "g--", label='Garis Tren')

    # Menambahkan label, judul tanpa legend dan grid
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
