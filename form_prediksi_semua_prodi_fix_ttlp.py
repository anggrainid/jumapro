import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pickle
import pandas as pd

# Halaman Prediksi Semua Prodi
st.title("Halaman Prediksi Semua Prodi Dengan Formula")

# Establishing a Google Sheets connection
conn = st.connection("gsheets", type=GSheetsConnection)

# Fetch data dhp = data history prediction
existing_dhp = conn.read(worksheet="Data Histori Prediksi Suatu Prodi", ttl=5)
existing_dhp = existing_dhp.dropna(how="all")

# Fetch data djm = data jumlah mahasiswa
existing_djm = conn.read(worksheet="Data Jumlah Mahasiswa")
existing_djm = existing_djm.dropna(how="all")

# Fetch existing formulas data
existing_formula = conn.read(worksheet="Rumus Pemantauan", usecols=list(range(7)), ttl=5)
existing_formula = existing_formula.dropna(how="all")

# Dropdown options for Lembaga
formula_options = existing_formula['Nama Rumus'].unique()

# Input fields
input_predict_year = st.number_input("Masukkan Tahun yang Ingin Diprediksi (ex: 2025) : ", min_value=2024)
input_last_year = input_predict_year - 1

input_years_to_predict = st.number_input("Masukkan Proyeksi Prediksi (Dalam Satuan Tahun) : ", min_value=1, max_value=10)

input_formula = st.radio("Formula yang Digunakan", ["Sudah Ada", "Baru"])

if input_formula == "Sudah Ada":
    input_existing_formula = st.selectbox("Pilih Rumus yang Digunakan : ", formula_options)
    selected_formula = existing_formula[existing_formula['Nama Rumus'] == input_existing_formula].iloc[0]

    input_kriteria = selected_formula["Kriteria"]
    if input_kriteria == "Persentase Penurunan":
        input_ambang_batas_persen = selected_formula["Ambang Batas (%)"]
        input_banyak_data_ts = selected_formula["Banyak Data TS"]
        input_ambang_batas_jumlah = None

    else:
        input_ambang_batas_jumlah = selected_formula["Ambang Batas (Jumlah)"]
        input_ambang_batas_persen = None

else:
    input_kriteria = st.radio("Kriteria", ["Jumlah Mahasiswa", "Persentase Penurunan"])
    if input_kriteria == "Persentase Penurunan":
        input_ambang_batas_persen = st.slider("Ambang Batas Persentase Maksimal (%)", min_value=1, max_value=100, step=1)
        input_banyak_data_ts = st.slider("Masukkan Banyak Tahun yang Dipakai untuk Persentase Penurunan : ", min_value=2, max_value=5, step=1)
        input_ambang_batas_jumlah = None
                
    else:
        input_ambang_batas_jumlah = st.number_input("Ambang Batas Jumlah Mahasiswa Minimal", min_value=1, step=1)
        input_ambang_batas_persen = None

model = pickle.load(open(r"D:\jumapro\next_year_students_prediction.sav", "rb"))

# Membuat kolom `current_students` untuk data tahun terakhir yang tersedia
existing_djm['current_students'] = existing_djm.get(str(input_last_year))

# Menghindari KeyError jika data tahun terakhir tidak ada
if existing_djm['current_students'].isnull().all():
    st.error(f"Data untuk tahun {input_last_year} tidak tersedia dalam dataset.")
else:
    current_students = existing_djm['current_students'].copy()

    tahun_tidak_lolos = f"Lebih dari {input_years_to_predict} Tahun ke Depan"  # Default value

    for i in range(1, input_years_to_predict + 1):
        next_year = input_last_year + i
        column_name = f'{next_year} (Prediksi)'

        # Lakukan prediksi menggunakan nilai di current_students
        existing_djm[column_name] = model.predict(current_students.values.reshape(-1, 1))
        existing_djm[column_name] = existing_djm[column_name].astype(int)

        # Gunakan hasil prediksi tahun ini sebagai current_students untuk prediksi tahun berikutnya
        current_students = existing_djm[column_name].copy()

        if tahun_tidak_lolos == f"Lebih dari {input_years_to_predict} Tahun ke Depan":  # Only update if no year has been set yet
            if input_kriteria == "Jumlah Mahasiswa":
                if existing_djm[column_name].min() < input_ambang_batas_jumlah:
                    tahun_tidak_lolos = next_year

            elif input_kriteria == "Persentase Penurunan":
                ambang_batas_jumlah_mahasiswa = int(existing_djm["current_students"] * (1 - input_ambang_batas_persen / 100))
                if existing_djm[column_name].min() < ambang_batas_jumlah_mahasiswa:
                    tahun_tidak_lolos = next_year

    def hitung_persentase_penurunan(data, predict_year):
        ts_1 = data[f"{predict_year} (Prediksi)"]
        ts_0 = data["current_students"]
        penurunan = (ts_0 - ts_1) / ts_1
        persentase_penurunan = penurunan * 100
        return persentase_penurunan

    def hitung_persentase_penurunan_lebih_dari_satu(data, predict_year, banyak_data_ts):
        total_penurunan = 0
        for i in range(int(banyak_data_ts) - 1):
            if i == 0:
                ts_1 = data[f"{predict_year} (Prediksi)"]
                ts_0 = data["current_students"]
            else:
                ts_1 = existing_djm[f"{input_last_year - i}"]
                ts_0 = existing_djm[f"{input_last_year - i + 1}"]

            penurunan = (ts_0 - ts_1) / ts_1
            total_penurunan += penurunan

        rata_rata_penurunan = total_penurunan / (banyak_data_ts - 1)
        persentase_penurunan = rata_rata_penurunan * 100
        return persentase_penurunan

    def prediksi_dan_penilaian(input_predict_year, input_last_year_data, input_years_to_predict, input_kriteria, input_ambang_batas_jumlah, input_ambang_batas_persen):

        if input_kriteria == "Jumlah Mahasiswa":
            existing_djm["Jumlah Mahasiswa Minimal"] = input_ambang_batas_jumlah
            existing_djm[f"Hasil Prediksi Pemantauan ({input_predict_year})"] = existing_djm.apply(
                lambda row: "Lolos" if row[f"{input_predict_year} (Prediksi)"] > input_ambang_batas_jumlah else "Tidak Lolos", axis=1)
            existing_djm["Tahun Tidak Lolos (Prediksi)"] = tahun_tidak_lolos

        elif input_kriteria == "Persentase Penurunan":
            if input_banyak_data_ts > 2:
                existing_djm["Hitung Persentase Penurunan"] = hitung_persentase_penurunan_lebih_dari_satu(existing_djm, input_predict_year, input_banyak_data_ts)
            else:
                existing_djm["Hitung Persentase Penurunan"] = hitung_persentase_penurunan(existing_djm, input_predict_year)

            existing_djm[f"Hasil Prediksi Pemantauan ({input_predict_year})"] = existing_djm.apply(
                lambda row: "Lolos" if row["Hitung Persentase Penurunan"] <= input_ambang_batas_persen else "Tidak Lolos", axis=1)
            existing_djm["Ambang Batas Jumlah Mahasiswa Minimal"] = existing_djm["current_students"] * (1 - input_ambang_batas_persen / 100)
            existing_djm["Tahun Tidak Lolos (Prediksi)"] = tahun_tidak_lolos

        return existing_djm

    if st.button("Prediksi"):
        hasil_prediksi = prediksi_dan_penilaian(input_predict_year, input_last_year, input_years_to_predict, input_kriteria, input_ambang_batas_jumlah, input_ambang_batas_persen)
        st.write(hasil_prediksi)
        st.success("Data berhasil ditambahkan ke worksheet!")