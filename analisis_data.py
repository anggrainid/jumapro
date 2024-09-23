#eksplorasi data analisis thd jumlah mahasiswa per prodi

import streamlit as st
import pandas as pd
# import plotly.express as px
from streamlit_gsheets import GSheetsConnection
import pickle
import re
import matplotlib.pyplot as plt




# Buat koneksi ke Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Baca data dari Google Sheets
data = conn.read()

last_column_name = data.columns[-1]

# Hapus kolom yang tidak digunakan, kecuali yang diperlukan untuk filter
unused_column = ['Kode Prodi', 'Kode Prodi UGM', 'Kode Fakultas', 'BAN PT', 'Departemen', 'Kluster', 'PDDIKTI x BAN']
data = data.drop(unused_column, axis=1)
data = data

# Pastikan kolom yang diperlukan ada
required_columns = ['Program Studi', 'Fakultas', 'Jenjang', 'Lembaga']
missing_columns = [col for col in required_columns if col not in data.columns]
if missing_columns:
    st.error(f"Kolom berikut hilang dari data: {', '.join(missing_columns)}")
    st.stop()

# Load model dari file .sav
model = pickle.load(open(r"D:\jumapro\next_year_students_prediction.sav", "rb"))

# Assuming `data` is already loaded from Google Sheets
# Apply filters
filtered_data = data.copy()

# Hapus baris dengan NaN di kolom "Program Studi"
filtered_data = filtered_data.dropna(subset=["Program Studi"])
# Multi-select for specific programs with default as "All"
prodi_options = ["All"] + filtered_data["Program Studi"].unique().tolist()
selected_prodi = st.multiselect("Pilih Program Studi", prodi_options, default="All")

if "All" in selected_prodi:
    selected_prodi = filtered_data["Program Studi"].unique().tolist()

# Filter data based on selected programs
filtered_data = filtered_data[filtered_data["Program Studi"].isin(selected_prodi)]

# Extract years columns for line chart
years = [col for col in filtered_data.columns if re.match(r'\d+', str(col))]

# Plot line chart
st.write("Tren Jumlah Mahasiswa per Prodi Setiap Tahun")
fig, ax = plt.subplots(figsize=(10, 6))

for prodi in selected_prodi:
    prodi_data = filtered_data[filtered_data["Program Studi"] == prodi]
    
        # Cek apakah data untuk prodi tersebut kosong
    if not prodi_data[years].empty:
        ax.plot(years, prodi_data[years].values.flatten(), marker='o', label=prodi)
    else:
        st.warning(f"Tidak ada data untuk Program Studi: {prodi}")

    # ax.plot(years, prodi_data[years].values.flatten(), marker='o', label=prodi)

# ax.set_xlabel("Tahun")
# ax.set_ylabel("Jumlah Mahasiswa")
# ax.set_title("Tren Jumlah Mahasiswa per Program Studi")
# ax.legend()
# st.pyplot(fig)

ax.set_xlabel("Tahun")
ax.set_ylabel("Jumlah Mahasiswa")
ax.set_title("Tren Jumlah Mahasiswa per Program Studi")
ax.legend()
st.pyplot(fig)