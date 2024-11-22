import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pickle
import pandas as pd
import matplotlib.pyplot as plt

def kalkulator_prediksi():

    # Halaman Prediksi Suatu Prodi
    st.title("Halaman Kalkulator Prediksi")
    st.markdown("Halaman ini digunakan untuk melakukan prediksi jumlah mahasiswa baru dengan melihat jumlah mahasiswa baru saat ini")
    input_jumlah_mahasiswa_ts = st.number_input(f"Masukkan Jumlah Mahasiswa Baru Saat Ini:", value=0)
    input_years_to_predict = st.number_input("Masukkan Proyeksi Prediksi (Dalam Satuan Tahun) : ", min_value=1, max_value=10)

    model = pickle.load(open(r"D:\jumapro\next_year_students_prediction.sav", "rb"))
    new_data_prodi = {
        # 'Prodi': [input_prodi],
        'Jumlah Mahasiswa Saat Ini (TS)': [input_jumlah_mahasiswa_ts]
    }
    data_prodi = pd.DataFrame(new_data_prodi)


    # Prediksi beberapa tahun ke depan
    current_students = data_prodi['Jumlah Mahasiswa Saat Ini (TS)'].copy()
    years = []
    predictions = []
    years.append(0)
    predictions.append(data_prodi['Jumlah Mahasiswa Saat Ini (TS)'].values[0])
    for i in range(1, input_years_to_predict + 1):
        # next_year = input_last_year + i
        column_name = f'Jumlah Mahasiswa Setelahnya (Prediksi TS+{i})'
        data_prodi[column_name] = model.predict(current_students.values.reshape(-1, 1))
        data_prodi[column_name] = data_prodi[column_name].astype(int)
        current_students = data_prodi[column_name].copy()

        years.append(i)
        predictions.append(data_prodi[column_name].values[0])
   
   
   
    # Tampilkan hasil prediksi dan penilaian jika tombol "Prediksi" ditekan
    if st.button("Prediksi"):
        
        st.write(data_prodi)
        # Scatter plot
        fig, ax = plt.subplots()
        ax.scatter(years, predictions, color='blue')
        ax.plot(years, predictions, color='blue', alpha=0.5)  # Menambahkan garis penghubung
        ax.set_title('Prediksi Jumlah Mahasiswa Baru')
        ax.set_xlabel('Tahun Ke Depan')
        ax.set_ylabel('Prediksi Jumlah Mahasiswa Baru')
        ax.set_xticks(years)
        st.pyplot(fig)

# kalkulator_prediksi()