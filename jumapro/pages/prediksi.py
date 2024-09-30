# pages/prediksi.py
import streamlit as st
from data.gsheets import read_worksheet, update_worksheet
import pandas as pd
import pickle
import math
from datetime import date

# Fungsi Formula Pemantauan
def formula():
    st.markdown("Masukkan Rumus Baru di Bawah Ini")

    existing_data = read_worksheet("Rumus Pemantauan", usecols=list(range(7)))
    existing_data = existing_data.dropna(how="all")
    st.write(existing_data)

    existing_djm = read_worksheet("Data Jumlah Mahasiswa")
    existing_djm = existing_djm.dropna(how="all")
    existing_djm = existing_djm.replace('#N/A ()', 0)

    unused_columns = ['Kode Prodi', 'Kode Prodi UGM', 'Kode Fakultas', 'Departemen', 'Kluster']
    existing_djm = existing_djm.drop(unused_columns, axis=1, errors='ignore')

    lembaga_options = existing_djm['Lembaga'].unique()

    input_lembaga = st.selectbox("Pilih Lembaga : ", lembaga_options)
    input_nama_rumus = st.text_input("Masukkan Nama Rumus (ex: PEMPT) :")
    input_kriteria = st.radio("Kriteria", ["Persentase Penurunan", "Jumlah Mahasiswa"])

    if input_kriteria == "Persentase Penurunan":
        input_ambang_batas_persen = st.slider("Ambang Batas Persentase Penurunan Maksimal (%)", 0, 100, 5)
        input_banyak_data_ts = st.slider("Masukkan Banyak Tahun yang Dipakai untuk Persentase Penurunan : ", min_value=2, max_value=5, step=1)
        input_ambang_batas_jumlah = None
    else:
        input_ambang_batas_jumlah = st.number_input("Ambang Batas Jumlah Mahasiswa Minimal", min_value=1, step=1)
        input_ambang_batas_persen = None
        input_banyak_data_ts = None

    input_tanggal_mulai = st.date_input("Tanggal Mulai Berlaku", value=pd.to_datetime("today"))
    input_keterangan = st.text_area("Keterangan")

    if st.button("Tambah Rumus"):
        if not input_lembaga or not input_nama_rumus:
            st.warning("Pastikan semua field wajib diisi.")
            st.stop()
        elif existing_data["Nama Rumus"].str.contains(input_nama_rumus).any():
            st.warning("Rumus dengan nama ini sudah ada.")
            st.stop()
        else:
            new_data = pd.DataFrame(
                [{
                    "Lembaga": input_lembaga,
                    "Nama Rumus": input_nama_rumus,
                    "Kriteria": input_kriteria,
                    "Banyak Data TS": input_banyak_data_ts,
                    "Ambang Batas (%)": input_ambang_batas_persen,
                    "Ambang Batas (Jumlah)": input_ambang_batas_jumlah,
                    "Tanggal Mulai Berlaku": input_tanggal_mulai,
                    "Keterangan": input_keterangan
                }]
            )

            updated_df = pd.concat([existing_data, new_data], ignore_index=True)
            update_worksheet("Rumus Pemantauan", updated_df)

            st.success("Rumus berhasil ditambahkan!")
            st.write(updated_df)

# Fungsi Pemantauan Satu Prodi
def pemantauan_satu_prodi():
    st.markdown("Form Pemantauan Suatu Program Studi")

    existing_formula = read_worksheet("Rumus Pemantauan")
    existing_formula = existing_formula.dropna(how="all")

    input_prodi = st.text_input("Masukkan Nama Program Studi : ")

    input_current_year = st.number_input(
        "Masukkan Tahun Sekarang (ex: 2024) : ", 
        min_value=1900, 
        max_value=2100, 
        value=2024
    )

    formula_options = existing_formula['Nama Rumus'].unique()
    input_existing_formula = st.selectbox("Pilih Rumus yang Digunakan : ", formula_options)

    selected_formula = existing_formula[existing_formula['Nama Rumus'] == input_existing_formula].iloc[0]
    st.write("**Detail Formula yang Dipilih:**")
    st.write(selected_formula)

    input_kriteria = selected_formula["Kriteria"]

    if input_kriteria == "Persentase Penurunan":
        input_ambang_batas_persen = selected_formula["Ambang Batas (%)"]
        input_banyak_data_ts = int(selected_formula["Banyak Data TS"])
        input_ambang_batas_jumlah = None

        st.subheader("Masukkan Jumlah Mahasiswa untuk Hitung Persentase Penurunan:")
        input_fields = {}
        ts_years = []
        for i in range(input_banyak_data_ts):
            year = input_current_year - i
            label = f"Masukkan Jumlah Mahasiswa Tahun {year} (TS-{i}) : "
            input_fields[f"input_jumlah_mahasiswa_ts{i}"] = st.number_input(label, value=0)
            ts_years.append(input_fields[f"input_jumlah_mahasiswa_ts{i}"])
    else:
        input_ambang_batas_jumlah = int(selected_formula["Ambang Batas (Jumlah)"])
        input_jumlah_mahasiswa_ts = st.number_input(
            f"Masukkan Jumlah Mahasiswa Tahun {input_current_year} (TS-0) : ", 
            value=0
        )
        input_ambang_batas_persen = None
        input_banyak_data_ts = None
        input_fields = None

    input_model = st.file_uploader("Upload Model (.sav)", type=["sav"])
    if input_model is not None:
        model = pickle.load(input_model)

    if st.button("Hitung Pemantauan"):
        if not input_prodi:
            st.error("Nama Program Studi harus diisi.")
            return

        if input_kriteria == "Persentase Penurunan":
            ts_values = ts_years
            persentase_penurunan = calculate_persentase_penurunan(ts_values)
            hasil_prediksi_pemantauan = "Lolos" if persentase_penurunan <= input_ambang_batas_persen else "Tidak Lolos"

            ts1 = ts_values[1] if len(ts_values) > 1 else 0
            ambang_batas_jumlah_mahasiswa = math.ceil(ts1 / (1 + input_ambang_batas_persen / 100))

            data_prodi = pd.DataFrame({
                'Prodi': [input_prodi],
                'Hitung Persentase Penurunan': [f"{persentase_penurunan}%"],
                'Persentase Penurunan Maksimal': [f"{input_ambang_batas_persen}%"],
                'Hitung Jumlah Mahasiswa Minimal': [ambang_batas_jumlah_mahasiswa],
                f'Hasil Pemantauan ({input_current_year})': [hasil_prediksi_pemantauan],
                'Tanggal Pemantauan': [date.today()]
            })

            st.success("Pemantauan Berhasil Dilakukan!")
            st.write("**Hasil Pemantauan:**")
            st.table(data_prodi)

        elif input_kriteria == "Jumlah Mahasiswa":
            current_students = input_jumlah_mahasiswa_ts
            hasil_prediksi_pemantauan = "Lolos" if current_students >= input_ambang_batas_jumlah else "Tidak Lolos"

            data_prodi = pd.DataFrame({
                'Prodi': [input_prodi],
                'Jumlah Mahasiswa Minimal': [input_ambang_batas_jumlah],
                f'Hasil Pemantauan ({input_current_year})': [hasil_prediksi_pemantauan],
                'Tanggal Pemantauan': [date.today()]
            })

            st.success("Pemantauan Berhasil Dilakukan!")
            st.write("**Hasil Pemantauan:**")
            st.table(data_prodi)

def calculate_persentase_penurunan(ts_values):
    total_penurunan = 0
    valid_years = 0

    for i in range(1, len(ts_values)):
        ts_current = ts_values[i]
        ts_previous = ts_values[i - 1]

        if ts_current == 0 or pd.isna(ts_current) or (ts_current is None):
            return 0.0

        penurunan = (ts_previous - ts_current) / ts_current
        total_penurunan += penurunan
        valid_years += 1

    if valid_years == 0:
        return 0.0

    rata_rata_penurunan = total_penurunan / valid_years
    persentase_penurunan = rata_rata_penurunan * 100
    return round(-persentase_penurunan, 2)

# Fungsi Pemantauan Semua Prodi
def pemantauan_semua_prodi():
    st.markdown("Form Pemantauan Semua Program Studi")
    # Implementasi sesuai dengan fungsionalitas sebelumnya
    st.write("Fungsi Pemantauan Semua Prodi belum diimplementasikan.")

# Fungsi Kalkulator Prediksi
def kalkulator_prediksi():
    st.markdown("Kalkulator Prediksi Jumlah Mahasiswa")
    # Implementasi sesuai dengan fungsionalitas sebelumnya
    st.write("Fungsi Kalkulator Prediksi belum diimplementasikan.")

# Fungsi Prediksi Pemantauan Satu Prodi
def prediksi_pemantauan_satu_prodi():
    st.markdown("Form Prediksi Pemantauan Suatu Program Studi")
    # Implementasi sesuai dengan fungsionalitas sebelumnya
    st.write("Fungsi Prediksi Pemantauan Satu Prodi belum diimplementasikan.")

# Fungsi Prediksi Pemantauan Semua Prodi
def prediksi_pemantauan_semua_prodi():
    st.markdown("Form Prediksi Pemantauan Semua Program Studi")
    # Implementasi sesuai dengan fungsionalitas sebelumnya
    st.write("Fungsi Prediksi Pemantauan Semua Prodi belum diimplementasikan.")
