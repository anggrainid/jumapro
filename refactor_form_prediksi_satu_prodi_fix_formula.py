import streamlit as st
import pickle
import pandas as pd
from datetime import date
import numpy as np

def load_form_prediksi():
    # Judul Halaman
    st.title("Halaman Prediksi Suatu Prodi Dengan Formula")

    # Memuat data dari pickle
    try:
        with open('D:\\jumapro\\existing_djm.pickle', 'rb') as handle:
            existing_djm = pickle.load(handle)

        with open('D:\\jumapro\\existing_formula.pickle', 'rb') as handle:
            existing_formula = pickle.load(handle)
    except Exception as e:
        st.error(f"Error memuat data: {e}")
        st.stop()

    # Memuat model prediksi yang sudah ada
    try:
        model = pickle.load(open(r"D:\jumapro\next_year_students_prediction.sav", "rb"))
    except Exception as e:
        st.error(f"Error memuat model: {e}")
        st.stop()

    # Data Preprocessing
    existing_djm = existing_djm.dropna(how="all").replace('#N/A ()', 0)
    existing_formula = existing_formula.dropna(how="all")
    existing_djm.columns = [str(i) for i in existing_djm.columns]

    # Menghapus kolom yang tidak diperlukan
    unused_columns = ['Kode Prodi', 'Kode Prodi UGM', 'Kode Fakultas', 'Program Studi', 
                      'BAN PT', 'Departemen', 'Kluster', 'PDDIKTI x BAN']
    existing_djm = existing_djm.drop(unused_columns, axis=1, errors='ignore')

    # Input Fields
    input_prodi = st.text_input("Masukkan Nama Program Studi : ")

    input_current_year = st.number_input(
        "Masukkan Tahun Sekarang (ex: 2024) : ", 
        min_value=1900, 
        max_value=2100, 
        value=2024
    )
    input_years_to_predict = st.number_input(
        "Masukkan Proyeksi Prediksi (Dalam Satuan Tahun) : ", 
        min_value=0, 
        max_value=10, 
        value=0,
        step=1
    )

    # Dropdown untuk memilih formula jika "Sudah Ada"
    input_formula = st.radio("Formula yang Digunakan", ["Sudah Ada", "Baru"])

    if input_formula == "Sudah Ada":
        formula_options = existing_formula['Nama Rumus'].unique()
        input_existing_formula = st.selectbox("Pilih Rumus yang Digunakan : ", formula_options)
        
        # Mengambil baris formula yang dipilih
        try:
            selected_formula = existing_formula[existing_formula['Nama Rumus'] == input_existing_formula].iloc[0]
            st.write("Detail Formula yang Dipilih:")
            st.write(selected_formula)
        except IndexError:
            st.error("Formula yang dipilih tidak ditemukan.")
            st.stop()
        
        # Cek kriteria
        input_kriteria = selected_formula.get("Kriteria", "Jumlah Mahasiswa")
        if input_kriteria == "Persentase Penurunan":
            input_ambang_batas_persen = selected_formula.get("Ambang Batas (%)", 0)
            input_banyak_data_ts = int(selected_formula.get("Banyak Data TS", 2))
            input_ambang_batas_jumlah = None

            # Input jumlah mahasiswa berdasarkan banyak_data_ts
            input_fields = {}
            st.subheader("Masukkan Jumlah Mahasiswa untuk Time Series:")
            for i in range(input_banyak_data_ts):
                year = input_current_year - i
                field_name = f"input_jumlah_mahasiswa_ts{i}"
                label = f"Masukkan Jumlah Mahasiswa Tahun {year} (TS-{i}) : "
                input_fields[field_name] = st.number_input(label, value=0, step=1)
        else:
            input_ambang_batas_jumlah = st.number_input(
                "Ambang Batas Jumlah Mahasiswa Minimal", 
                min_value=1, 
                step=1
            )
            input_jumlah_mahasiswa_ts = st.number_input(
                f"Masukkan Jumlah Mahasiswa Tahun {input_current_year} (TS-0) : ", 
                value=0,
                step=1
            )
            input_ambang_batas_persen = None
            input_fields = None

    else:
        input_kriteria = st.radio("Kriteria", ["Jumlah Mahasiswa", "Persentase Penurunan"])
        if input_kriteria == "Persentase Penurunan":
            input_ambang_batas_persen = st.slider(
                "Ambang Batas Persentase Maksimal (%)", 
                min_value=1, 
                max_value=100, 
                step=1
            )
            input_banyak_data_ts = st.slider(
                "Masukkan Banyak Tahun yang Dipakai untuk Persentase Penurunan : ", 
                min_value=2, 
                max_value=5, 
                step=1
            )
            input_ambang_batas_jumlah = None

            input_fields = {}
            st.subheader("Masukkan Jumlah Mahasiswa untuk Time Series:")
            for i in range(input_banyak_data_ts):
                year = input_current_year - i
                field_name = f"input_jumlah_mahasiswa_ts{i}"
                label = f"Masukkan Jumlah Mahasiswa Tahun {year} (TS-{i}) : "
                input_fields[field_name] = st.number_input(label, value=0, step=1)
        else:
            input_ambang_batas_jumlah = st.number_input(
                "Ambang Batas Jumlah Mahasiswa Minimal", 
                min_value=1, 
                step=1
            )
            input_jumlah_mahasiswa_ts = st.number_input(
                f"Masukkan Jumlah Mahasiswa Tahun {input_current_year} (TS-0) : ", 
                value=0,
                step=1
            )
            input_ambang_batas_persen = None
            input_fields = None

    # Fungsi untuk menghitung persentase penurunan
    def hitung_persentase_penurunan(ts_current, ts_previous):
        try:
            if ts_current == 0.0 or pd.isna(ts_current) or (ts_current is None):
                return 0
            penurunan = (ts_previous - ts_current) / ts_current
            persentase_penurunan = penurunan * 100
            return round(-persentase_penurunan, 2)
        except Exception as e:
            st.error(f"Error menghitung persentase penurunan: {e}")
            return 0

    # Fungsi untuk menghitung persentase penurunan dengan lebih dari satu tahun data
    def hitung_persentase_penurunan_lebih_dari_satu(ts_years):
        total_penurunan = 0
        valid_years = 0
        
        for i in range(1, len(ts_years)):
            ts_current = ts_years[i]
            ts_previous = ts_years[i - 1]
            
            if ts_current == 0 or pd.isna(ts_current) or (ts_current is None):
                return 0
            
            penurunan = (ts_previous - ts_current) / ts_current
            total_penurunan += penurunan
            valid_years += 1
        
        if valid_years == 0:
            return 0
        
        rata_rata_penurunan = total_penurunan / valid_years
        persentase_penurunan = rata_rata_penurunan * 100
        return round(-persentase_penurunan, 2)

    # Tombol Prediksi
    if st.button("Prediksi"):
        # Membuat DataFrame untuk prodi baru
        if input_kriteria == "Jumlah Mahasiswa":
            new_data_prodi = {
                'Prodi': [input_prodi],
                f'{input_current_year} (TS-0)': [input_jumlah_mahasiswa_ts]
            }
        else:
            ts_years = [input_fields[f"input_jumlah_mahasiswa_ts{i}"] for i in range(input_banyak_data_ts)]
            new_data_prodi = {
                'Prodi': [input_prodi],
                f'{input_current_year} (TS-0)': [ts_years[0]]
            }
            for i in range(1, input_banyak_data_ts):
                year = input_current_year - i
                new_data_prodi[f'{year} (TS-{i})'] = [ts_years[i]]

        data_prodi = pd.DataFrame(new_data_prodi)

        # Penilaian kelolosan berdasarkan kriteria
        if input_kriteria == "Jumlah Mahasiswa":
            current_students = data_prodi[f'{input_current_year} (TS-0)'].values[0]
            hasil_prediksi_pemantauan = "Lolos" if current_students >= input_ambang_batas_jumlah else "Tidak Lolos"
            
            data_prodi["Jumlah Mahasiswa Minimal"] = input_ambang_batas_jumlah
            data_prodi[f"Hasil Prediksi Pemantauan ({input_current_year})"] = hasil_prediksi_pemantauan
            data_prodi["Tahun Tidak Lolos (Prediksi)"] = "Lebih dari 0 Tahun ke Depan"  # Karena tidak ada prediksi

        elif input_kriteria == "Persentase Penurunan":
            ts_years = [input_fields[f"input_jumlah_mahasiswa_ts{i}"] for i in range(input_banyak_data_ts)]
            if input_years_to_predict == 0:
                # Gunakan data asli
                if input_banyak_data_ts > 2:
                    persentase_penurunan = hitung_persentase_penurunan_lebih_dari_satu(ts_years)
                else:
                    if len(ts_years) >=2:
                        persentase_penurunan = hitung_persentase_penurunan(ts_years[0], ts_years[1])
                    else:
                        persentase_penurunan = 0
            else:
                # Gunakan data prediksi
                # Prediksi tahun berikutnya
                predicted_year = input_current_year + input_years_to_predict
                prediksi_mahasiswa = model.predict([[ts_years[0]]])[0]
                data_prodi[f'{predicted_year} (Prediksi)'] = [round(prediksi_mahasiswa)]
                ts_years.append(prediksi_mahasiswa)
                persentase_penurunan = hitung_persentase_penurunan(ts_years[-1], ts_years[-2])
            
            hasil_prediksi_pemantauan = "Lolos" if persentase_penurunan <= input_ambang_batas_persen else "Tidak Lolos"
            
            ambang_batas_jumlah_mahasiswa = int(ts_years[0] * (1 - input_ambang_batas_persen / 100))
            data_prodi["Hitung Persentase Penurunan"] = f"{persentase_penurunan}%"
            data_prodi["Persentase Penurunan Maksimal"] = f"{input_ambang_batas_persen}%"
            data_prodi["Ambang Batas Jumlah Mahasiswa Minimal"] = ambang_batas_jumlah_mahasiswa
            data_prodi[f"Hasil Prediksi Pemantauan ({input_current_year})"] = hasil_prediksi_pemantauan
            data_prodi["Tahun Tidak Lolos (Prediksi)"] = "Lebih dari 0 Tahun ke Depan"  # Karena tidak ada prediksi

        # Pengurutan Kolom Time Series (`ts`)
        if input_kriteria == "Persentase Penurunan":
            # Membuat daftar kolom ts berdasarkan jumlah data ts dan years_to_predict
            if input_years_to_predict > 0:
                # Include prediksi
                ts_columns = [f'{input_current_year - i} (TS-{i})' for i in range(input_banyak_data_ts)]
                # Tambahkan prediksi
                for i in range(1, input_years_to_predict + 1):
                    year = input_current_year + i
                    ts_columns.append(f'{year} (Prediksi)')
            else:
                # Gunakan data asli
                ts_columns = [f'{input_current_year - i} (TS-{i})' for i in range(input_banyak_data_ts)]
            
            # Urutkan kolom ts berdasarkan TS-x dengan x menurun
            def sort_ts(column_name):
                if "Prediksi" in column_name:
                    # TS+1, TS+2, etc.
                    return float('inf')  # Prediksi muncul setelah TS-0
                else:
                    # Extract TS-x
                    try:
                        x = int(column_name.split('(TS-')[1].rstrip(')'))
                        return -x  # Agar TS-2 < TS-1 < TS-0
                    except:
                        return 0  # Default
    
            ts_columns_sorted = sorted(ts_columns, key=sort_ts)
            
            # Reorder DataFrame columns
            ordered_columns = ['Prodi'] + ts_columns_sorted
            additional_columns = [col for col in data_prodi.columns if col not in ordered_columns]
            ordered_columns += additional_columns
            data_prodi_sorted = data_prodi[ordered_columns]
            
            st.write("Data Prodi Setelah Pengurutan Kolom TS:")
            st.write(data_prodi_sorted)
        else:
            st.write("Hasil Prediksi dan Penilaian:")
            st.write(data_prodi)
    
        # (Optional) Menyimpan data ke Google Sheets atau file lain
        # Misalnya, menambahkan ke existing_dhp dan menyimpan kembali
        # existing_dhp = existing_dhp.append(data_prodi, ignore_index=True)
        # conn.update(worksheet="Data Histori Prediksi Suatu Prodi", data=existing_dhp)

        st.success("Prediksi dan penilaian berhasil dilakukan!")

    # Menampilkan informasi tambahan jika diperlukan
    st.write("**Catatan:** Jika Anda memilih `Masukkan Proyeksi Prediksi (Dalam Satuan Tahun)` > 0, maka prediksi model akan dilakukan.")

load_form_prediksi()
