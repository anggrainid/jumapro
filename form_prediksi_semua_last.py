import streamlit as st
import pickle
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import numpy as np

# 1. Connections from google sheets


# conn = st.connection("gsheets", type=GSheetsConnection)
# existing_dhp = conn.read(worksheet="Data Histori Prediksi Suatu Prodi", ttl=5)
# existing_djm = conn.read(worksheet="Data Jumlah Mahasiswa")
# existing_formula = conn.read(worksheet="Rumus Pemantauan", usecols=list(range(7)), ttl=5)

# with open('existing_dhp.pickle', 'wb') as handle:
#     pickle.dump(existing_dhp, handle, protocol=pickle.HIGHEST_PROTOCOL)

# with open('existing_djm.pickle', 'wb') as handle:
#     pickle.dump(existing_djm, handle, protocol=pickle.HIGHEST_PROTOCOL)
    
# with open('existing_formula.pickle', 'wb') as handle:
#     pickle.dump(existing_formula, handle, protocol=pickle.HIGHEST_PROTOCOL)

# 2. Connections from google sheets

with open('existing_djm.pickle', 'rb') as handle:
    existing_djm = pickle.load(handle)

with open('existing_djm.pickle', 'rb') as handle:
    existing_djm = pickle.load(handle)

with open('existing_formula.pickle', 'rb') as handle:
    existing_formula = pickle.load(handle)
    
model = pickle.load(open(r"next_year_students_prediction.sav", "rb"))

# 3. Data preprocessing

# Djm = data jumlah mahasiswa
# Dhp = data history prediksi

existing_djm = existing_djm.dropna(how="all")
existing_djm = existing_djm.replace('#N/A ()', 0)
# existing_dhp = existing_dhp.dropna(how="all")
existing_formula = existing_formula.dropna(how="all")
existing_djm.columns = [str(i) for i in existing_djm.columns]

# Dropdown options for Lembaga
lembaga_options = existing_djm['Lembaga'].unique()
formula_options = existing_formula['Nama Rumus'].unique()

unused_column = ['Kode Prodi', 'Kode Prodi UGM', 'Kode Fakultas', 'Program Studi', 'BAN PT', 'Departemen', 'Kluster', 'PDDIKTI x BAN']
existing_djm = existing_djm.drop(unused_column, axis=1)
existing_djm
# st.write(existing_djm.info())

# 4. CRUD form prediksi pemantauan semua prodi
djm_prodi = existing_djm["Prodi"]

max_year = int(existing_djm.columns[-1])
min_year = int(existing_djm.columns[12])

input_predict_year = st.slider("Masukkan Tahun yang Ingin Diprediksi (ex: 2025) : ", min_value=min_year, max_value=max_year+1)
input_last_year = input_predict_year - 1

input_years_to_predict = st.slider("Masukkan Proyeksi Prediksi (Dalam Satuan Tahun) : ", min_value=1, max_value=10)


# print(min_year, max_year)

# 5. Prepare output columns

# existing_djm[f'Hasil Prediksi Pemantauan ({input_predict_year})'] = [None]*len(existing_djm)

for i in range(input_years_to_predict):
    existing_djm[str(input_predict_year+i)] = [None]*len(existing_djm)

existing_djm['Hasil Proyeksi Prediksi Pemantauan'] = [None]*len(existing_djm)

# 6. Get Data Formula Pemantauan

selected_formulas_lembaga = {}
    # Pilih Formula untuk setiap lembaga
for lembaga_name in lembaga_options:
    # Filter formulas by the selected Lembaga
    formula_options = existing_formula[existing_formula['Lembaga'] == lembaga_name]['Nama Rumus'].unique()

    # Dropdown to select formula for the current Lembaga
    selected_formulas_lembaga[lembaga_name] = st.selectbox(f"Pilih Rumus yang Digunakan bagi Prodi di bawah Lembaga {lembaga_name} : ", formula_options)
    print("selected_formula", selected_formulas_lembaga[lembaga_name]) #Rumus Pertama BAN 2024
    selected_formulas_name = existing_formula[(existing_formula['Nama Rumus'] == selected_formulas_lembaga[lembaga_name]) & (existing_formula['Lembaga'] == lembaga_name)].iloc[0]
    st.write(selected_formulas_name)

# 7. Fungsi hitung persentase penurunan
def hitung_persentase_penurunan(index, data, predict_year):
    # data_mahasiswa_start_year = input_fields["input_jumlah_mahasiswa_ts0"]
    # end_year = predict_year
    # penurunan_total = (data[f"{end_year} (Prediksi)"] - data_mahasiswa_start_year)
    # persentase_penurunan = (penurunan_total / 2) * 100
    # return persentase_penurunan
    ts_1 = data.at[index, f"{predict_year}"]
    ts_0 = data.at[index, str(input_last_year)]
    try:
        if ts_1==0.0 or np.isnan(ts_1) or (ts_1 is None):
            return 0
    except Exception as e:
        print('ERRROR: ts0 ts1', index, type(ts_1), ts_0, ts_1)
        raise e
            
    penurunan = (ts_0 - ts_1) / ts_1

    persentase_penurunan = penurunan * 100

    return round(-persentase_penurunan, 2)

# print('input_fields:', input_fields)
# input_fields
# Fungsi untuk menghitung persentase penurunan dengan lebih dari satu tahun data
def hitung_persentase_penurunan_lebih_dari_satu(index, data, predict_year, banyak_data_ts):
    print('function ppls: ', (index, 'existing_djm', predict_year, banyak_data_ts))
    global input_fields

    total_penurunan = 0
    
    # Iterasi dari TS-1 hingga TS-n (n = banyak_data_ts)
    for i in range(int(banyak_data_ts) - 1):
        if i == 0:
            data = data.iloc[index]
            ts_0 = data[str(predict_year)]
            ts_1 = data[str(input_last_year)]

            
        else:
            # input_fields = input_fields[]
            ts_1 = input_fields[f"input_jumlah_mahasiswa_ts{i}"][index]
            ts_0 = input_fields[f"input_jumlah_mahasiswa_ts{i-1}"][index]

        print(i, (ts_0), (ts_1))
        
        if ts_1==0 or np.isnan(ts_1) or (ts_1 is None):
            return 0           
                 
        penurunan = (ts_0 - ts_1) / ts_1
        total_penurunan += penurunan
        
    
    # print('data:', type(data))
    
    # Hitung rata-rata penurunan
    
    rata_rata_penurunan = total_penurunan / (banyak_data_ts - 1)
    persentase_penurunan = rata_rata_penurunan * 100

    print(f'out {index}:', ' | ', total_penurunan, ' | ', persentase_penurunan)
    
    return round(-persentase_penurunan, 2)

# 8. Prediksi setiap prodi
model_results = {
    "index": [],
    "X": [],
    "Y": [],
}

existing_djm['index'] = existing_djm.index


for index, row in existing_djm.iterrows():
    lembaga_prodi = row['Lembaga']
    prodi_name = row['Prodi']        
    current_students = row[str(input_last_year)]
    tahun_tidak_lolos = f"Lebih dari {input_years_to_predict} Tahun ke Depan"  # Default value
    
    selected_formula = existing_formula[(existing_formula['Nama Rumus'] == selected_formulas_lembaga[lembaga_prodi]) & (existing_formula['Lembaga'] == lembaga_prodi)].iloc[0]
    input_kriteria = selected_formula["Kriteria"]
    existing_djm.at[index, 'Kriteria Input'] = input_kriteria
    input_ambang_batas_jumlah = selected_formula["Ambang Batas (Jumlah)"]
        # looping isi prediksi
    tahun_tidak_lolos_found = False
    existing_djm.at[index, 'Hasil Proyeksi Prediksi Pemantauan'] = f"Lolos Lebih dari {input_years_to_predict} Tahun ke Depan"
    for i in range(input_years_to_predict):
        next_year = input_last_year + i
        
        column_name = next_year#f'{next_year} (Prediksi)'

        # Lakukan prediksi menggunakan model untuk current_students dari baris ini
        
        # print('X:', index, next_year, existing_djm.at[index, next_year])
        prediksi_mahasiswa = model.predict([[existing_djm.at[index, str(next_year)]]])[0]
        model_results['index'].append(index)
        model_results['X'].append(existing_djm.at[index, str(next_year)])
        model_results['Y'].append(prediksi_mahasiswa)
        
            
        existing_djm.at[index, str(column_name+1)] = round(prediksi_mahasiswa)
        input_ambang_batas_jumlah = selected_formula["Ambang Batas (Jumlah)"]
        
        # print('Y:', column_name+1, existing_djm.at[index, column_name+1])

        # Perbarui current_students untuk iterasi berikutnya
        # current_students = prediksi_mahasiswa

        # Cek apakah jumlah mahasiswa di bawah ambang batas untuk kriteria Jumlah Mahasiswa
        
        
        if (not tahun_tidak_lolos_found) and (input_kriteria=='Jumlah Mahasiswa') and (prediksi_mahasiswa<input_ambang_batas_jumlah):
            existing_djm.at[index, 'Hasil Proyeksi Prediksi Pemantauan'] = f"Tidak Lolos pada {next_year+1}"
            tahun_tidak_lolos_found = True
        elif input_kriteria=='Persentase Penurunan':
            existing_djm.at[index, 'Hasil Proyeksi Prediksi Pemantauan'] = f"Hanya tersedia untuk Kriteria Jumlah Mahasiswa"

        # print('loop:', prediksi_mahasiswa, input_ambang_batas_jumlah, tahun_tidak_lolos_found, input_kriteria, existing_djm.at[index, 'Hasil Proyeksi Prediksi Pemantauan'])    

            # Cek apakah jumlah mahasiswa di bawah ambang batas untuk kriteria Persentase Penurunan
                
    
    if input_kriteria == "Persentase Penurunan":
        # print(index, 'PERSENTASE PENURUNAN')
        input_ambang_batas_persen = existing_formula[(existing_formula['Nama Rumus'] == selected_formulas_lembaga[existing_djm.at[index, 'Lembaga']]) & (existing_formula['Lembaga'] == existing_djm.at[index, 'Lembaga'])].iloc[0]['Ambang Batas (%)']
        input_ambang_batas_persen = 0 if np.isnan(input_ambang_batas_persen) else input_ambang_batas_persen
        
        input_banyak_data_ts = selected_formula["Banyak Data TS"]
        input_ambang_batas_jumlah = None
        input_fields = {}
        selected_formula = existing_formula[(existing_formula['Nama Rumus'] == selected_formulas_lembaga[lembaga_prodi]) & (existing_formula['Lembaga'] == lembaga_prodi)].iloc[0]
        
        input_fields["input_jumlah_mahasiswa_ts0"] = existing_djm[str(input_predict_year)]
        for i in range(int(input_banyak_data_ts)-1):
            field_name = f"input_jumlah_mahasiswa_ts{i}"            
            try:
                input_fields[field_name] = existing_djm[str(input_predict_year-i-1)]
                # print(f'jmlh {i} | {field_name} | {input_predict_year-i} | { existing_djm[input_predict_year-i]}')
            except KeyError:
                # MUNGKIN datanya ga cukup, misal pilih 2014, tapi datanya cmn ada dari 2013, trus ambil -3 tahun
                raise ValueError("Data TS tidak tersedia")    
    

        # dari looping function
        input_ambang_batas_persen = existing_formula[(existing_formula['Nama Rumus'] == selected_formulas_lembaga[existing_djm.at[index, 'Lembaga']]) & (existing_formula['Lembaga'] == existing_djm.at[index, 'Lembaga'])].iloc[0]['Ambang Batas (%)']
        input_ambang_batas_persen = 0 if np.isnan(input_ambang_batas_persen) else input_ambang_batas_persen
        round(input_ambang_batas_persen, 2)
        
        
        if input_banyak_data_ts > 2:
            persentase_penurunan = hitung_persentase_penurunan_lebih_dari_satu(index, existing_djm, input_predict_year, input_banyak_data_ts)
        else:
            persentase_penurunan = hitung_persentase_penurunan(index, existing_djm, input_predict_year)
            
        existing_djm.at[index, 'Hitung Persentase Penurunan'] = f"{persentase_penurunan}%"
        hasil_prediksi_pemantauan = str(("Lolos" if persentase_penurunan <= input_ambang_batas_persen else "Tidak Lolos"))
        existing_djm.at[index, f"Hasil Prediksi Pemantauan ({input_predict_year})"] = hasil_prediksi_pemantauan
            
        #print('persentase penurunan:', persentase_penurunan)
        # hasil_prediksi_pemantauan = "Lolos" if persentase_penurunan.values[0] <= input_ambang_batas_persen else "Tidak Lolos"
        
        #"Lolos" if float(persentase_penurunan.iloc[1]) <= input_ambang_batas_persen else "Tidak Lolos"
        convert_percent_to_ambang_batas_jumlah_mahasiswa = int(row[str(input_last_year)] * (1 - input_ambang_batas_persen / 100))
        # ambang_batas_jumlah_mahasiswa = int(data_prodi["current_students"] * (1 - input_ambang_batas_persen / 100))
        existing_djm.at[index, "Persentase Penurunan Maksimal"] = f"{input_ambang_batas_persen}%"
        # existing_djm.at[index, "Ambang Batas Jumlah Mahasiswa Minimal"] = convert_percent_to_ambang_batas_jumlah_mahasiswa
        
        # existing_djm.at[index, "Persentase Penurunan Maksimal"]
        # print(f'row existing djm at index {index}: ', existing_djm.loc[index])
        for col, value in input_fields.items():
            existing_djm[col] = value
        ts = [f"input_jumlah_mahasiswa_ts{i}" for i in range(1, int(input_banyak_data_ts-1))]
        ts = sorted(ts, reverse=True)
        



        existing_djm.at[index, "Jumlah Mahasiswa Minimal"] = 0

    elif input_kriteria == "Jumlah Mahasiswa":
        print(index, 'JUMLAH MAHASISWA')
        
        existing_djm.at[index, "Hitung Persentase Penurunan"] = 0

        existing_djm.at[index, "Persentase Penurunan Maksimal"] = 0.0

        hasil_prediksi_pemantauan = str(("Lolos" if existing_djm.at[index, str(input_predict_year)] >= input_ambang_batas_jumlah else "Tidak Lolos"))
        input_ambang_batas_persen = None
        input_fields = None

        
        existing_djm.at[index, "Jumlah Mahasiswa Minimal"] = input_ambang_batas_jumlah
        existing_djm.at[index, f"Hasil Prediksi Pemantauan ({input_predict_year})"] = hasil_prediksi_pemantauan
        ts = []

# 9. wrapping op columns

data_predict_years = [f"{next_year}" for next_year in range(input_predict_year+1, input_predict_year+input_years_to_predict)]
data_predict_target= [f"{input_predict_year}"]


ordered_data_prodi = ["Prodi"] + ["Jenjang"] + ["Lembaga"] +  ["Kriteria Input"] + ts + [f"{input_last_year}"] + data_predict_target + ["Hitung Persentase Penurunan"] +  ["Persentase Penurunan Maksimal"]+ ["Jumlah Mahasiswa Minimal"] +  [f"Hasil Prediksi Pemantauan ({input_predict_year})"] + data_predict_years + ['Hasil Proyeksi Prediksi Pemantauan']
tampil_data_prodi = existing_djm[ordered_data_prodi]

if input_kriteria=="persentase_penurunan":
    rename_ts = {f"input_jumlah_mahasiswa_ts{i+1}": f"{input_last_year-i-1} (TS-{i+1})" for i in range(int(input_banyak_data_ts-1))}
    tampil_data_prodi.rename(columns=rename_ts, inplace=True)
rename_predict_years = {f"{next_year}": f"{next_year} (Prediksi)" for next_year in range(input_predict_year+1, input_predict_year+input_years_to_predict)}
tampil_data_prodi.rename(columns=rename_predict_years, inplace=True)
tampil_data_prodi.rename(columns={f"{input_predict_year}": f"{input_predict_year} (Prediksi)"}, inplace=True)
tampil_data_prodi.rename(columns={f"{input_last_year}": f"{input_last_year} (TS)"}, inplace=True)

tampil_data_prodi