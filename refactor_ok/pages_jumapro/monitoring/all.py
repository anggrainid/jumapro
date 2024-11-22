import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date
from component.func import calculate_persentase_penurunan, calculate_ts0_minimal

def pemantauan_semua_prodi(existing_djm, existing_formula):

    st.title("Halaman Pemantauan Semua Program Studi")
    st.markdown("Halaman ini digunakan untuk melakukan pemantauan jumlah mahasiswa baru pada semua program studi yang tersedia")
    
    acc_columns = ['Peringkat', 'Awal Masa Berlaku', 'Akhir Masa Berlaku', 'Kadaluarsa']
    existing_djm = existing_djm.drop(acc_columns, axis=1, errors='ignore')
    st.write(existing_djm)
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
            persentase_penurunan = calculate_persentase_penurunan(ts_values)
            ambang_batas_jumlah_mahasiswa = calculate_ts0_minimal(ts_values, prodi_ppm)
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
    st.write("**Hasil Pemantauan:**")
    
    # Plot
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
    st.pyplot(plt)

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

