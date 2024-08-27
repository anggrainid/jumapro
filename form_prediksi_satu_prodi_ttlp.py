import streamlit as st
import pickle
import pandas as pd

# Halaman Prediksi Suatu Prodi
st.title("Halaman Prediksi Suatu Prodi")

# Input fields
input_prodi = st.text_input("Masukkan Nama Program Studi : ")

input_predict_year = st.number_input("Masukkan Tahun yang Ingin Diprediksi (ex: 2025) : ", min_value=2024)
input_last_year = input_predict_year - 1

input_years_to_predict = st.number_input("Masukkan Proyeksi Prediksi (Dalam Satuan Tahun) : ", min_value=1, max_value=10)

input_kriteria = st.radio("Kriteria", ["Jumlah Minimal", "Persentase Penurunan"])

if input_kriteria == "Persentase Penurunan":
    input_ambang_batas_persen = st.number_input("Ambang Batas Persentase Maksimal (%)", min_value=1, max_value=100, step=1)
    input_banyak_data_ts = st.number_input("Masukkan Banyak Tahun yang Dipakai untuk Persentase Penurunan : ", min_value=2, max_value=5, step=1)
    input_ambang_batas_jumlah = None

    input_fields = {}
    for i in range(input_banyak_data_ts - 1):
        field_name = f"input_jumlah_mahasiswa_ts{i}"
        input_fields[field_name] = st.number_input(f"Masukkan Jumlah Mahasiswa TS-{i}:", value=0)

else:
    input_ambang_batas_jumlah = st.number_input("Ambang Batas Jumlah Mahasiswa Minimal", min_value=1, step=1)
    input_jumlah_mahasiswa_ts = st.number_input(f"Masukkan Jumlah Mahasiswa TS:", value=0)
    input_ambang_batas_persen = None
    input_fields = None

model = pickle.load(open(r"D:\jumapro\next_year_students_prediction.sav", "rb"))

# Membuat DataFrame berdasarkan kriteria
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

# Prediksi beberapa tahun ke depan dan cek kapan prodi tidak lolos pemantauan
current_students = data_prodi['current_students'].copy()
tahun_tidak_lolos = "Lebih dari {input_years_to_predict} tahun ke depan"
for i in range(1, input_years_to_predict + 1):
    next_year = input_last_year + i
    column_name = f'{next_year} (Prediksi)'
    data_prodi[column_name] = model.predict(current_students.values.reshape(-1, 1))
    data_prodi[column_name] = data_prodi[column_name].astype(int)
    
    # Cek apakah prodi tidak lolos pemantauan
    if input_kriteria == "Jumlah Minimal":
        if data_prodi[column_name].values[0] < input_ambang_batas_jumlah:
            tahun_tidak_lolos = next_year
            break
    elif input_kriteria == "Persentase Penurunan":
        ambang_batas_jumlah_mahasiswa = int(data_prodi["current_students"].values[0] * (1 - input_ambang_batas_persen / 100))
        if data_prodi[column_name].values[0] < ambang_batas_jumlah_mahasiswa:
            tahun_tidak_lolos = next_year
            break
    
    current_students = data_prodi[column_name].copy()

# Tambahkan kolom "Tahun Tidak Lolos (Prediksi)"
data_prodi["Tahun Tidak Lolos (Prediksi)"] = tahun_tidak_lolos

# Fungsi untuk menghitung persentase penurunan
def hitung_persentase_penurunan(data, predict_year):
    ts_1 = data[f"{predict_year} (Prediksi)"]
    ts_0 = data["current_students"]
    penurunan = (ts_0 - ts_1) / ts_1
    persentase_penurunan = penurunan * 100
    return persentase_penurunan

# Fungsi untuk menghitung persentase penurunan dengan lebih dari satu tahun data
def hitung_persentase_penurunan_lebih_dari_satu(data, predict_year, banyak_data_ts):
    total_penurunan = 0
    for i in range(banyak_data_ts - 1):
        if i == 0:
            ts_1 = data[f"{predict_year} (Prediksi)"]
            ts_0 = data["current_students"]
        else:
            ts_1 = input_fields[f"input_jumlah_mahasiswa_ts{i-1}"]
            ts_0 = input_fields[f"input_jumlah_mahasiswa_ts{i}"]

        penurunan = (ts_0 - ts_1) / ts_1
        total_penurunan += penurunan

    rata_rata_penurunan = total_penurunan / (banyak_data_ts - 1)
    persentase_penurunan = rata_rata_penurunan * 100
    return persentase_penurunan

# Fungsi untuk prediksi dan penilaian
def prediksi_dan_penilaian(data_prodi, input_predict_year, input_last_year, input_years_to_predict, input_kriteria, input_ambang_batas_jumlah, input_ambang_batas_persen, input_fields):
    if input_kriteria == "Jumlah Minimal":
        hasil_prediksi_pemantauan = "Lolos" if data_prodi[f"{input_predict_year} (Prediksi)"].values[0] > input_ambang_batas_jumlah else "Tidak Lolos"
        data_prodi[f"Hasil Prediksi Pemantauan ({input_predict_year})"] = hasil_prediksi_pemantauan
        data_prodi.rename(columns={'current_students': f'{input_last_year} (Saat Ini)'}, inplace=True)
    elif input_kriteria == "Persentase Penurunan":
        if input_banyak_data_ts > 2:
            persentase_penurunan = hitung_persentase_penurunan_lebih_dari_satu(data_prodi, input_predict_year, input_banyak_data_ts)
        else:
            persentase_penurunan = hitung_persentase_penurunan(data_prodi, input_predict_year)
        
        ambang_batas_jumlah_mahasiswa = int(data_prodi["current_students"].values[0] * (1 - input_ambang_batas_persen / 100))
        hasil_prediksi_pemantauan = "Lolos" if persentase_penurunan.values[0] < input_ambang_batas_persen else "Tidak Lolos"
        data_prodi["Persentase Penurunan"] = persentase_penurunan
        data_prodi["Ambang Batas Jumlah Mahasiswa"] = ambang_batas_jumlah_mahasiswa
        data_prodi["Hasil Prediksi Pemantauan"] = hasil_prediksi_pemantauan
        data_prodi.rename(columns={'current_students': f'{input_last_year} (Saat Ini)'}, inplace=True)
    return data_prodi

# Tampilkan hasil prediksi dan penilaian jika tombol "Prediksi" ditekan
if st.button("Prediksi"):
    hasil_prediksi = prediksi_dan_penilaian(data_prodi, input_predict_year, input_last_year, input_years_to_predict, input_kriteria, input_ambang_batas_jumlah, input_ambang_batas_persen, input_fields)
    st.write(hasil_prediksi)