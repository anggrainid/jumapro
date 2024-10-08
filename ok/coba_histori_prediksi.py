def histori_prediksi():

    import streamlit as st
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import pickle

    # Memuat data Anda sendiri
    with open('existing_djm.pickle', 'rb') as handle:
        df = pickle.load(handle)

    df = df.dropna(how="all")
    df = df.replace('#N/A ()', 0)

    # Mengidentifikasi kolom tahun
    # Asumsikan bahwa kolom tahun adalah kolom yang bisa dikonversi menjadi integer
    def is_year(column_name):
        try:
            int(column_name)
            return True
        except ValueError:
            return False

    year_columns = [col for col in df.columns if is_year(col)]

    # Pastikan kolom 'Prodi' ada di DataFrame
    if 'Prodi' in df.columns:
        # Melakukan melt hanya pada kolom tahun
        df_melted = df.melt(id_vars=['Prodi'], value_vars=year_columns, var_name='Tahun', value_name='Jumlah Mahasiswa')
        df_melted['Tahun'] = df_melted['Tahun'].astype(int)
    else:
        st.error("Kolom 'Prodi' tidak ditemukan dalam data.")
        st.stop()

    # Memuat model prediksi yang sudah ada
    model = pickle.load(open("next_year_students_prediction.sav", "rb"))

    # Fungsi prediksi menggunakan model Anda
    def prediksi_jumlah_mahasiswa(jumlah_mahasiswa_sekarang):
        prediksi = model.predict([[jumlah_mahasiswa_sekarang]])[0]
        return round(prediksi)

    # Menambahkan kolom prediksi
    df_melted['Prediksi Jumlah Mahasiswa'] = df_melted['Jumlah Mahasiswa'].apply(lambda x: prediksi_jumlah_mahasiswa(x))

    # Tampilan Streamlit
    # st.title('Histori Prediksi')

    # Dropdown pilihan program studi
    prodi_list = df_melted['Prodi'].unique()
    prodi = st.selectbox('Pilih Program Studi', prodi_list)

    # Filter data berdasarkan prodi yang dipilih
    df_prodi = df_melted[df_melted['Prodi'] == prodi]

    # Menghitung total mahasiswa sebenarnya dan prediksi
    total_actual = df_prodi['Jumlah Mahasiswa'].sum()
    total_predicted = df_prodi['Prediksi Jumlah Mahasiswa'].sum()

    st.write('Total Mahasiswa Sebenarnya: ', total_actual)
    st.write('Total Prediksi Mahasiswa: ', total_predicted)

    # Grafik Trend Jumlah Mahasiswa
    st.write('Grafik Trend Jumlah Mahasiswa')

    plt.figure(figsize=(10, 6))

    # Plot Mahasiswa Sebenarnya
    plt.plot(df_prodi['Tahun'], df_prodi['Jumlah Mahasiswa'], label='Mahasiswa Sebenarnya', marker='o', color='blue')

    # Plot Prediksi Mahasiswa
    plt.plot(df_prodi['Tahun'], df_prodi['Prediksi Jumlah Mahasiswa'], label='Prediksi Mahasiswa', marker='o', color='red')

    # Menghitung garis tren untuk Mahasiswa Sebenarnya
    z = np.polyfit(df_prodi['Tahun'], df_prodi['Jumlah Mahasiswa'], 1)
    p = np.poly1d(z)
    plt.plot(df_prodi['Tahun'], p(df_prodi['Tahun']), "g--", label='Garis Tren')

    plt.legend()
    plt.xlabel('Tahun')
    plt.ylabel('Jumlah Mahasiswa')
    plt.title(f'Trend Jumlah Mahasiswa di {prodi}')
    st.pyplot(plt)

    df_prodi['Tahun'] = df_prodi['Tahun'].astype(str)
    # Tabel Detail Data
    st.write('Tabel Detail Data')
    st.dataframe(df_prodi)