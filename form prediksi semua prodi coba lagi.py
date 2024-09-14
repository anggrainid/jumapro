import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pickle
import pandas as pd

# Halaman Prediksi Suatu Prodi
st.title("Halaman Prediksi Semua Prodi Dengan Formula")

# Establishing a Google Sheets connection
conn = st.connection("gsheets", type=GSheetsConnection)

# Fetch data dhp = data history prediction
existing_dhp = conn.read(worksheet="Data Histori Prediksi Suatu Prodi", ttl=5)
existing_dhp = existing_dhp.dropna(how="all")

# Fetch data djm = data jumlah mahasiswa
existing_djm = conn.read(worksheet="Data Jumlah Mahasiswa")
existing_djm = existing_djm.dropna(how="all")
existing_djm = existing_djm.replace('#N/A ()', 0)

# Fetch existing formulas data
existing_formula = conn.read(worksheet="Rumus Pemantauan", usecols=list(range(7)), ttl=5)
existing_formula = existing_formula.dropna(how="all")

# Dropdown options for Lembaga
formula_options = existing_formula['Nama Rumus'].unique()

# Input fields
input_prodi = existing_djm["Prodi"]

input_predict_year = st.number_input("Masukkan Tahun yang Ingin Diprediksi (ex: 2025) : ", min_value=2024)
input_last_year = input_predict_year - 1

input_years_to_predict = st.number_input("Masukkan Proyeksi Prediksi (Dalam Satuan Tahun) : ", min_value=1, max_value=10)

input_formula = st.radio("Formula yang Digunakan", ["Sudah Ada", "Baru"])

if input_formula == "Sudah Ada":
    input_existing_formula = st.selectbox("Pilih Rumus yang Digunakan : ", formula_options)
    selected_formula = existing_formula[existing_formula['Nama Rumus'] == input_existing_formula].iloc[0]
    st.write(selected_formula)

    input_kriteria = selected_formula["Kriteria"]
    if input_kriteria == "Persentase Penurunan":
        input_ambang_batas_persen = selected_formula["Ambang Batas (%)"]
        input_banyak_data_ts = selected_formula["Banyak Data TS"]
        input_ambang_batas_jumlah = None
        input_fields = {}

        for i in range(int(input_banyak_data_ts - 1)):
            field_name = f"input_jumlah_mahasiswa_ts{i}"
            input_fields[field_name] = existing_djm[input_predict_year - 1]

    else:
        input_ambang_batas_jumlah = selected_formula["Ambang Batas (Jumlah)"]
        input_jumlah_mahasiswa_ts = existing_djm[input_predict_year - 1]
        input_ambang_batas_persen = None
        input_fields = None

else:
    input_kriteria = st.radio("Kriteria", ["Jumlah Mahasiswa", "Persentase Penurunan"])
    if input_kriteria == "Persentase Penurunan":
        input_ambang_batas_persen = st.slider("Ambang Batas Persentase Maksimal (%)", min_value=1, max_value=100, step=1)
        input_banyak_data_ts = st.slider("Masukkan Banyak Tahun yang Dipakai untuk Persentase Penurunan : ", min_value=2, max_value=5, step=1)
        input_ambang_batas_jumlah = None
        input_fields = {}

        for i in range(input_banyak_data_ts - 1):
            field_name = f"input_jumlah_mahasiswa_ts{i}"
            input_fields[field_name] = existing_djm[input_predict_year - 1]

    else:
        input_ambang_batas_jumlah = st.number_input("Ambang Batas Jumlah Mahasiswa Minimal", min_value=1, step=1)
        input_jumlah_mahasiswa_ts = existing_djm[input_predict_year - 1]
        input_ambang_batas_persen = None
        input_fields = None

model = pickle.load(open(r"D:\jumapro\next_year_students_prediction.sav", "rb"))

existing_djm.rename(columns={input_last_year: "current_students"}, inplace=True)

def hitung_persentase_penurunan(data, predict_year):
    ts_1 = data[f"{predict_year} (Prediksi)"]
    ts_0 = data["current_students"]
    penurunan = (ts_0 - ts_1) / ts_0
    persentase_penurunan = penurunan * 100
    return persentase_penurunan

def hitung_persentase_penurunan_lebih_dari_satu(data, predict_year, banyak_data_ts):
    total_penurunan = 0

    for i in range(int(banyak_data_ts) - 1):
        if i == 0:
            ts_1 = data[f"{predict_year} (Prediksi)"]
            ts_0 = data["current_students"]
        else:
            ts_1 = input_fields[f"input_jumlah_mahasiswa_ts{i-1}"]
            ts_0 = input_fields[f"input_jumlah_mahasiswa_ts{i}"]

        penurunan = (ts_0 - ts_1) / ts_0
        total_penurunan += penurunan

    rata_rata_penurunan = total_penurunan / (banyak_data_ts - 1)
    persentase_penurunan = rata_rata_penurunan * 100
    return persentase_penurunan

def prediksi_dan_penilaian(existing_djm, input_predict_year, input_years_to_predict, input_kriteria, input_ambang_batas_jumlah, input_ambang_batas_persen, input_fields):
    for index, row in existing_djm.iterrows():
        current_students = row['current_students']
        tahun_tidak_lolos = f"Lebih dari {input_years_to_predict} Tahun ke Depan"

        for i in range(1, input_years_to_predict + 1):
            next_year = input_predict_year + i
            column_name = f'{next_year} (Prediksi)'

            prediksi_mahasiswa = model.predict([[current_students]])[0]
            existing_djm.at[index, column_name] = int(prediksi_mahasiswa)
            current_students = prediksi_mahasiswa

            if input_kriteria == "Jumlah Mahasiswa" and prediksi_mahasiswa < input_ambang_batas_jumlah:
                tahun_tidak_lolos = next_year

            elif input_kriteria == "Persentase Penurunan":
                ambang_batas_jumlah_mahasiswa = int(row["current_students"] * (1 - input_ambang_batas_persen / 100))
                if prediksi_mahasiswa < ambang_batas_jumlah_mahasiswa:
                    tahun_tidak_lolos = next_year

        if input_kriteria == "Jumlah Mahasiswa":
            hasil_prediksi_pemantauan = "Lolos" if current_students >= input_ambang_batas_jumlah else "Tidak Lolos"
            existing_djm.at[index, f"Hasil Prediksi Pemantauan ({input_predict_year})"] = hasil_prediksi_pemantauan

        elif input_kriteria == "Persentase Penurunan":
            if input_banyak_data_ts > 2:
                persentase_penurunan = hitung_persentase_penurunan_lebih_dari_satu(existing_djm, input_predict_year, input_banyak_data_ts)
            else:
                persentase_penurunan = hitung_persentase_penurunan(existing_djm, input_predict_year)

            convert_percent_to_ambang_batas_jumlah_mahasiswa = int(row["current_students"] * (1 - input_ambang_batas_persen / 100))
            hasil_prediksi_pemantauan = "Lolos" if persentase_penurunan <= input_ambang_batas_persen else "Tidak Lolos"

            existing_djm.at[index, "Persentase Penurunan Maksimal"] = f"{input_ambang_batas_persen}%"
            existing_djm.at[index, "Ambang Batas Jumlah Mahasiswa Minimal"] = convert_percent_to_ambang_batas_jumlah_mahasiswa
            existing_djm.at[index, f"Hasil Prediksi Pemantauan ({input_predict_year})"] = hasil_prediksi_pemantauan

    return existing_djm

if st.button("Prediksi"):
    hasil_prediksi = prediksi_dan_penilaian(existing_djm, input_predict_year, input_years_to_predict, input_kriteria, input_ambang_batas_jumlah, input_ambang_batas_persen, input_fields)
    st.write(hasil_prediksi)