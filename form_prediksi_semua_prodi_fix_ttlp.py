import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pickle
import pandas as pd
import numpy as np

# Halaman Prediksi Suatu Prodi
st.title("Halaman Prediksi Semua Prodi Dengan Formula")


# Establishing a Google Sheets connection
# conn = st.connection("gsheets", type=GSheetsConnection)

# Fetch data dhp = data history prediction
# existing_dhp = conn.read(worksheet="Data Histori Prediksi Suatu Prodi", ttl=5)
# with open('existing_dhp.pickle', 'wb') as handle:
#     pickle.dump(existing_dhp, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open('existing_dhp.pickle', 'rb') as handle:
    existing_dhp = pickle.load(handle)

existing_dhp = existing_dhp.dropna(how="all")

# Fetch data djm = data jumlah mahasiswa
# existing_djm = conn.read(worksheet="Data Jumlah Mahasiswa")
# with open('existing_djm.pickle', 'wb') as handle:
#     pickle.dump(existing_djm, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open('existing_djm.pickle', 'rb') as handle:
    existing_djm = pickle.load(handle)

existing_djm = existing_djm.dropna(how="all")
existing_djm = existing_djm.replace('#N/A ()', 0)

# Fetch existing formulas data
# existing_formula = conn.read(worksheet="Rumus Pemantauan", usecols=list(range(7)), ttl=5)
# with open('existing_formula.pickle', 'wb') as handle:
#     pickle.dump(existing_formula, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open('existing_formula.pickle', 'rb') as handle:
    existing_formula = pickle.load(handle)

existing_formula = existing_formula.dropna(how="all")

# Dropdown options for Lembaga
lembaga_options = existing_djm['Lembaga'].unique()
formula_options = existing_formula['Nama Rumus'].unique()

unused_column = ['Kode Prodi', 'Kode Prodi UGM', 'Kode Fakultas', 'Program Studi', 'BAN PT', 'Departemen', 'Kluster', 'PDDIKTI x BAN']
djm = existing_djm.drop(unused_column, axis=1)

st.write(djm)
# Input fields
# input_prodi = st.text_input("Masukkan Nama Program Studi : ")
input_prodi = existing_djm["Prodi"]

# CRUD Form
max_value = int(existing_djm.columns[-1])
min_value = int(existing_djm.columns[12])

input_predict_year = st.slider("Masukkan Tahun yang Ingin Diprediksi (ex: 2025) : ", min_value=min_value+6, max_value=max_value+1)
input_last_year = input_predict_year - 1

input_years_to_predict = st.slider("Masukkan Proyeksi Prediksi (Dalam Satuan Tahun) : ", min_value=1, max_value=10)

input_formula = st.radio("Formula yang Digunakan", ["Sudah Ada", "Baru"])


model = pickle.load(open(r"D:\jumapro\next_year_students_prediction.sav", "rb"))


print('existing formula:', existing_formula)
selected_formulas = {}
if input_formula == "Sudah Ada":
    for lembaga_name in lembaga_options:
        # Filter formulas by the selected Lembaga
        formula_options = existing_formula[existing_formula['Lembaga'] == lembaga_name]['Nama Rumus'].unique()

        # Dropdown to select formula for the current Lembaga
        selected_formulas[lembaga_name] = st.selectbox(f"Pilih Rumus yang Digunakan bagi Prodi di bawah Lembaga {lembaga_name} : ", formula_options)
        selected_formulas_name = existing_formula[(existing_formula['Nama Rumus'] == selected_formulas[lembaga_name]) & (existing_formula['Lembaga'] == lembaga_name)].iloc[0]
        st.write(selected_formulas_name)

            
    print('selected_formulas:', selected_formulas)
    for index, row in existing_djm.iterrows():
        lembaga_prodi = row['Lembaga']
        prodi_name = row['Prodi']

            
        # Mengambil baris formula yang dipilih
        selected_formula = existing_formula[(existing_formula['Nama Rumus'] == selected_formulas[lembaga_prodi]) & (existing_formula['Lembaga'] == lembaga_prodi)].iloc[0]
        
        # st.write(selected_formula)
        # Cek kriteria
        input_kriteria = selected_formula["Kriteria"]

        

        if input_kriteria == "Persentase Penurunan":
            # input_ambang_batas_persen = selected_formula["Ambang Batas (%)"]
            input_ambang_batas_persen = existing_formula[(existing_formula['Nama Rumus'] == selected_formulas[existing_djm.at[index, 'Lembaga']]) & (existing_formula['Lembaga'] == existing_djm.at[index, 'Lembaga'])].iloc[0]['Ambang Batas (%)']
            input_ambang_batas_persen = 0 if np.isnan(input_ambang_batas_persen) else input_ambang_batas_persen
            input_banyak_data_ts = selected_formula["Banyak Data TS"]
            input_ambang_batas_jumlah = None
            input_fields = {}
            for i in range(int(input_banyak_data_ts)):
                field_name = f"input_jumlah_mahasiswa_ts{i}"
                # input_fields[field_name] = st.number_input(f"Masukkan Jumlah Mahasiswa TS-{i}:", value=0)
                try:
                    input_fields[field_name] = existing_djm[input_predict_year-i-1]
                    # print(f'jmlh {i} | {field_name} | {input_predict_year-i} | { existing_djm[input_predict_year-i]}')
                except KeyError:
                    # MUNGKIN datanya ga cukup, misal pilih 2014, tapi datanya cmn ada dari 2013, trus ambil -3 tahun
                    # input_fields[field_name] = 1
                    raise ValueError("TAHUNNYA KURANG BRO")
                

        else:
            input_ambang_batas_jumlah = selected_formula["Ambang Batas (Jumlah)"]
            # input_jumlah_mahasiswa_ts = None
            input_ambang_batas_persen = None
            input_fields = None
            # # Calculate predictions
            # current_students = row[input_last_year]
            # tahun_tidak_lolos = f"Lebih dari {input_years_to_predict} Tahun ke Depan"  # Default value

            # for i in range(1, input_years_to_predict + 1):
            #     next_year = input_last_year + i
            #     column_name = f'{next_year} (Prediksi)'

            #     # Lakukan prediksi menggunakan model untuk current_students dari baris ini
            #     prediksi_mahasiswa = model.predict([[current_students]])[0]
            #     existing_djm.at[index, column_name] = int(prediksi_mahasiswa)

            #     # Perbarui current_students untuk iterasi berikutnya
            #     current_students = prediksi_mahasiswa

            #     # Cek apakah jumlah mahasiswa di bawah ambang batas
            #     if prediksi_mahasiswa < input_ambang_batas_jumlah:
            #         tahun_tidak_lolos = next_year
            # print('after milih jumlah mahasiswa, sudah menghitung variable tahun_tidak_lolos: ', tahun_tidak_lolos)
            # existing_djm.at[index, f"Hasil Prediksi Pemantauan ({input_predict_year})"] = "Lolos" if prediksi_mahasiswa >= input_ambang_batas_jumlah else "Tidak Lolos"
else:
    input_kriteria = st.radio("Kriteria", ["Jumlah Mahasiswa", "Persentase Penurunan"])
    if input_kriteria == "Persentase Penurunan":
        input_ambang_batas_persen = st.slider("Ambang Batas Persentase Maksimal (%)", min_value=1, max_value=100, step=1)
        input_banyak_data_ts = st.slider("Masukkan Banyak Tahun yang Dipakai untuk Persentase Penurunan : ", min_value=2, max_value=5, step=1)
        input_ambang_batas_jumlah = None

        input_fields = {}
        for i in range(input_banyak_data_ts - 1):
            field_name = f"input_jumlah_mahasiswa_ts{i}"
            input_fields[field_name] = existing_djm[input_predict_year-i-1]

            
                
    else:
        input_ambang_batas_jumlah = st.number_input("Ambang Batas Jumlah Mahasiswa Minimal", min_value=1, step=1)
        input_jumlah_mahasiswa_ts = existing_djm[input_predict_year-1]
        input_ambang_batas_persen = None
        input_fields = None

model = pickle.load(open(r"D:\jumapro\next_year_students_prediction.sav", "rb"))

# existing_djm = existing_djm.dropna()
# if input_kriteria == "Jumlah Mahasiswa":
existing_djm.rename(columns={input_last_year:"current_students"}, inplace=True)
#     new_data_prodi = {
#         'Prodi': [input_prodi],
#         'current_students': [input_jumlah_mahasiswa_ts]
#     }
# else:
#     new_data_prodi = {
#         'Prodi': [input_prodi],
#         'current_students': [input_fields[list(input_fields.keys())[0]]]
#     }

# data_prodi = pd.DataFrame(new_data_prodi)
all_tahun_tidak_lolos = dict()
# Prediksi beberapa tahun ke depan
for index, row in existing_djm.iterrows():
    # Ambil data current_students dari baris saat ini
    current_students = row['current_students']
    tahun_tidak_lolos = f"Lebih dari {input_years_to_predict} Tahun ke Depan"  # Default value

    for i in range(1, input_years_to_predict + 1):
        next_year = input_last_year + i
        column_name = f'{next_year} (Prediksi)'

        # Lakukan prediksi menggunakan model untuk current_students dari baris ini
        prediksi_mahasiswa = model.predict([[current_students]])[0]
        existing_djm.at[index, column_name] = int(prediksi_mahasiswa)

        # Perbarui current_students untuk iterasi berikutnya
        current_students = prediksi_mahasiswa

        # Cek apakah jumlah mahasiswa di bawah ambang batas untuk kriteria Jumlah Mahasiswa
        if input_kriteria == "Jumlah Mahasiswa" and prediksi_mahasiswa < input_ambang_batas_jumlah:
            tahun_tidak_lolos = next_year

        # Cek apakah jumlah mahasiswa di bawah ambang batas untuk kriteria Persentase Penurunan
        elif input_kriteria == "Persentase Penurunan":
            ambang_batas_jumlah_mahasiswa = int(row["current_students"] * (1 - input_ambang_batas_persen / 100))
            if prediksi_mahasiswa < ambang_batas_jumlah_mahasiswa:
                tahun_tidak_lolos = next_year
        all_tahun_tidak_lolos[index] = tahun_tidak_lolos
        
    # Update kolom hasil pemantauan dan tahun tidak lolos
    if input_kriteria == "Jumlah Mahasiswa":
        existing_djm.at[index, f"Hasil Prediksi Pemantauan ({input_predict_year})"] = "Lolos" if prediksi_mahasiswa >= input_ambang_batas_jumlah else "Tidak Lolos"
    elif input_kriteria == "Persentase Penurunan":
        existing_djm.at[index, f"Hasil Prediksi Pemantauan ({input_predict_year})"] = "Lolos" if prediksi_mahasiswa >= ambang_batas_jumlah_mahasiswa else "Tidak Lolos"
    



data_predict_years = [f"{next_year} (Prediksi)" for next_year in range(input_predict_year+1, input_predict_year+input_years_to_predict)]
data_predict_target= [f"{input_predict_year} (Prediksi)"]

# Fungsi untuk menghitung persentase penurunan
def hitung_persentase_penurunan(data, predict_year):
    # data_mahasiswa_start_year = input_fields["input_jumlah_mahasiswa_ts0"]
    # end_year = predict_year
    # penurunan_total = (data[f"{end_year} (Prediksi)"] - data_mahasiswa_start_year)
    # persentase_penurunan = (penurunan_total / 2) * 100
    # return persentase_penurunan
    ts_1 = data[f"{predict_year} (Prediksi)"]
    ts_0 = data["current_students"]
    penurunan = (ts_0 - ts_1) / ts_1

    persentase_penurunan = penurunan * 100

    return persentase_penurunan

# print('input_fields:', input_fields)
# input_fields
# Fungsi untuk menghitung persentase penurunan dengan lebih dari satu tahun data
def hitung_persentase_penurunan_lebih_dari_satu(index, data, predict_year, banyak_data_ts):
    global input_fields

    total_penurunan = 0
    
    
    # Iterasi dari TS-1 hingga TS-n (n = banyak_data_ts)
    for i in range(int(banyak_data_ts) - 1):
        if i == 0:
            data = data.iloc[index]
            ts_1 = data[f"{predict_year} (Prediksi)"]
            ts_0 = data["current_students"]
        else:
            # input_fields = input_fields[]
            ts_1 = input_fields[f"input_jumlah_mahasiswa_ts{i}"][index]
            ts_0 = input_fields[f"input_jumlah_mahasiswa_ts{i-1}"][index]
            
        
        
       
        penurunan = (ts_0 - ts_1) / ts_1
        total_penurunan += penurunan
        (index, i, (ts_0), (ts_1))
    
    # print('data:', type(data))
    


       

    # Hitung rata-rata penurunan
    rata_rata_penurunan = total_penurunan / (banyak_data_ts - 1)
    persentase_penurunan = rata_rata_penurunan * 100

    # print(f'out {index}:', ' | ', total_penurunan, ' | ', persentase_penurunan)
    

    return persentase_penurunan

# Perbarui fungsi prediksi_dan_penilaian untuk menggunakan fungsi yang baru
# print('all tahun tidak lolos:', all_tahun_tidak_lolos)
def prediksi_dan_penilaian(input_prodi, input_predict_year, input_last_year_data, input_years_to_predict, input_kriteria, input_ambang_batas_jumlah, input_ambang_batas_persen, input_fields, existing_formula):
    # print('all args:')
    # print('input prodi:', type(input_prodi), input_prodi)
    args = input_predict_year, input_last_year_data, input_years_to_predict, input_kriteria, input_ambang_batas_jumlah, input_ambang_batas_persen
    print('args:', args)
    # print('input fields:', type(input_fields), input_fields)
    with open('input_fields.pkl', 'wb+') as file:
        pickle.dump(input_fields, file)
    with open('input_prodi.pkl', 'wb') as file:
        pickle.dump(input_prodi, file)     
    # print('export arg done')   
    # print('before loop, edjm length:', existing_djm.shape, len(existing_djm))
    # print('existing djm head: ', existing_djm.head())
    for index, row in existing_djm.iterrows():
        # print('LOOP BEFORE IF', index)
        # Penilaian kelolosan berdasarkan kriteria
        if input_kriteria == "Jumlah Mahasiswa":
            # print('looping jumlah mahasiswa', index)
            hasil_prediksi_pemantauan = "Lolos" if row[f"{input_predict_year} (Prediksi)"] > input_ambang_batas_jumlah else "Tidak Lolos"
            existing_djm.at[index, f"Hasil Prediksi Pemantauan ({input_predict_year})"] = hasil_prediksi_pemantauan
            # existing_djm[f"Hasil Prediksi Pemantauan ({input_predict_year})"] = hasil_prediksi_pemantauan
            existing_djm.at[index, "Jumlah Mahasiswa Minimal"] = input_ambang_batas_jumlah
            # existing_djm["Jumlah Mahasiswa Minimal"] = input_ambang_batas_jumlah
            existing_djm.at[index,"Tahun Tidak Lolos (Prediksi)"] = str(all_tahun_tidak_lolos[index])
            # existing_djm["Tahun Tidak Lolos (Prediksi)"] = str(tahun_tidak_lolos)

            ordered_data_prodi = ["Prodi"] + ["Lembaga"] + ["current_students"] + data_predict_target + ["Jumlah Mahasiswa Minimal"] + [f"Hasil Prediksi Pemantauan ({input_predict_year})"] + data_predict_years + ["Tahun Tidak Lolos (Prediksi)"]
            tampil_data_prodi = existing_djm[ordered_data_prodi]
            tampil_data_prodi.rename(columns={'current_students': f'{input_last_year} (Saat Ini)'}, inplace=True)

            # updated_dhp = pd.concat([existing_dhp, tampil_data_prodi], ignore_index=True)
            # conn.update(worksheet="Histori Prediksi Suatu Prodi", data=updated_dhp)

        elif input_kriteria == "Persentase Penurunan":
            # print('looping persentase penurunan', index)
            input_ambang_batas_persen = existing_formula[(existing_formula['Nama Rumus'] == selected_formulas[existing_djm.at[index, 'Lembaga']]) & (existing_formula['Lembaga'] == existing_djm.at[index, 'Lembaga'])].iloc[0]['Ambang Batas (%)']
            input_ambang_batas_persen = 0 if np.isnan(input_ambang_batas_persen) else input_ambang_batas_persen
            #print('input ambang batas persen:', input_ambang_batas_persen)
            if input_banyak_data_ts > 2:
                persentase_penurunan = hitung_persentase_penurunan_lebih_dari_satu(index, existing_djm, input_predict_year, input_banyak_data_ts)
            else:
                persentase_penurunan = hitung_persentase_penurunan(existing_djm, input_predict_year)
            
            existing_djm["Hitung Persentase Penurunan"] = persentase_penurunan
            #print('persentase penurunan:', persentase_penurunan)
            # hasil_prediksi_pemantauan = "Lolos" if persentase_penurunan.values[0] <= input_ambang_batas_persen else "Tidak Lolos"
            hasil_prediksi_pemantauan = str(("Lolos" if persentase_penurunan <= input_ambang_batas_persen else "Tidak Lolos"))
            #"Lolos" if float(persentase_penurunan.iloc[1]) <= input_ambang_batas_persen else "Tidak Lolos"
            
            convert_percent_to_ambang_batas_jumlah_mahasiswa = int(row["current_students"] * (1 - input_ambang_batas_persen / 100))
            # ambang_batas_jumlah_mahasiswa = int(data_prodi["current_students"] * (1 - input_ambang_batas_persen / 100))
            # existing_djm["Hitung Persentase Penurunan"] = persentase_penurunan
            existing_djm.at[index, "Persentase Penurunan Maksimal"] = f"{input_ambang_batas_persen}%"
            existing_djm.at[index, "Ambang Batas Jumlah Mahasiswa Minimal"] = convert_percent_to_ambang_batas_jumlah_mahasiswa
            existing_djm.at[index, f"Hasil Prediksi Pemantauan ({input_predict_year})"] = hasil_prediksi_pemantauan
            existing_djm.at[index, "Tahun Tidak Lolos (Prediksi)"] = str(all_tahun_tidak_lolos[index])
            existing_djm.at[index, "Persentase Penurunan Maksimal"]
            # print(f'row existing djm at index {index}: ', existing_djm.loc[index])
            for col, value in input_fields.items():
                if col!="input_jumlah_mahasiswa_ts0":
                    existing_djm[col] = value
            ts = [f"input_jumlah_mahasiswa_ts{i}" for i in range(1, int(input_banyak_data_ts-1))]
            ts = sorted(ts, reverse=True)

            ordered_data_prodi = ["Prodi"] + ["Lembaga"] + ts + ["current_students"] + data_predict_target + ["Persentase Penurunan Maksimal"] + ["Hitung Persentase Penurunan"] + [f"Hasil Prediksi Pemantauan ({input_predict_year})"] + ["Ambang Batas Jumlah Mahasiswa Minimal"] + data_predict_years + ["Tahun Tidak Lolos (Prediksi)"]
            tampil_data_prodi = existing_djm[ordered_data_prodi]
            tampil_data_prodi.rename(columns={'current_students': f'{input_last_year} (Saat Ini)'}, inplace=True)
            rename_ts = {f"input_jumlah_mahasiswa_ts{i+1}": f"{input_last_year-i-1}" for i in range(int(input_banyak_data_ts-1))}
            tampil_data_prodi.rename(columns=rename_ts, inplace=True)
            tampil_data_prodi.rename(columns={'current_students': f'{input_last_year_data} (Saat Ini)'}, inplace=True)

            # updated_dhp = pd.concat([existing_dhp, tampil_data_prodi], ignore_index=True)
            # conn.update(worksheet="Histori Prediksi Suatu Prodi", data=updated_dhp)
        else:
            print('Other ', index)

    return tampil_data_prodi
        # return existing_djm
    


# Tampilkan hasil prediksi dan penilaian jika tombol "Prediksi" ditekan
if st.button("Prediksi"):
    hasil_prediksi = prediksi_dan_penilaian(input_prodi, input_predict_year, input_last_year, input_years_to_predict, input_kriteria, input_ambang_batas_jumlah, input_ambang_batas_persen, input_fields, existing_formula)
    st.write(hasil_prediksi)
    st.success("Data berhasil ditambahkan ke worksheet!")

def show_page():
    st.write("Ini adalah halaman home")
    