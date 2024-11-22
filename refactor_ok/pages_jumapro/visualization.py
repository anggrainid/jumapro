import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from component.data import get_data, refresh_data, preprocess_data
from sklearn.metrics import r2_score, mean_squared_error
import pickle

def visualisasi_model(existing_djm):

    year_columns = [col for col in existing_djm.columns if str(col).isdigit()]
    tahun = st.selectbox('Pilih Tahun', year_columns[:-1])
    tahun_selanjutnya = str(int(tahun) + 1)

    # Menampilkan data berdasarkan tahun yang dipilih
    df_tahun = existing_djm[['Prodi', int(tahun), int(tahun_selanjutnya)]].copy()
    df_tahun.columns = ['Program Studi', 'Jumlah Mahasiswa Baru Saat Ini', 'Jumlah Mahasiswa Baru Setelahnya']

    # Menghapus baris dengan NaN pada 'Jumlah Mahasiswa Setelahnya'
    df_tahun = df_tahun.dropna(subset=['Jumlah Mahasiswa Baru Setelahnya'])


    # Membuat scatter plot berdasarkan tahun yang dipilih
    X = df_tahun['Jumlah Mahasiswa Baru Saat Ini'].values.reshape(-1, 1)  # Jumlah Mahasiswa Saat Ini
    y = df_tahun['Jumlah Mahasiswa Baru Setelahnya'].values  # Jumlah Mahasiswa Setelahnya

    # Membuat model regresi linear
    model = pickle.load(open("next_year_students_prediction.sav", "rb"))
    model.fit(X, y)
    y_pred = model.predict(X)

    # Menghitung nilai R²
    r2 = r2_score(y, y_pred)
    r2 = round (r2, 2)
    st.write(f'Nilai R² untuk prediksi tahun selanjutnya adalah: ', r2)  # Menampilkan R²

    # Menghitung nilai RMSE
    rmse = np.sqrt(mean_squared_error(y, y_pred))
    rmse = round(rmse, 2)
    st.write(f'Root Mean Squared Error (RMSE): {rmse}')  # Menampilkan RMSE


    # Menambahkan kolom prediksi ke df_tahun
    df_tahun['Prediksi Jumlah Mahasiswa Baru Setelahnya'] = np.round(y_pred)

    average_row = pd.DataFrame({
        'Program Studi': ['Average'],
        'Jumlah Mahasiswa Baru Saat Ini': [df_tahun['Jumlah Mahasiswa Baru Saat Ini'].mean(skipna=True)],
        'Jumlah Mahasiswa Baru Setelahnya': [df_tahun['Jumlah Mahasiswa Baru Setelahnya'].mean(skipna=True)],
        'Prediksi Jumlah Mahasiswa Baru Setelahnya': [df_tahun['Prediksi Jumlah Mahasiswa Baru Setelahnya'].mean(skipna=True)]
    })
    # Menambahkan baris rata-rata ke dataframe
    df_tahun = pd.concat([df_tahun, average_row], ignore_index=True)


    plt.figure(figsize=(10, 6))
    plt.scatter(X, y, color='blue', label='Data Sebenarnya')
    # Menambahkan garis regresi merah
    plt.plot(X, y_pred, color='red', linewidth=2, label='Data Prediksi')
    # Menambahkan label, judul tanpa legend dan grid
    plt.title(f"Scatter Plot Linear Regression\nTahun: {tahun}", fontsize=18)
    plt.xlabel('Jumlah Mahasiswa Baru Saat Ini', fontsize=12)
    plt.ylabel('Jumlah Mahasiswa Baru Setelahnya', fontsize=12)
    plt.grid(False)
    plt.legend()
    # Menampilkan grafik di Streamlit
    st.pyplot(plt)


    # Matriks Korelasi
    st.write("Matriks Korelasi")
    # Menghitung korelasi menggunakan data 'Jumlah Mahasiswa Saat Ini' dan 'Jumlah Mahasiswa Setelahnya'
    correlation_df = df_tahun[['Jumlah Mahasiswa Baru Saat Ini', 'Jumlah Mahasiswa Baru Setelahnya']]
    # Menghitung korelasi
    corr = correlation_df.corr()
    # Menampilkan matriks korelasi menggunakan heatmap dari Seaborn
    plt.figure(figsize=(8, 6))
    sns.heatmap(corr, annot=True, cmap="Blues", vmin=0, vmax=1, linewidths=0.5)
    # Menampilkan grafik matriks korelasi di Streamlit
    st.pyplot(plt)

    # Menampilkan tabel detail data
    st.write('Tabel Detail Data')
    st.dataframe(df_tahun)

    