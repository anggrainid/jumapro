import streamlit as st
from streamlit_gsheets import GSheetsConnection
import streamlit_gsheets as stg
import pickle
import numpy as np

# 1. Connections from google sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. Load Data
# Djm = data jumlah mahasiswa
# Dhp = data histori prediksi
# existing_dhp = conn.read(worksheet="Data Histori Prediksi Suatu Prodi", ttl=5)
# existing_djm = conn.read(worksheet="Data Jumlah Mahasiswa")
# existing_formula = conn.read(worksheet="Rumus Pemantauan", usecols=list(range(7)), ttl=5)

# with open('existing_dhp.pickle', 'wb') as handle:
#     pickle.dump(existing_dhp, handle, protocol=pickle.HIGHEST_PROTOCOL)

# with open('existing_djm.pickle', 'wb') as handle:
#     pickle.dump(existing_djm, handle, protocol=pickle.HIGHEST_PROTOCOL)
    
# with open('existing_formula.pickle', 'wb') as handle:
#     pickle.dump(existing_formula, handle, protocol=pickle.HIGHEST_PROTOCOL)


with open('existing_dhp.pickle', 'rb') as handle:
    existing_dhp = pickle.load(handle)

with open('existing_djm.pickle', 'rb') as handle:
    existing_djm = pickle.load(handle)

with open('existing_formula.pickle', 'rb') as handle:
    existing_formula = pickle.load(handle)

# 3. Data preprocessing
existing_djm = existing_djm.dropna(how="all")
existing_djm = existing_djm.replace('#N/A ()', 0)
existing_dhp = existing_dhp.dropna(how="all")
existing_formula = existing_formula.dropna(how="all")
existing_djm.columns = [str(i) for i in existing_djm.columns]

# Dropdown options for Lembaga
lembaga_options = existing_djm['Lembaga'].unique()
formula_options = existing_formula['Nama Rumus'].unique()

# Start Table
unused_column = ['Kode Prodi', 'Kode Prodi UGM', 'Kode Fakultas', 'Program Studi', 'BAN PT', 'Departemen', 'Kluster', 'PDDIKTI x BAN']
existing_djm = existing_djm.drop(unused_column, axis=1)
# existing_djm.head()
existing_djm.info()

max_value = int(existing_djm.columns[-1])
min_value = int(existing_djm.columns[12])



# 4. CRUD form prediksi pemantauan semua prodi
djm_prodi = existing_djm["Prodi"]

input_predict_year = st.slider("Masukkan Tahun yang Ingin Diprediksi (ex: 2025) : ", min_value=min_value, max_value=max_value+1)
input_last_year = input_predict_year - 1

input_years_to_predict = st.slider("Masukkan Proyeksi Prediksi (Dalam Satuan Tahun) : ", min_value=1, max_value=10)

# input_formula = st.radio("Formula yang Digunakan", ["Sudah Ada", "Baru"])

# 5. Prepare output columns

# existing_djm[f'Hasil Prediksi Pemantauan {input_predict_year}'] = [None]*len(existing_djm)

for i in range(input_years_to_predict):
    existing_djm[str(input_predict_year+i)] = [None]*len(existing_djm)

existing_djm['Hasil Proyeksi Prediksi Pemantauan'] = [None]*len(existing_djm)

data_predict_years = [f"{next_year}" for next_year in range(input_predict_year+1, input_predict_year+input_years_to_predict)]
data_predict_target= [f"{input_predict_year}"]

# 6. Fungsi hitung persentase penurunan

# Fungsi untuk menghitung persentase penurunan
def hitung_persentase_penurunan(data, predict_year):
    # data_mahasiswa_start_year = input_fields["input_jumlah_mahasiswa_ts0"]
    # end_year = predict_year
    # penurunan_total = (data[f"{end_year} (Prediksi)"] - data_mahasiswa_start_year)
    # persentase_penurunan = (penurunan_total / 2) * 100
    # return persentase_penurunan
    ts_1 = data[f"{predict_year}"]
    ts_0 = data[str(input_last_year)]
    penurunan = (ts_0 - ts_1) / ts_1

    persentase_penurunan = penurunan * 100

    return persentase_penurunan

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
        penurunan = (ts_0 - ts_1) / ts_1
        total_penurunan += penurunan
        
    
    # print('data:', type(data))
    
    # Hitung rata-rata penurunan
    
    rata_rata_penurunan = total_penurunan / (banyak_data_ts - 1)
    persentase_penurunan = rata_rata_penurunan * 100

    print(f'out {index}:', ' | ', total_penurunan, ' | ', persentase_penurunan)
    
    return round(-persentase_penurunan, 2)

# print(existing_djm.loc[5])
# hitung_persentase_penurunan_lebih_dari_satu(5, existing_djm, 2024, 5.0)


# # Finish Table
# used_column = ['Fakultas', 'Prodi', 'Jenjang', 'Lembaga']
# existing_djm = existing_djm[used_column]

# 8. Prediksi setiap prodi
model = pickle.load(open(r"D:\jumapro\next_year_students_prediction.sav", "rb"))
# looping isi prediksi
model_results = {
    "index": [],
    "X": [],
    "Y":[]
}
# 7. Get Data Formula Pemantauan
# if input_formula == "Sudah Ada":
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
    existing_djm.at[index, 'Hasil Proyeksi Prediksi Pemantauan'] = f"Lebih dari {input_years_to_predict} Tahun ke Depan"
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
        # input_ambang_batas_jumlah = selected_formula["Ambang Batas (Jumlah)"]
        
        # print('Y:', column_name+1, existing_djm.at[index, column_name+1])

        # Perbarui current_students untuk iterasi berikutnya
        # current_students = prediksi_mahasiswa

        # Cek apakah jumlah mahasiswa di bawah ambang batas untuk kriteria Jumlah Mahasiswa
        
        
        
        
        if (not tahun_tidak_lolos_found) and (input_kriteria=='Jumlah Mahasiswa') and (prediksi_mahasiswa<input_ambang_batas_jumlah):
            existing_djm.at[index, 'Hasil Proyeksi Prediksi Pemantauan'] = next_year+1
            tahun_tidak_lolos_found = True
            
        print('loop:', prediksi_mahasiswa, input_ambang_batas_jumlah, tahun_tidak_lolos_found, input_kriteria, existing_djm.at[index, 'Hasil Proyeksi Prediksi Pemantauan'])    

            # Cek apakah jumlah mahasiswa di bawah ambang batas untuk kriteria Persentase Penurunan
                
                
            

    
    if input_kriteria == "Persentase Penurunan":
        print(index, 'PERSENTASE PENURUNAN')
        input_ambang_batas_persen = existing_formula[(existing_formula['Nama Rumus'] == selected_formulas_lembaga[existing_djm.at[index, 'Lembaga']]) & (existing_formula['Lembaga'] == existing_djm.at[index, 'Lembaga'])].iloc[0]['Ambang Batas (%)']
        input_ambang_batas_persen = 0 if np.isnan(input_ambang_batas_persen) else input_ambang_batas_persen
        input_banyak_data_ts = selected_formula["Banyak Data TS"]
        input_ambang_batas_jumlah = None
        input_fields = {}
        selected_formula = existing_formula[(existing_formula['Nama Rumus'] == selected_formulas_lembaga[lembaga_prodi]) & (existing_formula['Lembaga'] == lembaga_prodi)].iloc[0]
        
        
        for i in range(int(input_banyak_data_ts)-1):
            field_name = f"input_jumlah_mahasiswa_ts{i}"            
            try:
                input_fields[field_name] = existing_djm[str(input_predict_year-i-1)]
                # print(f'jmlh {i} | {field_name} | {input_predict_year-i} | { existing_djm[input_predict_year-i]}')
            except KeyError:
                # MUNGKIN datanya ga cukup, misal pilih 2014, tapi datanya cmn ada dari 2013, trus ambil -3 tahun
                raise ValueError("TAHUNNYA KURANG BRO")    
    

        # dari looping function
        input_ambang_batas_persen = existing_formula[(existing_formula['Nama Rumus'] == selected_formulas_lembaga[existing_djm.at[index, 'Lembaga']]) & (existing_formula['Lembaga'] == existing_djm.at[index, 'Lembaga'])].iloc[0]['Ambang Batas (%)']
        input_ambang_batas_persen = 0 if np.isnan(input_ambang_batas_persen) else input_ambang_batas_persen
        
        if input_banyak_data_ts > 2:
            persentase_penurunan = hitung_persentase_penurunan_lebih_dari_satu(index, existing_djm, input_predict_year, input_banyak_data_ts)
        else:
            persentase_penurunan = hitung_persentase_penurunan(existing_djm, input_predict_year)
            
        # existing_djm.at[index, 'Hitung Persentase Penurunan'] = persentase_penurunan
        #print('persentase penurunan:', persentase_penurunan)
        # hasil_prediksi_pemantauan = "Lolos" if persentase_penurunan.values[0] <= input_ambang_batas_persen else "Tidak Lolos"
        # hasil_prediksi_pemantauan = str(("Lolos" if persentase_penurunan <= input_ambang_batas_persen else "Tidak Lolos"))
        #"Lolos" if float(persentase_penurunan.iloc[1]) <= input_ambang_batas_persen else "Tidak Lolos"
        # convert_percent_to_ambang_batas_jumlah_mahasiswa = int(row[str(input_last_year)] * (1 - input_ambang_batas_persen / 100))
        # ambang_batas_jumlah_mahasiswa = int(data_prodi["current_students"] * (1 - input_ambang_batas_persen / 100))
        existing_djm.at[index, "Persentase Penurunan Maksimal"] = f"{input_ambang_batas_persen}%"
        # existing_djm.at[index, "Ambang Batas Jumlah Mahasiswa Minimal"] = convert_percent_to_ambang_batas_jumlah_mahasiswa
        # existing_djm.at[index, f"Hasil Prediksi Pemantauan ({input_predict_year})"] = hasil_prediksi_pemantauan
        # existing_djm.at[index, "Persentase Penurunan Maksimal"]
        # print(f'row existing djm at index {index}: ', existing_djm.loc[index])
        existing_djm.at[index, "Ambang Batas Jumlah Mahasiswa Minimal"] = None
        for col, value in input_fields.items():
            if col!="input_jumlah_mahasiswa_ts0":
                existing_djm[col] = value
        ts = [f"input_jumlah_mahasiswa_ts{i}" for i in range(1, int(input_banyak_data_ts-1))]
        ts = sorted(ts, reverse=True)
        
     
    elif input_kriteria == "Jumlah Mahasiswa":
        print(index, 'JUMLAH MAHASISWA')
        
        # input_jumlah_mahasiswa_ts = None
        # print('comparasion prediksi pemantauan:', existing_djm.at[index, str(input_predict_year)], input_ambang_batas_jumlah, input_predict_year)

        existing_djm.at[index, 'Hitung Persentase Penurunan'] = None
        existing_djm.at[index, "Persentase Penurunan Maksimal"] = None
        hasil_prediksi_pemantauan = str(("Lolos" if existing_djm.at[index, str(input_predict_year)] >= input_ambang_batas_jumlah else "Tidak Lolos"))
        input_ambang_batas_persen = None
        input_fields = None
        existing_djm.at[index, f"Hasil Prediksi Pemantauan ({input_predict_year})"] = hasil_prediksi_pemantauan
        existing_djm.at[index, "Ambang Batas Jumlah Mahasiswa Minimal"] = input_ambang_batas_jumlah
        ts = []


ordered_data_prodi = ["Prodi"] + ["Jenjang"] + ["Lembaga"] +  ["Kriteria Input"] + ts + [f"{input_last_year}"] + data_predict_target + ["Hitung Persentase Penurunan"] +  ["Persentase Penurunan Maksimal"]  + ["Ambang Batas Jumlah Mahasiswa Minimal"] +  [f"Hasil Prediksi Pemantauan ({input_predict_year})"] + ["Ambang Batas Jumlah Mahasiswa Minimal"] + data_predict_years + ['Hasil Proyeksi Prediksi Pemantauan']
tampil_data_prodi = existing_djm[ordered_data_prodi]
tampil_data_prodi.rename(columns={'current_students': f'{input_last_year} (Saat Ini)'}, inplace=True)
rename_ts = {f"input_jumlah_mahasiswa_ts{i+1}": f"{input_last_year-i-1}" for i in range(int(input_banyak_data_ts-1))}
tampil_data_prodi.rename(columns=rename_ts, inplace=True)
tampil_data_prodi.rename(columns={'current_students': f'{input_last_year} (Saat Ini)'}, inplace=True)


existing_djm
# tampil_data_prodi
# existing_formula


ts = [f"input_jumlah_mahasiswa_ts{i}" for i in range(1, int(input_banyak_data_ts-1))]
ts = sorted(ts, reverse=True)
data_predict_years = [f"{next_year}" for next_year in range(input_predict_year+1, input_predict_year+input_years_to_predict)]
data_predict_target= [f"{input_predict_year}"]
ordered_data_prodi = ["Prodi"] + ["Jenjang"] + ["Lembaga"] +  ["Kriteria Input"] + ts + [f"{input_last_year}"] + data_predict_target + ["Hitung Persentase Penurunan"] +  ["Persentase Penurunan Maksimal"]  + ["Ambang Batas Jumlah Mahasiswa Minimal"] +  [f"Hasil Prediksi Pemantauan ({input_predict_year})"] + ["Ambang Batas Jumlah Mahasiswa Minimal"] + data_predict_years + ['Hasil Proyeksi Prediksi Pemantauan']
tampil_data_prodi = existing_djm[ordered_data_prodi]
tampil_data_prodi.rename(columns={'current_students': f'{input_last_year} (Saat Ini)'}, inplace=True)
rename_ts = {f"input_jumlah_mahasiswa_ts{i+1}": f"{input_last_year-i-1}" for i in range(int(input_banyak_data_ts-1))}
tampil_data_prodi.rename(columns=rename_ts, inplace=True)
tampil_data_prodi.rename(columns={'current_students': f'{input_last_year} (Saat Ini)'}, inplace=True)

