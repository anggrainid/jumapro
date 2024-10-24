import streamlit as st
import pickle
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import numpy as np
from data import get_data, refresh_data, preprocess_data
from rumus_prediksi_pemantauan import hitung_persentase_penurunan

def predict_all():
    # 1. Connections from google sheets
    if st.button('Refresh Data'):
        existing_djm = refresh_data('djm')
        existing_formula = refresh_data('formula')
        st.success("Data berhasil dimuat ulang dari Google Sheets!")
    else:
    # 2. Connections from pickle
        existing_djm = get_data('djm')
        existing_formula = get_data('formula')
    
    model = pickle.load(open(r"next_year_students_prediction.sav", "rb"))
       
    # 3. Data preprocessing

    existing_djm = preprocess_data(existing_djm)
    existing_formula = preprocess_data(existing_formula)
    existing_djm.columns = [str(i) for i in existing_djm.columns]

    # Dropdown options for Lembaga
    lembaga_options = existing_djm['Lembaga'].unique()
    formula_options = existing_formula['Nama Rumus'].unique()

    # Menentukan Tahun Pemantauan
    years = [int(col) for col in existing_djm.columns if str(col).isdigit()]
    if not years:
        st.error("Tidak ada data tahun yang tersedia di existing_djm.")

    max_year = max(years)
    min_year = min(years)

    # 4. CRUD form prediksi pemantauan semua prodi

    input_predict_year = st.slider("Masukkan Tahun yang Ingin Diprediksi (ex: 2025) : ", min_value=min_year+5, max_value=max_year+1)
    input_last_year = input_predict_year - 1
    input_years_to_predict = st.slider("Masukkan Proyeksi Prediksi (Dalam Satuan Tahun) : ", min_value=1, max_value=10)

    # 5. Prepare output columns

    for i in range(input_years_to_predict):
        existing_djm[str(input_predict_year+i)] = [None]*len(existing_djm)

    existing_djm['Hasil Proyeksi Prediksi Pemantauan'] = [None]*len(existing_djm)

    # 6. Get Data Formula Pemantauan
    
    selected_formulas_lembaga = {}
    banyak_data_ts_lembaga = {}

    for lembaga_name in lembaga_options:
        formula_options = existing_formula[existing_formula['Lembaga'] == lembaga_name]['Nama Rumus'].unique()
        selected_formulas_lembaga[lembaga_name] = st.selectbox(f"Pilih Rumus yang Digunakan bagi Prodi di bawah Lembaga {lembaga_name} : ", formula_options)
        selected_formulas_name = existing_formula[(existing_formula['Nama Rumus'] == selected_formulas_lembaga[lembaga_name]) & (existing_formula['Lembaga'] == lembaga_name)].iloc[0]
        st.write(selected_formulas_name)
        banyak_data_ts_lembaga[lembaga_name] = selected_formulas_name['Banyak Data TS']

    max_banyak_data_ts = max([0 if pd.isna(banyak_data_ts_lembaga[lembaga_name]) else banyak_data_ts_lembaga[lembaga_name] for lembaga_name in lembaga_options])
    max_banyak_data_ts = int(max_banyak_data_ts)

    # 7. Prediksi setiap prodi
    model_results = {
        "index": [],
        "X": [],
        "Y": [],
    }

    existing_djm['index'] = existing_djm.index

    for index, row in existing_djm.iterrows():
        lembaga_prodi = row['Lembaga']
        selected_formula = existing_formula[(existing_formula['Nama Rumus'] == selected_formulas_lembaga[lembaga_prodi]) & (existing_formula['Lembaga'] == lembaga_prodi)].iloc[0]
        input_kriteria = selected_formula["Kriteria"]
        existing_djm.at[index, 'Kriteria Input'] = input_kriteria
        input_ambang_batas_jumlah = selected_formula["Ambang Batas (Jumlah)"]

        input_banyak_data_ts = selected_formula["Banyak Data TS"]
        input_fields = {}
        input_fields["input_jumlah_mahasiswa_ts0"] = existing_djm[str(input_predict_year)]
        for i in range(max_banyak_data_ts-1):
            field_name = f"input_jumlah_mahasiswa_ts{i}"            
            try:
                input_fields[field_name] = existing_djm[str(input_predict_year-i-1)]
            except KeyError:
                raise ValueError("Data TS tidak tersedia")
            
        for col, value in input_fields.items():
            existing_djm[col] = value
            
        ts = [f"input_jumlah_mahasiswa_ts{i}" for i in range(1, int(max_banyak_data_ts-1))]
        ts = sorted(ts, reverse=True)
        
        existing_djm.at[index, 'Hasil Proyeksi Prediksi Pemantauan'] = f"Lebih dari {input_years_to_predict} Tahun ke Depan"
        tahun_tidak_lolos_found = False
        
        for i in range(input_years_to_predict):
            next_year = input_last_year + i
            
            column_name = next_year
            prediksi_mahasiswa = model.predict([[existing_djm.at[index, str(next_year)]]])[0]
            model_results['index'].append(index)
            model_results['X'].append(existing_djm.at[index, str(next_year)])
            model_results['Y'].append(prediksi_mahasiswa)
            
            existing_djm.at[index, str(column_name+1)] = round(prediksi_mahasiswa)
            input_ambang_batas_jumlah = selected_formula["Ambang Batas (Jumlah)"]
            
            if (not tahun_tidak_lolos_found) and (input_kriteria == 'Jumlah Mahasiswa') and (prediksi_mahasiswa < input_ambang_batas_jumlah):
                existing_djm.at[index, 'Hasil Proyeksi Prediksi Pemantauan'] = f"Tidak Lolos pada {next_year+1}"
                tahun_tidak_lolos_found = True
            else:
                existing_djm.at[index, 'Hasil Proyeksi Prediksi Pemantauan'] = f"Hanya tersedia untuk Kriteria Jumlah Mahasiswa"

        if input_kriteria == "Persentase Penurunan":
            input_ambang_batas_persen = existing_formula[(existing_formula['Nama Rumus'] == selected_formulas_lembaga[existing_djm.at[index, 'Lembaga']]) & (existing_formula['Lembaga'] == existing_djm.at[index, 'Lembaga'])].iloc[0]['Ambang Batas (%)']
            input_ambang_batas_persen = 0 if np.isnan(input_ambang_batas_persen) else input_ambang_batas_persen
            input_ambang_batas_jumlah = None
            selected_formula = existing_formula[(existing_formula['Nama Rumus'] == selected_formulas_lembaga[lembaga_prodi]) & (existing_formula['Lembaga'] == lembaga_prodi)].iloc[0]
            input_banyak_data_ts = selected_formula["Banyak Data TS"]

            if input_banyak_data_ts > 2:
                persentase_penurunan = hitung_persentase_penurunan(index=index, data=existing_djm, predict_year=input_predict_year, banyak_data_ts=input_banyak_data_ts, input_fields=input_fields)
            else:
                persentase_penurunan = hitung_persentase_penurunan(index=index, data=existing_djm, predict_year=input_predict_year)
                
            existing_djm.at[index, 'Hitung Persentase Penurunan'] = f"{persentase_penurunan}%"
            hasil_prediksi_pemantauan = "Lolos" if persentase_penurunan <= input_ambang_batas_persen else "Tidak Lolos"
            existing_djm.at[index, f"Hasil Prediksi Pemantauan ({input_predict_year})"] = hasil_prediksi_pemantauan
            
            # convert_percent_to_ambang_batas_jumlah_mahasiswa = int(row[str(input_last_year)] * (1 - input_ambang_batas_persen / 100))
            existing_djm.at[index, "Persentase Penurunan Maksimal"] = f"{input_ambang_batas_persen}%"
            existing_djm.at[index, "Jumlah Mahasiswa Minimal"] = 0

        elif input_kriteria == "Jumlah Mahasiswa":
            existing_djm.at[index, "Hitung Persentase Penurunan"] = 0
            existing_djm.at[index, "Persentase Penurunan Maksimal"] = 0.0
            hasil_prediksi_pemantauan = "Lolos" if existing_djm.at[index, str(input_predict_year)] >= input_ambang_batas_jumlah else "Tidak Lolos"
            existing_djm.at[index, "Jumlah Mahasiswa Minimal"] = input_ambang_batas_jumlah
            existing_djm.at[index, f"Hasil Prediksi Pemantauan ({input_predict_year})"] = hasil_prediksi_pemantauan

    # 9. Wrapping output columns
    data_predict_years = [f"{next_year}" for next_year in range(input_predict_year + 1, input_predict_year + input_years_to_predict)]
    data_predict_target = [f"{input_predict_year}"]

    ordered_data_prodi = ["Prodi"] + ["Jenjang"] + ["Lembaga"] + ["Kriteria Input"] + ts + [f"{input_last_year}"] + data_predict_target + ["Hitung Persentase Penurunan"] + ["Persentase Penurunan Maksimal"] + ["Jumlah Mahasiswa Minimal"] + [f"Hasil Prediksi Pemantauan ({input_predict_year})"] + data_predict_years + ['Hasil Proyeksi Prediksi Pemantauan']
    tampil_data_prodi = existing_djm[ordered_data_prodi]

    rename_ts = {f"input_jumlah_mahasiswa_ts{i+1}": f"{input_last_year-i-1} (TS-{i+1})" for i in range(int(input_banyak_data_ts-1))}
    rename_predict_years = {f"{next_year}": f"{next_year} (Prediksi)" for next_year in range(input_predict_year + 1, input_predict_year + input_years_to_predict)}
    tampil_data_prodi.rename(columns=rename_ts, inplace=True)
    tampil_data_prodi.rename(columns=rename_predict_years, inplace=True)
    tampil_data_prodi.rename(columns={f"{input_predict_year}": f"{input_predict_year} (Prediksi)"}, inplace=True)
    tampil_data_prodi.rename(columns={f"{input_last_year}": f"{input_last_year} (TS)"}, inplace=True)

    if st.button('Prediksi'):
        tampil_data_prodi
   
