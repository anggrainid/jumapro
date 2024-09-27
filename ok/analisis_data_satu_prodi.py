import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def analisis_data(existing_djm):
    # st.title("Analisis Data Historis Jumlah Mahasiswa")

    # Filter Program Studi
    prodi_options = existing_djm['Prodi'].unique()
    selected_prodi = st.selectbox("Pilih Program Studi", options=prodi_options)

    # Convert column names to string and filter columns that are numeric (representing years)
    year_columns = [str(col) for col in existing_djm.columns if str(col).isdigit()]

    # Handle NaN values (Replace NaN with 0 for simplicity)
    existing_djm = existing_djm.fillna(0)

    # Filter Tahun
    min_year = int(min(year_columns))
    max_year = int(max(year_columns))

    start_year = st.slider("Pilih Tahun Awal", min_value=min_year, max_value=max_year, value=min_year)
    end_year = st.slider("Pilih Tahun Akhir", min_value=start_year, max_value=max_year, value=max_year)

    # Filter data berdasarkan Prodi dan Tahun
    filtered_data = existing_djm[existing_djm['Prodi'] == selected_prodi].copy()

    # Generate a list of filtered years, ensuring all columns exist in the data
    filtered_years = [int(year) for year in range(start_year, end_year + 1)]
    
    # Pastikan kolom tahun yang ada benar-benar tersedia di dalam existing_djm
    available_years = [year for year in filtered_years if year in filtered_data.columns]
    
    if len(available_years) == 0:
        st.warning("Tidak ada data untuk tahun yang dipilih.")
        return

    # Filter data hanya pada kolom-kolom yang tersedia
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
