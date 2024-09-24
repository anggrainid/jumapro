#  Pemantauan Semua Prodi

# pages/Halaman_Pemantauan.py

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pickle

# Fungsi untuk menghitung persentase penurunan
def hitung_persentase_penurunan(ts_0, ts_1):
    if ts_1 == 0 or np.isnan(ts_1):
        return 0.0
    penurunan = (ts_0 - ts_1) / ts_1
    persentase_penurunan = penurunan * 100
    return round(persentase_penurunan, 2)

# Fungsi untuk rename kolom
def rename_kolom(existing_djm, input_predict_year, input_years_to_predict, input_banyak_data_ts):
    input_last_year = input_predict_year - 1
    
    # Data TS-i
    ts_columns = [f"{input_last_year - i} (TS-{i})" for i in range(1, input_banyak_data_ts)]
    
    # Data TS
    ts_columns.append(f"{input_last_year} (TS)")
    
    # Rename kolom
    rename_dict = {}
    for i, col in enumerate(existing_djm.columns[1:1 + input_banyak_data_ts]):
        rename_dict[col] = ts_columns[i]
    
    existing_djm = existing_djm.rename(columns=rename_dict)
    return existing_djm

# Memuat data dari existing_djm dan existing_formula
with open('existing_djm.pickle', 'rb') as handle:
    existing_djm = pickle.load(handle)

with open('existing_formula.pickle', 'rb') as handle:
    existing_formula = pickle.load(handle)

model = pickle.load(open("next_year_students_prediction.sav", "rb"))

# 1. Data preprocessing
existing_djm = existing_djm.dropna(how="all")
existing_djm = existing_djm.replace('#N/A ()', 0)
existing_formula = existing_formula.dropna(how="all")
existing_djm.columns = [str(i) for i in existing_djm.columns]

# Dropdown options for Lembaga
lembaga_options = existing_djm['Lembaga'].unique()

# 2. Input form untuk pemantauan
st.title('Halaman Pemantauan Jumlah Mahasiswa')

# Sidebar untuk filter
st.sidebar.header("Filter Pemantauan")

# Filter Program Studi
prodi_list = existing_djm['Prodi'].unique()
selected_prodi = st.sidebar.selectbox("Pilih Program Studi", prodi_list)

# Filter Tahun Pemantauan
year_columns = [col for col in existing_djm.columns if col.isdigit()]
min_year = int(min(year_columns))
max_year = int(max(year_columns))
selected_year = st.sidebar.selectbox("Pilih Tahun Pemantauan", list(range(min_year, max_year + 1)))

# 3. Rename kolom tahun sesuai permintaan
# Asumsikan input_predict_year adalah selected_year + 1 untuk pemantauan
input_predict_year = selected_year + 1  # Contoh, sesuaikan jika perlu
input_years_to_predict = 0  # Tidak digunakan di halaman pemantauan
input_banyak_data_ts = 2  # Minimal 2 data untuk persentase penurunan

existing_djm = rename_kolom(existing_djm, input_predict_year, input_years_to_predict, input_banyak_data_ts)

# 4. Filter data berdasarkan program studi dan tahun
df_filtered = existing_djm[existing_djm['Prodi'] == selected_prodi]

# Mengambil jumlah mahasiswa untuk tahun yang dipilih
jumlah_mahasiswa = df_filtered.iloc[0, 1]  # Kolom pertama setelah 'Prodi'

# Menampilkan tabel data
st.subheader(f"Data Jumlah Mahasiswa Program Studi: {selected_prodi} pada Tahun {selected_year}")
df_display = df_filtered[['Prodi', f"{selected_year} (TS)"]]
df_display.columns = ['Prodi', 'Jumlah Mahasiswa']
st.dataframe(df_display, use_container_width=True)

# Menghitung total mahasiswa sebenarnya
total_actual = df_display['Jumlah Mahasiswa'].sum()
st.write(f"**Total Mahasiswa Sebenarnya pada Tahun {selected_year}:** {total_actual}")

# Analisis Pemantauan
st.subheader("Analisis Pemantauan")

# Ambil formula yang relevan untuk lembaga dan prodi
lembaga_name = existing_djm.loc[existing_djm['Prodi'] == selected_prodi, 'Lembaga'].values[0]

selected_formula = existing_formula[
    (existing_formula['Nama Rumus'] == 'Formula1') & (existing_formula['Lembaga'] == lembaga_name)
].iloc[0]

input_kriteria = selected_formula["Kriteria"]
input_ambang_batas_jumlah = selected_formula["Ambang Batas (Jumlah)"]
input_ambang_batas_persen = selected_formula.get("Ambang Batas (%)", None)  # Optional

# Evaluasi Kriteria
if input_kriteria == "Jumlah Mahasiswa":
    hasil = "Lolos" if jumlah_mahasiswa >= input_ambang_batas_jumlah else "Tidak Lolos"
    st.write(f"**Hasil Pemantauan:** {hasil}")
elif input_kriteria == "Persentase Penurunan":
    previous_year = selected_year - 1
    if previous_year >= min_year:
        jumlah_mahasiswa_prev = existing_djm.loc[existing_djm['Prodi'] == selected_prodi, f"{previous_year} (TS-1)"].values[0]
        persentase_penurunan = hitung_persentase_penurunan(jumlah_mahasiswa, jumlah_mahasiswa_prev)
        st.write(f"**Persentase Penurunan dari Tahun {previous_year} ke Tahun {selected_year}:** {persentase_penurunan}%")
        
        hasil = "Lolos" if persentase_penurunan <= input_ambang_batas_persen else "Tidak Lolos"
        st.write(f"**Hasil Pemantauan:** {hasil}")
    else:
        st.write("**Tidak ada data tahun sebelumnya untuk menghitung persentase penurunan.**")

# Grafik Jumlah Mahasiswa per Tahun
st.subheader("Grafik Jumlah Mahasiswa per Tahun")

# Ekstrak data untuk grafik
prodi_data = existing_djm[existing_djm['Prodi'] == selected_prodi]
years = [int(col.split()[0]) for col in prodi_data.columns if col.startswith(str(selected_year - 1)) or col.startswith(str(selected_year))]
jumlah_mahasiswa_list = prodi_data.loc[:, prodi_data.columns.isdigit()].values.flatten().astype(int).tolist()

# Membuat garis tren
if len(years) >= 2:
    z = np.polyfit(years, jumlah_mahasiswa_list, 1)
    p = np.poly1d(z)
    garis_tren = p(years)
else:
    garis_tren = [jumlah_mahasiswa_list[0]] * len(years)  # Tidak bisa menghitung tren dengan kurang dari 2 data

plt.figure(figsize=(10, 6))
plt.plot(years, jumlah_mahasiswa_list, label='Mahasiswa Sebenarnya', marker='o', color='blue')

if len(years) >= 2:
    plt.plot(years, garis_tren, color='green', linestyle='--', label='Garis Tren')

plt.legend()
plt.xlabel('Tahun')
plt.ylabel('Jumlah Mahasiswa')
plt.title(f'Trend Jumlah Mahasiswa di {selected_prodi} ({min_year} - {max_year})')
plt.grid(True)
st.pyplot(plt)
