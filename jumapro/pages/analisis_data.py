# pages/analisis_data.py
import streamlit as st
from data.gsheets import read_worksheet
import pandas as pd
import matplotlib.pyplot as plt

def analisis_data(existing_djm):
    prodi_options = existing_djm['Prodi'].unique()
    selected_prodi = st.selectbox("Pilih Program Studi", options=prodi_options)

    existing_djm = existing_djm.fillna(0)
    year_columns = [str(col) for col in existing_djm.columns if col.isdigit()]

    min_year = int(min(year_columns))
    max_year = int(max(year_columns))

    start_year, end_year = st.slider(
        "Pilih Rentang Tahun",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year)
    )

    filtered_data = existing_djm[existing_djm['Prodi'] == selected_prodi]
    filtered_years = [str(year) for year in range(start_year, end_year + 1)]
    available_years = [year for year in filtered_years if year in filtered_data.columns]

    if not available_years:
        st.warning("Tidak ada data untuk tahun yang dipilih.")
        return

    filtered_data = filtered_data[['Prodi'] + available_years]

    # Line Chart
    st.subheader("Line Chart: Jumlah Mahasiswa per Tahun")
    plt.figure(figsize=(10, 5))
    plt.plot(available_years, filtered_data.iloc[0, 1:].values, marker='o', label=selected_prodi)
    plt.title(f'Jumlah Mahasiswa {selected_prodi} (Tahun {start_year} - {end_year})')
    plt.xlabel('Tahun')
    plt.ylabel('Jumlah Mahasiswa')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.legend()
    st.pyplot(plt)

    # Bar Chart
    st.subheader("Bar Chart: Jumlah Mahasiswa per Tahun")
    plt.figure(figsize=(10, 5))
    plt.bar(available_years, filtered_data.iloc[0, 1:].values, color='skyblue')
    plt.title(f'Jumlah Mahasiswa {selected_prodi} (Tahun {start_year} - {end_year})')
    plt.xlabel('Tahun')
    plt.ylabel('Jumlah Mahasiswa')
    plt.xticks(rotation=45)
    st.pyplot(plt)

    # Display Table of Filtered Data
    st.subheader(f"Data Jumlah Mahasiswa {selected_prodi}")
    st.dataframe(filtered_data)
