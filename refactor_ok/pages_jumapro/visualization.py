import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from component.data import get_data, refresh_data, preprocess_data
from sklearn.metrics import r2_score

def visualisasi_model(existing_djm):

    # # Memuat data existing_djm dari file pickle
    # with open('existing_djm.pickle', 'rb') as handle:
    #     df = pickle.load(handle)

    # df = df.dropna(how="all")
    # df = df.replace('#N/A ()', 0)

    # # Mengidentifikasi kolom tahun
    # def is_year(column_name):
    #     try:
    #         int(column_name)
    #         return True
    #     except ValueError:
    #         return False

    # # Memilih kolom yang merupakan tahun berdasarkan tipe data numerik
    # year_columns = [col for col in df.columns if is_year(col)]

    
    # 1. Connections from google sheets
    # if st.button('Refresh Data'):
    #     existing_djm = refresh_data('djm')
    #     st.success("Data berhasil dimuat ulang dari Google Sheets!")
    # else:
    # # 2. Connections from pickle
    #     existing_djm = get_data('djm')
    # # st.write(existing_djm)
    #  # 3. Data preprocessing
    # existing_djm = preprocess_data(existing_djm)

    # Convert column names to string and filter columns that are numeric (representing years)
    year_columns = [col for col in existing_djm.columns if str(col).isdigit()]

    
    
    
    # Filter dropdown untuk memilih tahun
    # st.title("Visualisasi Model")
    tahun = st.selectbox('Pilih Tahun', year_columns[:-1])  # Menghapus tahun terakhir untuk menjaga agar ada data 'setelahnya'

    # Menentukan kolom tahun selanjutnya untuk 'Jumlah Mahasiswa Setelahnya'
    tahun_selanjutnya = str(int(tahun) + 1)

    # Menampilkan data berdasarkan tahun yang dipilih
    df_tahun = existing_djm[['Prodi', int(tahun), int(tahun_selanjutnya)]].copy()
    df_tahun.columns = ['Program Studi', 'Jumlah Mahasiswa Saat Ini', 'Jumlah Mahasiswa Setelahnya']

    # Menghapus baris dengan NaN pada 'Jumlah Mahasiswa Setelahnya'
    df_tahun = df_tahun.dropna(subset=['Jumlah Mahasiswa Setelahnya'])

    # Membuat scatter plot berdasarkan tahun yang dipilih
    X = df_tahun['Jumlah Mahasiswa Saat Ini'].values.reshape(-1, 1)  # Jumlah Mahasiswa Saat Ini
    y = df_tahun['Jumlah Mahasiswa Setelahnya'].values  # Jumlah Mahasiswa Setelahnya

    # Membuat model regresi linear
    model = LinearRegression()
    model.fit(X, y)
    y_pred = model.predict(X)

    # Menghitung nilai R²
    r2 = r2_score(y, y_pred)
    r2 = round (r2, 2)
    st.write(f'Nilai R² untuk prediksi tahun selanjutnya adalah: ', r2)  # Menampilkan R²

    # Menambahkan kolom prediksi ke df_tahun
    df_tahun['Prediksi Jumlah Mahasiswa Setelahnya'] = np.round(y_pred)
    
    # comparison = (df_tahun['Prediksi Jumlah Mahasiswa Setelahnya'] / df_tahun['Jumlah Mahasiswa Setelahnya']) * 100
    # df_tahun['Perbandingan Persentase Prediksi Mahasiswa Baru (%)'] = np.where(df_tahun['Jumlah Mahasiswa Setelahnya']==0, np.nan, comparison.round())

    # r2_prodi = r2_score(df_tahun['Jumlah Mahasiswa Setelahnya'], df_tahun['Prediksi Jumlah Mahasiswa Setelahnya'])
    # r2_prodi = round(r2, 2)
    # df_tahun['Perbandingan Persentase Prediksi Mahasiswa Baru (%)'] = r2_prodi


    average_row = pd.DataFrame({
        'Program Studi': ['Average'],
        'Jumlah Mahasiswa Baru Saat Ini': [df_tahun['Jumlah Mahasiswa Saat Ini'].mean(skipna=True)],
        'Jumlah Mahasiswa Baru Setelahnya': [df_tahun['Jumlah Mahasiswa Setelahnya'].mean(skipna=True)],
        'Prediksi Jumlah Mahasiswa Baru Setelahnya': [df_tahun['Prediksi Jumlah Mahasiswa Setelahnya'].mean(skipna=True)]
        # 'R²': [df_tahun['Perbandingan Persentase Prediksi Mahasiswa Baru (%)'].mean(skipna=True)]
    })
    # Menambahkan baris rata-rata ke dataframe
    df_tahun = pd.concat([df_tahun, average_row], ignore_index=True)

    plt.figure(figsize=(10, 6))

    # Scatter plot jumlah mahasiswa saat ini vs jumlah mahasiswa setelahnya
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
    correlation_df = df_tahun[['Jumlah Mahasiswa Saat Ini', 'Jumlah Mahasiswa Setelahnya']]

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

    