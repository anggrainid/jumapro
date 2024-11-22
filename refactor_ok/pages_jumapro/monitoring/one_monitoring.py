import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date
from component.func import calculate_persentase_penurunan, calculate_ts0_minimal

def pemantauan_satu_prodi(existing_formula):
    st.title("Halaman Pemantauan Suatu Program Studi")
    # st.markdown("Form Pemantauan Program Studi")
    st.markdown("Halaman ini digunakan untuk melakukan pemantauan jumlah mahasiswa baru pada suatu program studi")
    # Input Fields
    input_prodi = st.text_input("Masukkan Nama Program Studi : ")

    input_current_year = st.number_input(
        "Masukkan Tahun Pemantauan (ex: 2024) : ", 
        min_value=1900, 
        max_value=2100, 
        value=2024
    )
    input_formula = st.radio("Formula yang Digunakan", ["Sudah Ada", "Baru"])

    if input_formula == "Sudah Ada":
        st.subheader("Pilih Formula Pemantauan")
        formula_options = existing_formula['Nama Rumus'].unique()
        input_existing_formula = st.selectbox("Pilih Rumus yang Digunakan : ", formula_options)

        selected_formula = existing_formula[existing_formula['Nama Rumus'] == input_existing_formula].iloc[0]
        st.write("**Detail Formula yang Dipilih:**")
        st.write(selected_formula)
        input_kriteria = selected_formula["Kriteria"]
        input_banyak_data_ts = int(selected_formula["Banyak Data TS"])
        if input_kriteria == "Persentase Penurunan":
            input_ambang_batas_persen = selected_formula["Ambang Batas (%)"]
            # input_banyak_data_ts = int(selected_formula["Banyak Data TS"])
            ts_values = []

            for i in range(input_banyak_data_ts):
                year = input_current_year - i
                value = st.number_input(f"Masukkan Jumlah Mahasiswa Baru Tahun {year} (TS-{i}) : ", step=0)
                ts_values.append(value)

        else:
            input_ambang_batas_jumlah = int(selected_formula["Ambang Batas (Jumlah)"])
            input_jumlah_mahasiswa_ts = st.number_input(
                f"Masukkan Jumlah Mahasiswa Baru Tahun {input_current_year} (TS-0) : ", 
                step=0
            )
            ts_values = [input_jumlah_mahasiswa_ts]  # Start with TS-0

    else:
        input_kriteria = st.radio("Kriteria", ["Jumlah Mahasiswa", "Persentase Penurunan"])
        ts_values = []

        if input_kriteria == "Persentase Penurunan":
            input_ambang_batas_persen = st.slider("Ambang Batas Persentase Maksimal (%)", min_value=1, max_value=100, step=1)
            input_banyak_data_ts = st.slider("Masukkan Banyak Tahun yang Dipakai untuk Persentase Penurunan : ", min_value=2, max_value=5, step=1)

            for i in range(input_banyak_data_ts):
                value = st.number_input(f"Masukkan Jumlah Mahasiswa Baru TS-{i}:", step=0)
                ts_values.append(value)

        else:
            input_banyak_data_ts = 1
            input_ambang_batas_jumlah = st.number_input("Ambang Batas Jumlah Mahasiswa Minimal", min_value=1, step=1)
            input_jumlah_mahasiswa_ts = st.number_input(f"Masukkan Jumlah Mahasiswa Baru Tahun {input_current_year} (TS-0) : ", step=0)
            ts_values.append(input_jumlah_mahasiswa_ts)

    # Tombol untuk melakukan pemantauan
    if st.button("Hitung Pemantauan"):
        
        if input_kriteria == "Persentase Penurunan":
            persentase_penurunan = calculate_persentase_penurunan(ts_values)


            hasil_prediksi_pemantauan = "Lolos" if persentase_penurunan <= input_ambang_batas_persen else "Tidak Lolos"

            # Hitung jumlah mahasiswa minimal berdasarkan persentase penurunan
            ambang_batas_jumlah_mahasiswa = calculate_ts0_minimal(ts_values, input_ambang_batas_persen)

            # Membuat DataFrame hasil pemantauan
            data_prodi = pd.DataFrame({
                'Prodi': [input_prodi],
                f'Jumlah Mahasiswa TS (TS sd TS-{input_banyak_data_ts-1}) ': [ts_values],
                'Persentase Penurunan Maksimal': [f"{input_ambang_batas_persen}%"],
                'Hitung Persentase Penurunan': [f"{persentase_penurunan:.2f}%"],
                'Konversi Jumlah Mahasiswa Minimal': [ambang_batas_jumlah_mahasiswa],
                f'Hasil Pemantauan ({input_current_year})': [hasil_prediksi_pemantauan],
                'Tanggal Pemantauan': [date.today()],
            })

        elif input_kriteria == "Jumlah Mahasiswa":
            current_students = input_jumlah_mahasiswa_ts
            hasil_prediksi_pemantauan = "Lolos" if current_students >= input_ambang_batas_jumlah else "Tidak Lolos"
            ambang_batas_jumlah_mahasiswa = input_ambang_batas_jumlah
            
            # Membuat DataFrame hasil pemantauan
            data_prodi = pd.DataFrame({
                'Prodi': [input_prodi],
                'Jumlah Mahasiswa TS': [input_jumlah_mahasiswa_ts],
                f'Jumlah Mahasiswa Minimal': [input_ambang_batas_jumlah],
                f'Hasil Pemantauan ({input_current_year})': [hasil_prediksi_pemantauan],
                'Tanggal Pemantauan': [date.today()]
            })

        # # Menampilkan hasil pemantauan
        # st.success("Pemantauan Berhasil Dilakukan!")
        # st.write("**Hasil Pemantauan:**")
        # st.table(data_prodi)
  
        # Menampilkan hasil pemantauan
        st.success("Pemantauan Berhasil Dilakukan!")
        st.write("**Hasil Pemantauan:**")
        st.table(data_prodi)

        # Grafik Scatter Plot
        plt.figure(figsize=(10, 6))
        years = list(range(input_current_year - input_banyak_data_ts + 1, input_current_year + 1))
        plt.scatter(years, ts_values[::-1], color='blue', label='Jumlah Mahasiswa Baru')
        plt.plot(years, ts_values[::-1], color='orange', label='Trend')
        plt.axhline(y=ambang_batas_jumlah_mahasiswa, color='red', linestyle='--', label='Ambang Batas Jumlah Mahasiswa Baru Minimal')
        plt.title('Jumlah Mahasiswa Baru Tahun ke Tahun')
        plt.xlabel('Tahun')
        plt.ylabel('Jumlah Mahasiswa Baru')
        plt.xticks(years)  # X-axis labels
        plt.legend()
        plt.grid()
        st.pyplot(plt)

# Pemanggilan fungsi
# pemantauan_satu_prodi(existing_formula)  # Uncomment this line when you call the function in your application
