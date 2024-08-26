import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pickle
import pandas as pd

# Halaman Prediksi Suatu Prodi
st.title("Halaman Prediksi Suatu Prodi")

# Input fields
input_prodi = st.text_input("Masukkan Nama Program Studi : ")

input_predict_year = st.number_input("Masukkan Tahun yang Ingin Diprediksi (ex: 2025) : ", min_value=2024)
input_last_year_data = input_predict_year - 1

input_years_to_predict = st.number_input("Masukkan Proyeksi Prediksi (Dalam Satuan Tahun) : ", min_value=1, max_value=10)

input_kriteria = st.radio("Kriteria", ["Jumlah Minimal", "Persentase Penurunan"])

if input_kriteria == "Persentase Penurunan":
    input_ambang_batas_persen = st.number_input("Ambang Batas Persentase Maksimal (%)", min_value=1, max_value=100, step=1)
    input_banyak_data_ts = st.number_input("Masukkan Banyak Tahun yang Dipakai untuk Persentase Penurunan : ", min_value=2, max_value=5, step=1)
    input_ambang_batas_jumlah = None
    input_jumlah_mahasiswa_ts = None

    if input_banyak_data_ts > 1:
        input_fields = {}
        for i in range(input_banyak_data_ts - 1):
            field_name = f"input_jumlah_mahasiswa_ts{i}"
            input_fields[field_name] = st.number_input(f"Masukkan Jumlah Mahasiswa TS-{i+1}:", value=0)

else:
    input_ambang_batas_jumlah = st.number_input("Ambang Batas Jumlah Mahasiswa Minimal", min_value=1, step=1)
    input_jumlah_mahasiswa_ts = st.number_input(f"Masukkan Jumlah Mahasiswa TS:", value=0)
    input_ambang_batas_persen = None
    input_fields = None

# Fungsi untuk menghitung persentase penurunan
def hitung_persentase_penurunan(data, current_year, input_banyak_data_ts):
    start_year = current_year - input_banyak_data_ts + 1
    end_year = current_year
    penurunan_total = (data[f"{end_year} (Prediksi)"] - data[f"{start_year} (Prediksi)"]) / data[f"{start_year} (Prediksi)"]
    persentase_penurunan = penurunan_total * 100
    return persentase_penurunan

# Fungsi prediksi dan penilaian kelolosan
def prediksi_dan_penilaian(input_prodi, input_predict_year, input_last_year_data, input_years_to_predict, input_kriteria, input_ambang_batas_jumlah, input_ambang_batas_persen, input_fields):
    # Load model dari file .sav
    model = pickle.load(open(r"D:\jumapro\next_year_students_prediction.sav", "rb"))

    # Siapkan data untuk prediksi
    last_year_data = input_last_year_data
    current_year = input_predict_year
    years_to_predict = input_years_to_predict

    if input_kriteria == "Jumlah Minimal":
        new_data_prodi = {
            'Prodi': [input_prodi],
            'current_students': [input_jumlah_mahasiswa_ts]
        }
    else:
        new_data_prodi = {
            'Prodi': [input_prodi],
            'current_students': [input_fields[list(input_fields.keys())[0]]]
        }
    
    data_prodi = pd.DataFrame(new_data_prodi)

    # Prediksi beberapa tahun ke depan
    current_students = data_prodi['current_students'].copy()
    for i in range(1, input_years_to_predict + 1):
        next_year = input_last_year_data + i
        column_name = f'{next_year} (Prediksi)'
        data_prodi[column_name] = model.predict(current_students.values.reshape(-1, 1))
        data_prodi[column_name] = data_prodi[column_name].astype(int)
        current_students = data_prodi[column_name].copy()

    # Penilaian kelolosan berdasarkan kriteria
    if input_kriteria == "Jumlah Minimal":
        hasil_prediksi_pemantauan = "Lolos" if data_prodi[f"{input_predict_year} (Prediksi)"].values[0] > input_ambang_batas_jumlah else "Tidak Lolos"
        data_prodi[f"Hasil Prediksi Pemantauan ({input_predict_year})"] = hasil_prediksi_pemantauan
        data_prodi.rename(columns={'current_students': f'{input_last_year_data} (Saat Ini)'}, inplace=True)

    elif input_kriteria == "Persentase Penurunan":
        # if f"{input_last_year_data} (Prediksi)" not in data_prodi.columns:
        #     st.error(f"Kolom {input_last_year_data} (Prediksi) tidak ditemukan dalam data.")
        #     return None
        
        persentase_penurunan = hitung_persentase_penurunan(data_prodi, input_predict_year, input_banyak_data_ts)
        ambang_batas_jumlah_mahasiswa = int(input_fields[list(input_fields.keys())[0]] * (1 - input_ambang_batas_persen / 100))
        hasil_prediksi_pemantauan = "Lolos" if persentase_penurunan < input_ambang_batas_persen else "Tidak Lolos"
        data_prodi["Persentase Penurunan"] = persentase_penurunan
        data_prodi["Ambang Batas Jumlah Mahasiswa"] = ambang_batas_jumlah_mahasiswa
        data_prodi["Hasil Prediksi Pemantauan"] = hasil_prediksi_pemantauan
        # data_prodi.rename(columns={'current_students': f'{input_last_year_data} (Saat Ini)'}, inplace=True)

    return data_prodi


# Tampilkan hasil prediksi dan penilaian jika tombol "Prediksi" ditekan
if st.button("Prediksi"):
    hasil_prediksi = prediksi_dan_penilaian(input_prodi, input_predict_year, input_last_year_data, input_years_to_predict, input_kriteria, input_ambang_batas_jumlah, input_ambang_batas_persen, input_fields)
    if hasil_prediksi is not None:
        st.write(hasil_prediksi)
    else:
        st.write("none")