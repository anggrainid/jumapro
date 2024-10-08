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
    input_banyak_tahun_pp = st.number_input("Masukkan Banyak Tahun yang Dipakai untuk Persentase Penurunan : ", min_value=2, max_value=5, step=1)
    input_ambang_batas_jumlah = None

    input_fields = {}
    field_name = f"input_jumlah_mahasiswa_ts"
    input_fields[field_name] = st.number_input(f"Masukkan Jumlah Mahasiswa TS (Tahun Sekarang):", value=0)

    if input_banyak_tahun_pp > 2:
        for i in range(1, input_banyak_tahun_pp):
            field_name = f"input_jumlah_mahasiswa_ts{i}"
            input_fields[field_name] = st.number_input(f"Masukkan Jumlah Mahasiswa TS-{i}:", value=0)

else:
    input_ambang_batas_jumlah = st.number_input("Ambang Batas Jumlah Mahasiswa Minimal", min_value=1, step=1)
    input_jumlah_mahasiswa_ts = st.number_input(f"Masukkan Jumlah Mahasiswa TS (Tahun Sekarang):", value=0)
    input_ambang_batas_persen = None
    input_fields = None

# Fungsi untuk menghitung persentase penurunan
def hitung_persentase_penurunan(data, predict_year):
    data_mahasiswa_start_year = input_fields["input_jumlah_mahasiswa_ts"]
    end_year = predict_year
    penurunan_total = (data[f"{end_year} (Prediksi)"] - data_mahasiswa_start_year)
    persentase_penurunan = (penurunan_total / data_mahasiswa_start_year) * 100
    return persentase_penurunan

# Fungsi untuk menghitung persentase penurunan dengan lebih dari satu tahun data
def hitung_persentase_penurunan_lebih_dari_satu(data, banyak_data_ts):
    total_penurunan = 0

    # Iterasi dari TS-1 hingga TS-n (n = banyak_data_ts)
    for i in range(banyak_data_ts - 1):
        ts_current = data[f"input_jumlah_mahasiswa_ts{i}"]
        ts_next = data[f"input_jumlah_mahasiswa_ts{i+1}"]
        penurunan = (ts_next - ts_current) / ts_current
        total_penurunan += penurunan

    # Hitung rata-rata penurunan
    rata_rata_penurunan = total_penurunan / (banyak_data_ts - 1)
    persentase_penurunan = rata_rata_penurunan * 100

    return persentase_penurunan

# Perbarui fungsi prediksi_dan_penilaian untuk menggunakan fungsi yang baru
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
        if input_banyak_tahun_pp > 2:
            persentase_penurunan = hitung_persentase_penurunan_lebih_dari_satu(input_fields, input_banyak_tahun_pp)
        else:
            persentase_penurunan = hitung_persentase_penurunan(data_prodi, input_predict_year)
        
        ambang_batas_jumlah_mahasiswa = int(input_fields[list(input_fields.keys())[0]] * (1 - input_ambang_batas_persen / 100))
        hasil_prediksi_pemantauan = "Lolos" if persentase_penurunan.values[0] < input_ambang_batas_persen else "Tidak Lolos"
        data_prodi["Persentase Penurunan"] = persentase_penurunan.values[0]
        data_prodi["Ambang Batas Jumlah Mahasiswa"] = ambang_batas_jumlah_mahasiswa
        data_prodi["Hasil Prediksi Pemantauan"] = hasil_prediksi_pemantauan

    return data_prodi

# Tampilkan hasil prediksi dan penilaian jika tombol "Prediksi" ditekan
if st.button("Prediksi"):
    hasil_prediksi = prediksi_dan_penilaian(input_prodi, input_predict_year, input_last_year, input_years_to_predict, input_kriteria, input_ambang_batas_jumlah, input_ambang_batas_persen, input_fields)
    st.write(hasil_prediksi)