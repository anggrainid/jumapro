import streamlit as st
import pickle
import pandas as pd
import numpy as np
from datetime import date
import math
from component.data import get_data, refresh_data, preprocess_data
from component.func import calculate_persentase_penurunan
# def load_data():
#     # Load existing data and formulas from pickle files
#     # with open('existing_djm.pickle', 'rb') as handle:
#     #     existing_djm = pickle.load(handle)
    
#     with open('existing_formula.pickle', 'rb') as handle:
#         existing_formula = pickle.load(handle)
    
#     return existing_formula

# def calculate_persentase_penurunan(ts_values):
#     """
#     Menghitung persentase penurunan berdasarkan data time series.
#     ts_values: List of jumlah mahasiswa dari tahun-tahun sebelumnya (TS-n, ..., TS-1, TS-0)
#     """
#     total_penurunan = 0
#     valid_years = 0
    
#     for i in range(1, len(ts_values)):
#         ts_current = ts_values[i]
#         ts_previous = ts_values[i - 1]
        
#         if ts_current == 0 or pd.isna(ts_current) or (ts_current is None):
#             return 0.0
        
#         penurunan = (ts_previous - ts_current) / ts_current
#         total_penurunan += penurunan
#         valid_years += 1
    
#     if valid_years == 0:
#         return 0.0
    
#     rata_rata_penurunan = total_penurunan / valid_years
#     persentase_penurunan = rata_rata_penurunan * 100
#     return round(-persentase_penurunan, 2)




def pemantauan_satu_prodi(existing_formula):
    # if st.button('Refresh Data'):
    #     existing_dhp = refresh_data('dhp')
    #     existing_formula = refresh_data('formula')
    #     st.success("Data berhasil dimuat ulang dari Google Sheets!")
    # else:
    # # 2. Connections from pickle
    #     existing_dhp = get_data('dhp')
    #     existing_formula = get_data('formula')
    # # st.write(existing_djm)
    #     # 3. Data preprocessing
    # existing_dhp = preprocess_data(existing_dhp)
    # existing_formula = preprocess_data(existing_formula)
    st.markdown("Form Pemantauan Program Studi")
    
    # Input Fields
    input_prodi = st.text_input("Masukkan Nama Program Studi : ")
    
    input_current_year = st.number_input(
        "Masukkan Tahun Sekarang (ex: 2024) : ", 
        min_value=1900, 
        max_value=2100, 
        value=2024
    )
    
    # Dropdown untuk memilih formula
    st.subheader("Pilih Formula Pemantauan")
    formula_options = existing_formula['Nama Rumus'].unique()
    input_existing_formula = st.selectbox("Pilih Rumus yang Digunakan : ", formula_options)
    
    # Mengambil baris formula yang dipilih
    selected_formula = existing_formula[existing_formula['Nama Rumus'] == input_existing_formula].iloc[0]
    st.write("**Detail Formula yang Dipilih:**")
    st.write(selected_formula)
    
    # Cek kriteria
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
        # st.subheader(f"Masukkan Jumlah Mahasiswa Tahun {input_current_year} (TS-0) : ")
        input_jumlah_mahasiswa_ts = st.number_input(
            f"Masukkan Jumlah Mahasiswa Tahun {input_current_year} (TS-0) : ", 
            value=0
        )
        input_fields = None
    
    # Tombol untuk melakukan pemantauan
    if st.button("Hitung Pemantauan"):
        if not input_prodi:
            st.error("Nama Program Studi harus diisi.")
            return
        
        if input_kriteria == "Persentase Penurunan":
            ts_values = ts_years
            persentase_penurunan = calculate_persentase_penurunan(ts_values)
            hasil_prediksi_pemantauan = "Lolos" if persentase_penurunan <= input_ambang_batas_persen else "Tidak Lolos"
            
            # Menghitung Ambang Batas Jumlah Mahasiswa Minimal
            # Ambang Batas Jumlah Mahasiswa Minimal = ceil(ts-1 / (1 + p_max / 100))
            ts1 = ts_values[1] if len(ts_values) > 1 else 0
            ambang_batas_jumlah_mahasiswa = math.ceil(ts1 / (1 + input_ambang_batas_persen / 100))
            
            # Membuat DataFrame hasil pemantauan
            data_prodi = pd.DataFrame({
                'Prodi': [input_prodi],
                'Hitung Persentase Penurunan': [f"{persentase_penurunan}%"],
                'Persentase Penurunan Maksimal': [f"{input_ambang_batas_persen}%"],
                'Hitung Jumlah Mahasiswa Minimal': [ambang_batas_jumlah_mahasiswa],
                f'Hasil Pemantauan ({input_current_year})': [hasil_prediksi_pemantauan],
                'Tanggal Pemantauan': [date.today()]
            })
            
            # Menampilkan hasil pemantauan
            st.success("Pemantauan Berhasil Dilakukan!")
            st.write("**Hasil Pemantauan:**")
            st.table(data_prodi)
        
        elif input_kriteria == "Jumlah Mahasiswa":
            current_students = input_jumlah_mahasiswa_ts
            hasil_prediksi_pemantauan = "Lolos" if current_students >= input_ambang_batas_jumlah else "Tidak Lolos"
            
            # Membuat DataFrame hasil pemantauan
            data_prodi = pd.DataFrame({
                'Prodi': [input_prodi],
                f'Jumlah Mahasiswa Minimal': [input_ambang_batas_jumlah],
                f'Hasil Pemantauan ({input_current_year})': [hasil_prediksi_pemantauan],
                'Tanggal Pemantauan': [date.today()]
            })
            
            # Menampilkan hasil pemantauan
            st.success("Pemantauan Berhasil Dilakukan!")
            st.write("**Hasil Pemantauan:**")
            st.table(data_prodi)


# def main():
#     # Load dan preprocess data
#     existing_formula = load_data()
    
#     # Buat form pemantauan
#     create_pemantauan_form(existing_formula)

# if __name__ == "__main__":
#     main()

# create_pemantauan_form()