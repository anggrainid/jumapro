import streamlit as st
import pickle
import pandas as pd

# CRUD Form
st.title("Halaman Prediksi Suatu Prodi")

# Input fields
input_prodi = st.text_input("Masukkan Nama Program Studi : ")

# Mengubah input_last_year_data menjadi input_predict_year
input_predict_year = st.number_input("Masukkan Tahun yang Ingin Diprediksi (ex: 2025):", min_value=2023)
input_last_year_data = input_predict_year - 1

input_years_to_predict = input_predict_year - input_last_year_data  # Prediksi hanya untuk tahun yang dimasukkan
input_kriteria = st.radio("Kriteria", ["Jumlah Minimal", "Persentase Penurunan"])

if input_kriteria == "Persentase Penurunan":
    input_ambang_batas_persen = st.number_input("Ambang Batas Persentase Maksimal (%)", min_value=1, max_value=100, step=1)
    input_ambang_batas_jumlah = None
    input_banyak_data_ts = st.number_input("Masukkan Banyak Tahun yang Dipakai untuk Persentase Penurunan : ", min_value=2, max_value=5, step=1)
    if input_banyak_data_ts > 0:
        input_fields = {}
        for i in range(input_banyak_data_ts - 1):  # Dikurangi 1 karena tidak butuh hingga TS-(input_banyak_data_ts-1)
            if i == 0:
                input_jumlah_mahasiswa_ts = st.number_input(f"Masukkan Jumlah Mahasiswa TS:", value=0)
            else:
                field_name = f"input_jumlah_mahasiswa_ts{i}"
                input_fields[field_name] = st.number_input(f"Masukkan Jumlah Mahasiswa TS-{i}:", value=0)
else:
    input_ambang_batas_jumlah = st.number_input("Ambang Batas Jumlah Mahasiswa Minimal", min_value=1, step=1)
    input_ambang_batas_persen = None
    input_jumlah_mahasiswa_ts = st.number_input("Masukkan Jumlah Mahasiswa TS:", value=0)

# Taking actions based on user input
if st.button("Prediksi"):
    # Load model dari file .sav
    model = pickle.load(open(r"D:\jumapro\next_year_students_prediction.sav", "rb"))

    # Membuat data prediksi
    new_data_prodi = {
        'Prodi': [input_prodi],
        'current_students': [input_jumlah_mahasiswa_ts]
    }
    data_prodi = pd.DataFrame(new_data_prodi)

    current_year = int(input_last_year_data)
    years_to_predict = input_years_to_predict

    for i in range(1, years_to_predict + 1):
        next_year = current_year + i
        column_name = f'{next_year} (Prediksi)'
        data_prodi[column_name] = model.predict(data_prodi['current_students'].values.reshape(-1, 1))
        data_prodi[column_name] = data_prodi[column_name].astype(int)
        data_prodi['current_students'] = data_prodi[column_name]

    hasil_prediksi_pemantauan = None

    if input_kriteria == "Jumlah Minimal":
        prediksi_tahun_terpilih = data_prodi[f'{input_predict_year} (Prediksi)'].iloc[0]
        hasil_prediksi_pemantauan = "Lolos" if prediksi_tahun_terpilih > input_ambang_batas_jumlah else "Tidak Lolos"

    elif input_kriteria == "Persentase Penurunan":
        prediksi_tahun_terpilih = data_prodi[f'{input_predict_year} (Prediksi)'].iloc[0]
        nilai_awal = input_fields[f'input_jumlah_mahasiswa_ts{input_banyak_data_ts - 2}']  # Nilai TS-(input_banyak_data_ts-2)
        persentase_penurunan = ((nilai_awal - prediksi_tahun_terpilih) / nilai_awal) * 100

        data_prodi['Persentase Penurunan'] = persentase_penurunan
        hasil_prediksi_pemantauan = "Lolos" if persentase_penurunan < input_ambang_batas_persen else "Tidak Lolos"

    if hasil_prediksi_pemantauan:
        data_prodi['Hasil Prediksi Pemantauan'] = hasil_prediksi_pemantauan

    # Tampilkan hasil prediksi
    st.write(f'Hasil Prediksi Tahun {input_predict_year}:')
    st.write(data_prodi)