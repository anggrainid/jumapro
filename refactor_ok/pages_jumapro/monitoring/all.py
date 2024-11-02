import streamlit as st
# import pickle
import pandas as pd
# import numpy as np
import matplotlib.pyplot as plt
from datetime import date
import math
from component.data import get_data, refresh_data, preprocess_data, add_data
from component.func import calculate_persentase_penurunan, calculate_ts0_minimal

# def load_data():
#     """
#     Memuat data existing_djm dan existing_formula dari file pickle.
#     """
#     with open('existing_djm.pickle', 'rb') as handle:
#         existing_djm = pickle.load(handle)
    
#     with open('existing_formula.pickle', 'rb') as handle:
#         existing_formula = pickle.load(handle)
    
#     return existing_djm, existing_formula

# def preprocess_data(existing_djm, existing_formula):
#     """
#     Membersihkan data dengan menghapus baris yang kosong, mengganti nilai tertentu,
#     dan menghapus kolom yang tidak diperlukan.
#     """
#     # Drop rows where all elements are NaN
#     existing_djm = existing_djm.dropna(how="all")
#     existing_djm = existing_djm.replace('#N/A ()', 0)
#     existing_formula = existing_formula.dropna(how="all")
    
#     # Ubah nama kolom menjadi string
#     existing_djm.columns = [str(i) for i in existing_djm.columns]
    
#     # Menghapus kolom yang tidak diperlukan
#     unused_columns = ['Kode Prodi', 'Kode Prodi UGM', 'Kode Fakultas', 'Program Studi', 
#                       'BAN PT', 'Departemen', 'Kluster', 'PDDIKTI x BAN']
#     existing_djm = existing_djm.drop(unused_columns, axis=1, errors='ignore')
    
#     return existing_djm, existing_formula

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
#             return 0
        
#         penurunan = (ts_previous - ts_current) / ts_current
#         total_penurunan += penurunan
#         valid_years += 1
    
#     if valid_years == 0:
#         return 0
    
#     rata_rata_penurunan = total_penurunan / valid_years
#     persentase_penurunan = rata_rata_penurunan * 100
#     return round(-persentase_penurunan, 2)

def pemantauan_semua_prodi(existing_djm, existing_formula):

    st.title("Halaman Pemantauan Semua Program Studi")
    st.markdown("Halaman ini digunakan untuk melakukan pemantauan jumlah mahasiswa baru pada semua program studi yang tersedia")
    
    acc_columns = ['Peringkat', 'Awal Masa Berlaku', 'Akhir Masa Berlaku', 'Kadaluarsa']
    existing_djm = existing_djm.drop(acc_columns, axis=1, errors='ignore')
    st.write(existing_djm)

    def visualization_selected(hasil_df):
        # Filter Program Studi
        prodi_options = hasil_df['Prodi'].unique()
        selected_prodi = st.selectbox("Pilih Program Studi", options=prodi_options)
        st.write(hasil_df[hasil_df['Prodi'] == selected_prodi])
        filtered_data = hasil_df[hasil_df['Prodi'] == selected_prodi].iloc[0].copy()
        

        # Ambil data yang dibutuhkan
        ts_data = filtered_data['Jumlah Mahasiswa TS']
        # kriteria = filtered_data['Kriteria']
        ambang_batas = filtered_data['Konversi Jumlah Mahasiswa Minimal']
        banyak_data_ts = filtered_data['Banyak Data TS']
        
        # Grafik Scatter Plot
        plt.figure(figsize=(10, 6))
        years = list(range(current_year - int(banyak_data_ts) + 1,current_year + 1))
        plt.scatter(years,ts_data[::-1], color='blue', label='Jumlah Mahasiswa Baru')
        plt.plot(years, ts_data[::-1], color='orange', label='Trend')
        plt.axhline(y=ambang_batas, color='red', linestyle='--', label='Ambang Batas Jumlah Mahasiswa Baru Minimal')
        plt.title('Jumlah Mahasiswa Baru Tahun ke Tahun')
        plt.xlabel('Tahun')
        plt.ylabel('Jumlah Mahasiswa Baru')
        plt.xticks(years)  # X-axis labels
        plt.legend()
        plt.grid()
        # prodi_banyak_data = prodi_formula["Banyak Data TS"]
        st.pyplot(plt)
    
    # 1. Connections from google sheets
    # if st.button('Refresh Data'):
    #     existing_djm = refresh_data('djm')
    #     existing_formula = refresh_data('formula')
    #     st.success("Data berhasil dimuat ulang dari Google Sheets!")
    # else:
    # # 2. Connections from pickle
    #     existing_djm = get_data('djm')
    #     existing_formula = get_data('formula')
    # # st.write(existing_djm)
    #     # 3. Data preprocessing
    # existing_djm = preprocess_data(existing_djm)
    # existing_formula = preprocess_data(existing_formula)

    existing_djm.columns = [str(i) for i in existing_djm.columns]


    """
    Membuat form pemantauan untuk semua prodi dan melakukan pemantauan berdasarkan data yang ada.
    """
    st.markdown("Form Pemantauan Semua Program Studi")
    
    # Menentukan Tahun Pemantauan
    available_years = [int(col) for col in existing_djm.columns if col.isdigit()]
    filtered_years = [year for year in available_years if year>min(available_years) + 4]
    if not filtered_years:
        st.error("Tidak ada data tahun yang tersedia di existing_djm.")
        return
    
    current_year_default = max(filtered_years)
    current_year = st.selectbox(
        "Pilih Tahun Pemantauan:",
        options=sorted(filtered_years),
        index=sorted(filtered_years).index(current_year_default) if filtered_years else 0
    )
    
    # Identifikasi semua lembaga
    lembaga_options = existing_djm['Lembaga'].unique()
    selected_formulas_lembaga = {}
    banyak_data_ts_lembaga = {}
    
    st.subheader("Pilih Formula Pemantauan untuk Setiap Lembaga")
    
    for lembaga_name in lembaga_options:
        st.write(f"### Lembaga: {lembaga_name}")
        
        # Filter formulas by the current lembaga
        formula_options = existing_formula[existing_formula['Lembaga'] == lembaga_name]['Nama Rumus'].unique()
        
        if len(formula_options) == 0:
            st.warning(f"Tidak ada formula yang tersedia untuk Lembaga {lembaga_name}.")
            selected_formulas_lembaga[lembaga_name] = "-"
            banyak_data_ts_lembaga[lembaga_name] = "-"
            continue
        
        # Dropdown to select formula for the current Lembaga
        selected_formulas_lembaga[lembaga_name] = st.selectbox(
            f"Pilih Rumus yang Digunakan bagi Prodi di bawah Lembaga {lembaga_name} : ",
            formula_options,
            key=f"formula_{lembaga_name}"
        )
        
        # Ambil nilai Banyak Data TS untuk lembaga terkait, handling NaN
        selected_formulas_name = existing_formula[
            (existing_formula['Nama Rumus'] == selected_formulas_lembaga[lembaga_name]) & 
            (existing_formula['Lembaga'] == lembaga_name)
        ].iloc[0]
        
        banyak_data_ts = selected_formulas_name['Banyak Data TS']
        if pd.isna(banyak_data_ts):
            banyak_data_ts_lembaga[lembaga_name] = "-"
        else:
            banyak_data_ts_lembaga[lembaga_name] = int(banyak_data_ts)
        
        st.write("**Detail Formula yang Dipilih:**")
        st.write(selected_formulas_name)
    
    # Tombol untuk melakukan pemantauan
    # if st.button("Hitung Pemantauan"):
    #     # Inisialisasi list untuk menyimpan hasil
    hasil_list = []

    
    
    # Iterasi melalui semua prodi
    for index, row in existing_djm.iterrows():
        prodi_name = row['Prodi']
        lembaga = row['Lembaga']
        jenjang = row['Jenjang']
        
        # # Cari formula yang sesuai dengan Lembaga
        # if lembaga not in selected_formulas_lembaga:
        #     st.warning(f"Formula tidak dipilih untuk Lembaga '{lembaga}'. Prodi '{prodi_name}' dilewati.")
        #     continue
        
        
        # if selected_formula_name == "-":
        #     st.warning(f"Tidak ada formula yang dipilih untuk Lembaga '{lembaga}'. Prodi '{prodi_name}' dilewati.")
        #     hasil_list.append({
        #         'Prodi': prodi_name,
        #         'Persentase Penurunan (%)': "-",
        #         'Persentase Penurunan Maksimal (%)': "-",
        #         'Ambang Batas Jumlah Mahasiswa Minimal': "-",
        #         f'Hasil Pemantauan ({current_year})': "-",
        #         'Tanggal Pemantauan': date.today(),
        #         'TS Data': "-"
        #     })
        #     continue
        
        selected_formula_name = selected_formulas_lembaga[lembaga]
        prodi_formula = existing_formula[
            (existing_formula['Nama Rumus'] == selected_formula_name) & 
            (existing_formula['Lembaga'] == lembaga)
        ]
        
        
        if prodi_formula.empty:
            st.warning(f"Formula '{selected_formula_name}' tidak ditemukan untuk Lembaga '{lembaga}'. Prodi '{prodi_name}' dilewati.")
            hasil_list.append({
                'Prodi': prodi_name,
                'Persentase Penurunan (%)': "-",
                'Persentase Penurunan Maksimal (%)': "-",
                'Ambang Batas Jumlah Mahasiswa Minimal': "-",
                f'Hasil Pemantauan ({current_year})': "-",
                'Tanggal Pemantauan': date.today(),
                'TS Data': "-"
            })
            continue
        
        prodi_formula = prodi_formula.iloc[0]
        prodi_kriteria = prodi_formula["Kriteria"]
        prodi_banyak_data = prodi_formula["Banyak Data TS"]
        prodi_ppm = prodi_formula["Ambang Batas (%)"]
        
        # Ambil Banyak Data TS
        banyak_data_ts = banyak_data_ts_lembaga[lembaga]
        ts_columns = []
        ts_values = []
        
        if banyak_data_ts != "-":
            for i in range(int(banyak_data_ts)):
                year = current_year - i
                ts_key = str(year)
                ts_value = row[ts_key] if ts_key in row else "-"
                ts_values.append(ts_value)
                ts_columns.append(f"TS-{i}")
        else:
            ts_values = row[str(current_year)]  # Default placeholder
            ts_columns = ["TS-0"]  # Default placeholder if Banyak Data TS not available
        
        if prodi_kriteria == "Persentase Penurunan":
            # Hitung persentase penurunan jika ts_values valid
            # if isinstance(ts_values, list) and all(isinstance(val, (int, float)) for val in ts_values if val != "-"):
            persentase_penurunan = calculate_persentase_penurunan(ts_values)
            ambang_batas_jumlah_mahasiswa = calculate_ts0_minimal(ts_values, prodi_ppm)
                
            #     # Hitung Ambang Batas Jumlah Mahasiswa Minimal
            #     if len(ts_values) > 1 and ts_values[1] != 0 and ts_values[1] != "-":
            #         ts1 = ts_values[1]
            #         ambang_batas_jumlah_mahasiswa = math.ceil(ts1 / (1 + prodi_formula["Ambang Batas (%)"] / 100))
            #     else:
            #         ambang_batas_jumlah_mahasiswa = "-"
                
            #     # Tentukan Hasil Pemantauan
            #     if persentase_penurunan == "-":
            #         hasil_pemantauan = "-"
            #     else:
            hasil_pemantauan = "Lolos" if persentase_penurunan <= prodi_formula["Ambang Batas (%)"] else "Tidak Lolos"
                
            # Tambahkan hasil ke list
            hasil_list.append({
                'Prodi': prodi_name,
                'Jenjang': jenjang,
                'Lembaga': lembaga,
                'Kriteria': prodi_kriteria,
                'Banyak Data TS': prodi_banyak_data,
                'Jumlah Mahasiswa TS': ts_values,
                'Hitung Persentase Penurunan (%)': persentase_penurunan,
                'Persentase Penurunan Maksimal (%)': prodi_ppm,
                'Konversi Jumlah Mahasiswa Minimal': ambang_batas_jumlah_mahasiswa,
                f'Hasil Pemantauan ({current_year})': hasil_pemantauan,
                # 'Tanggal Pemantauan': date.today(),
            })
            
            # else:
            #     # Jika ts_values tidak valid, set semua ke "-"
            #     hasil_list.append({
            #         'Prodi': prodi_name,
            #         'TS Data': ts_values,
            #         'Persentase Penurunan (%)': "-",
            #         'Persentase Penurunan Maksimal (%)': "-",
            #         'Ambang Batas Jumlah Mahasiswa Minimal': "-",
            #         f'Hasil Pemantauan ({current_year})': "-",
            #         # 'Tanggal Pemantauan': date.today(),
            #     })
        
        elif prodi_kriteria == "Jumlah Mahasiswa":
            # Ambil jumlah mahasiswa pada tahun pemantauan
            current_students = row.get(str(current_year), 0)
            
            # Tentukan Hasil Pemantauan
            hasil_pemantauan = "Lolos" if current_students >= prodi_formula["Ambang Batas (Jumlah)"] else "Tidak Lolos"
            
            # Tambahkan hasil ke list
            hasil_list.append({
                'Prodi': prodi_name,
                'Jenjang': jenjang,
                'Lembaga': lembaga,
                'Kriteria': prodi_kriteria,
                'Banyak Data TS': prodi_banyak_data,
                'Jumlah Mahasiswa TS': ts_values,
                'Hitung Persentase Penurunan (%)': None,
                'Persentase Penurunan Maksimal (%)': None,
                'Konversi Jumlah Mahasiswa Minimal': prodi_formula["Ambang Batas (Jumlah)"],
                f'Hasil Pemantauan ({current_year})': hasil_pemantauan
                # 'Tanggal Pemantauan': date.today(),
            })

            # hasil_list.append({
            #     'Prodi': prodi_name,
            #     'Jenjang': jenjang,
            #     'Lembaga': lembaga,
            #     'Kriteria': prodi_kriteria,
            #     'Banyak Data TS': prodi_banyak_data,
            #     'Data TS': ts_values,
            #     'Hitung Persentase Penurunan (%)': persentase_penurunan,
            #     'Persentase Penurunan Maksimal (%)': prodi_ppm,
            #     'Konversi Jumlah Mahasiswa Minimal': ambang_batas_jumlah_mahasiswa,
            #     f'Hasil Pemantauan ({current_year})': hasil_pemantauan,
            #     # 'Tanggal Pemantauan': date.today(),
            # })
    
    if not hasil_list:
        st.warning("Tidak ada hasil pemantauan yang tersedia.")
        return
    
    # Convert hasil_list ke DataFrame
    hasil_df = pd.DataFrame(hasil_list)
    
    # Menampilkan hasil pemantauan
    # st.success("Pemantauan Berhasil Dilakukan!")
    st.write("**Hasil Pemantauan:**")
    visualization_selected(hasil_df)
    st.write(hasil_df)

    
        # (Optional) Menyimpan hasil ke file pickle atau Google Sheets
        # Simpan ke 'existing_dhp.pickle'
        # try:
        #     with open('existing_dhp.pickle', 'rb') as handle:
        #         existing_dhp = pickle.load(handle)
        # except FileNotFoundError:
        #     existing_dhp = pd.DataFrame()
        
        # updated_dhp = pd.concat([existing_dhp, hasil_df], ignore_index=True)
        
        # with open('existing_dhp.pickle', 'wb') as handle:
        #     pickle.dump(updated_dhp, handle, protocol=pickle.HIGHEST_PROTOCOL)
        

    # # Display the plot in Streamlit

    # st.pyplot(plt)
    #     # st.success("Hasil pemantauan telah disimpan.")
    
# def main():
#     # Load dan preprocess data
#     existing_djm, existing_formula = load_data()
#     existing_djm, existing_formula = preprocess_data(existing_djm, existing_formula)
    
#     # Buat form pemantauan
#     create_pemantauan_form(existing_djm, existing_formula)

# if __name__ == "__main__":
#     main()

