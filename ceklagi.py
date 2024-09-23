import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

# Data Mahasiswa per tahun (Contoh Data)
data = {
    'Tahun': [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023],
    'Jumlah Mahasiswa Saat Ini': [53, 38, 37, 59, 44, 49, 57, 61, 62, 79, 64]
}

df = pd.DataFrame(data)

# Model Prediksi (Menggunakan Linear Regression sebagai contoh)
def prediksi_jumlah_mahasiswa(jumlah_mahasiswa_sekarang):
    # Menggunakan linear regression untuk memprediksi data tahun berikutnya
    X = np.array(df['Tahun'][:-1]).reshape(-1, 1)  # Tahun hingga tahun ke-n-1
    y = np.array(df['Jumlah Mahasiswa Saat Ini'][:-1])  # Jumlah mahasiswa hingga tahun ke-n-1

    model = LinearRegression()
    model.fit(X, y)

    # Prediksi untuk tahun ke-n berdasarkan data tahun sebelumnya
    prediksi = model.predict(np.array([[jumlah_mahasiswa_sekarang]]))[0]
    return prediksi

# Membuat kolom prediksi untuk data tahun berikutnya
df['Prediksi'] = df['Jumlah Mahasiswa Saat Ini'].shift(1).fillna(df['Jumlah Mahasiswa Saat Ini'].mean())  # Menggunakan prediksi dari tahun sebelumnya

# Menghitung prediksi jumlah mahasiswa setelahnya
df['Jumlah Mahasiswa Setelahnya'] = df['Jumlah Mahasiswa Saat Ini'].shift(-1)
df['Prediksi Setelahnya'] = df['Jumlah Mahasiswa Saat Ini'].apply(lambda x: prediksi_jumlah_mahasiswa(x))

# Fungsi untuk menghitung total mahasiswa
def total_mahasiswa(df):
    return df['Jumlah Mahasiswa Saat Ini'].sum()

# Fungsi untuk menghitung total prediksi mahasiswa
def total_prediksi(df):
    return df['Prediksi'].sum()

# Tampilan Streamlit
st.title('Histori Jumlah Mahasiswa')

# Dropdown pilihan program studi (Contoh data diambil dari dua program studi)
prodi = st.selectbox('Pilih Program Studi', ['Doktor Ilmu Kedokteran dan Kesehatan', 'Magister Ilmu Biomedik'])

# Tampilkan total jumlah mahasiswa sebenarnya dan prediksi
st.write('Total Mahasiswa Sebenarnya: ', total_mahasiswa(df))
st.write('Total Prediksi Mahasiswa: ', total_prediksi(df))

# Line Chart Jumlah Mahasiswa Sebenarnya dan Prediksi
st.write('Grafik Trend Jumlah Mahasiswa')

plt.figure(figsize=(10, 6))
plt.plot(df['Tahun'], df['Jumlah Mahasiswa Saat Ini'], label='Mahasiswa Sebenarnya', marker='o', color='blue')
plt.plot(df['Tahun'], df['Prediksi'], label='Prediksi Mahasiswa', linestyle='--', marker='x', color='red')
plt.legend()
plt.xlabel('Tahun')
plt.ylabel('Jumlah Mahasiswa')
plt.title(f'Trend Jumlah Mahasiswa di {prodi}')
st.pyplot(plt)

# Tabel Detail Data
st.write('Tabel Detail Data')

# Membuat tabel detail yang berisi prodi, tahun, jumlah mahasiswa saat ini, jumlah mahasiswa setelahnya, dan prediksi jumlah mahasiswa setelahnya
df_tabel = df[['Tahun', 'Jumlah Mahasiswa Saat Ini', 'Jumlah Mahasiswa Setelahnya', 'Prediksi Setelahnya']].copy()
df_tabel['Prodi'] = prodi  # Menambahkan kolom Prodi

st.dataframe(df_tabel)
