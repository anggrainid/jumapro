import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pickle
import pandas as pd

# Halaman Prediksi Suatu Prodi
st.title("Halaman Prediksi Semua Prodi Dengan Formula")


# Establishing a Google Sheets connection
conn = st.connection("gsheets", type=GSheetsConnection)

# Fetch data dhp = data history prediction
existing_dhp = conn.read(worksheet="Data Histori Prediksi Suatu Prodi", ttl=5)
existing_dhp = existing_dhp.dropna(how="all")

# Fetch data djm = data jumlah mahasiswa
existing_djm = conn.read(worksheet="Data Jumlah Mahasiswa")
existing_djm = existing_djm.dropna(how="all")
existing_djm = existing_djm.replace('#N/A ()', 0)

# Fetch existing formulas data
existing_formula = conn.read(worksheet="Rumus Pemantauan", usecols=list(range(7)), ttl=5)
existing_formula = existing_formula.dropna(how="all")

# Dropdown options for Lembaga
lembaga_options = existing_djm['Lembaga'].unique() # kode lembaga
formula_options = existing_formula['Nama Rumus'].unique()

unused_column = ['Kode Prodi', 'Kode Prodi UGM', 'Kode Fakultas', 'Program Studi', 'BAN PT', 'Departemen', 'Kluster', 'PDDIKTI x BAN']
djm = existing_djm.drop(unused_column, axis=1)

djm
# Input fields
# input_prodi = st.text_input("Masukkan Nama Program Studi : ")
input_prodi = existing_djm["Prodi"] # kolom (banyak baris)

# CRUD Form
max_value = int(existing_djm.columns[-1]) # tahun terakhir (2023)
min_value = int(existing_djm.columns[12]) # tahun pertama (2013)

input_predict_year = st.slider("Masukkan Tahun yang Ingin Diprediksi (ex: 2025) : ", min_value=min_value+1, max_value=max_value+1)
input_last_year = input_predict_year - 1

input_years_to_predict = st.slider("Masukkan Proyeksi Prediksi (Dalam Satuan Tahun) : ", min_value=1, max_value=10)

input_formula = st.radio("Formula yang Digunakan", ["Sudah Ada", "Baru"])

model = pickle.load(open(r"next_year_students_prediction.sav", "rb"))


selected_formulas = {}
datas = {}
if input_formula == "Sudah Ada":
    # store selected formulas for each Lembaga to selected_formulas
    for lembaga_name in lembaga_options:
        # Filter formulas by the selected Lembaga
        formula_options = existing_formula[existing_formula['Lembaga'] == lembaga_name]['Nama Rumus'].unique()

        # Dropdown to select formula for the current Lembaga
        selected_formulas[lembaga_name] = st.selectbox(f"Pilih Rumus yang Digunakan bagi Prodi di bawah Lembaga {lembaga_name} : ", formula_options)
        selected_formulas_name = existing_formula[(existing_formula['Nama Rumus'] == selected_formulas[lembaga_name]) & (existing_formula['Lembaga'] == lembaga_name)].iloc[0]
        st.write(selected_formulas_name)

             
    for index, row in existing_djm.iterrows():
        data = {}
        lembaga_prodi = row['Lembaga']
        prodi_name = row['Prodi']

            
        # Mengambil baris formula yang dipilih
        selected_formula = existing_formula[(existing_formula['Nama Rumus'] == selected_formulas[lembaga_prodi]) & (existing_formula['Lembaga'] == lembaga_prodi)].iloc[0]

        # st.write(selected_formula)
        # Cek kriteria
        input_kriteria = selected_formula["Kriteria"]
        data['input_kriteria'] = input_kriteria

        if input_kriteria == "Persentase Penurunan":
            data['input_ambang_batas_persen'] = selected_formula["Ambang Batas (%)"]
            data['input_banyak_data_ts'] = selected_formula["Banyak Data TS"]
            data['input_ambang_batas_jumlah'] = None
            data['input_fields'] = {}
            for i in range(int(data['input_banyak_data_ts'] - 1)):
                field_name = f"input_jumlah_mahasiswa_ts{i}"
                # input_fields[field_name] = st.number_input(f"Masukkan Jumlah Mahasiswa TS-{i}:", value=0)
                data['input_fields'][field_name] = existing_djm[input_predict_year-1]

        # HANDLE LATER
        else:
            data['input_ambang_batas_persen'] = None
            data['input_jumlah_mahasiswa_ts'] = None
            data['input_ambang_batas_jumlah'] = selected_formula["Ambang Batas (Jumlah)"]
            data['input_fields'] = None
            # Calculate predictions
            current_students = row[input_last_year]
            tahun_tidak_lolos = f"Lebih dari {input_years_to_predict} Tahun ke Depan"  # Default value

            for i in range(1, input_years_to_predict + 1):
                next_year = input_last_year + i
                column_name = f'{next_year} (Prediksi)'

                # Lakukan prediksi menggunakan model untuk current_students dari baris ini
                prediksi_mahasiswa = model.predict([[current_students]])[0]
                existing_djm.at[index, column_name] = int(prediksi_mahasiswa)

                # Perbarui current_students untuk iterasi berikutnya
                current_students = prediksi_mahasiswa

                # Cek apakah jumlah mahasiswa di bawah ambang batas
                if prediksi_mahasiswa < data['input_ambang_batas_jumlah']:
                    tahun_tidak_lolos = next_year

            existing_djm.at[index, f"Hasil Prediksi Pemantauan ({input_predict_year})"] = "Lolos" if prediksi_mahasiswa >= data['input_ambang_batas_jumlah'] else "Tidak Lolos"
        
        datas[index] = data




# datas
# else:
#     input_kriteria = st.radio("Kriteria", ["Jumlah Mahasiswa", "Persentase Penurunan"])
#     if input_kriteria == "Persentase Penurunan":
#         input_ambang_batas_persen = st.slider("Ambang Batas Persentase Maksimal (%)", min_value=1, max_value=100, step=1)
#         input_banyak_data_ts = st.slider("Masukkan Banyak Tahun yang Dipakai untuk Persentase Penurunan : ", min_value=2, max_value=5, step=1)
#         input_ambang_batas_jumlah = None

#         input_fields = {}
#         for i in range(input_banyak_data_ts - 1):
#             field_name = f"input_jumlah_mahasiswa_ts{i}"
#             input_fields[field_name] = existing_djm[input_predict_year-1]
                
#     else:
#         input_ambang_batas_jumlah = st.number_input("Ambang Batas Jumlah Mahasiswa Minimal", min_value=1, step=1)
#         input_jumlah_mahasiswa_ts = existing_djm[input_predict_year-1]
#         input_ambang_batas_persen = None
#         input_fields = None

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

# Prediksi beberapa tahun ke depan
for index, row in existing_djm.iterrows():
    data = datas[index]
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
        if input_kriteria == "Jumlah Mahasiswa" and prediksi_mahasiswa < data['input_ambang_batas_jumlah']:
            tahun_tidak_lolos = next_year

        # Cek apakah jumlah mahasiswa di bawah ambang batas untuk kriteria Persentase Penurunan
        elif input_kriteria == "Persentase Penurunan":
            ambang_batas_jumlah_mahasiswa = int(row["current_students"] * (1 - data['input_ambang_batas_persen'] / 100))
            if prediksi_mahasiswa < ambang_batas_jumlah_mahasiswa:
                tahun_tidak_lolos = next_year

    # Update kolom hasil pemantauan dan tahun tidak lolos
    if input_kriteria == "Jumlah Mahasiswa":
        existing_djm.at[index, f"Hasil Prediksi Pemantauan ({input_predict_year})"] = "Lolos" if prediksi_mahasiswa >= data['input_ambang_batas_jumlah'] else "Tidak Lolos"
    elif input_kriteria == "Persentase Penurunan":
        existing_djm.at[index, f"Hasil Prediksi Pemantauan ({input_predict_year})"] = "Lolos" if prediksi_mahasiswa >= ambang_batas_jumlah_mahasiswa else "Tidak Lolos"
    

data

data_predict_years = [f"{next_year} (Prediksi)" for next_year in range(input_predict_year+1, input_predict_year+input_years_to_predict)]
data_predict_target= [f"{input_predict_year} (Prediksi)"]

# Fungsi untuk menghitung persentase penurunan
def hitung_persentase_penurunan(df, predict_year):
    # data_mahasiswa_start_year = input_fields["input_jumlah_mahasiswa_ts0"]
    # end_year = predict_year
    # penurunan_total = (data[f"{end_year} (Prediksi)"] - data_mahasiswa_start_year)
    # persentase_penurunan = (penurunan_total / 2) * 100
    # return persentase_penurunan
    ts_1 = df[f"{predict_year} (Prediksi)"]
    ts_0 = df["current_students"]
    penurunan = (ts_0 - ts_1) / ts_1

    persentase_penurunan = penurunan * 100

    return persentase_penurunan


# Fungsi untuk menghitung persentase penurunan dengan lebih dari satu tahun data
def hitung_persentase_penurunan_lebih_dari_satu(df, predict_year, data):
    total_penurunan = 0

    # Iterasi dari TS-1 hingga TS-n (n = banyak_data_ts)
    for i in range(int(data['input_banyak_data_ts']) - 1):
        if i == 0:
            ts_1 = df[f"{predict_year} (Prediksi)"]
            ts_0 = df["current_students"]
        else:
            ts_1 = data['input_fields'][f"input_jumlah_mahasiswa_ts{i-1}"]
            ts_0 = data['input_fields'][f"input_jumlah_mahasiswa_ts{i}"]

        penurunan = (ts_0 - ts_1) / ts_1
        total_penurunan += penurunan

    # Hitung rata-rata penurunan
    rata_rata_penurunan = total_penurunan / (data['input_banyak_data_ts'] - 1)
    persentase_penurunan = rata_rata_penurunan * 100

    return persentase_penurunan

# Perbarui fungsi prediksi_dan_penilaian untuk menggunakan fungsi yang baru

def prediksi_dan_penilaian(input_prodi, input_predict_year, input_last_year_data, input_years_to_predict, datas):
    for index, row in existing_djm.iterrows():
        data = datas[index]
        # Penilaian kelolosan berdasarkan kriteria
        if data['input_kriteria'] == "Jumlah Mahasiswa":
            hasil_prediksi_pemantauan = "Lolos" if row[f"{input_predict_year} (Prediksi)"] > data['input_ambang_batas_jumlah'] else "Tidak Lolos"
            existing_djm.at[index, f"Hasil Prediksi Pemantauan ({input_predict_year})"] = hasil_prediksi_pemantauan
            # existing_djm[f"Hasil Prediksi Pemantauan ({input_predict_year})"] = hasil_prediksi_pemantauan
            existing_djm.at[index, "Jumlah Mahasiswa Minimal"] = data['input_ambang_batas_jumlah']
            # existing_djm["Jumlah Mahasiswa Minimal"] = input_ambang_batas_jumlah
            existing_djm.at[index,"Tahun Tidak Lolos (Prediksi)"] = str(tahun_tidak_lolos)
            # existing_djm["Tahun Tidak Lolos (Prediksi)"] = str(tahun_tidak_lolos)

            ordered_data_prodi = ["Prodi"] + ["Lembaga"] + ["current_students"] + data_predict_target + ["Jumlah Mahasiswa Minimal"] + [f"Hasil Prediksi Pemantauan ({input_predict_year})"] + data_predict_years + ["Tahun Tidak Lolos (Prediksi)"]
            tampil_data_prodi = existing_djm[ordered_data_prodi]
            tampil_data_prodi.rename(columns={'current_students': f'{input_last_year} (Saat Ini)'}, inplace=True)

            # updated_dhp = pd.concat([existing_dhp, tampil_data_prodi], ignore_index=True)
            # conn.update(worksheet="Histori Prediksi Suatu Prodi", data=updated_dhp)

        elif data['input_kriteria'] == "Persentase Penurunan":

            if data['input_banyak_data_ts'] > 2:
                persentase_penurunan = hitung_persentase_penurunan_lebih_dari_satu(existing_djm, input_predict_year, data)
            else:
                persentase_penurunan = hitung_persentase_penurunan(existing_djm, input_predict_year)
            
            existing_djm["Hitung Persentase Penurunan"] = persentase_penurunan
            # hasil_prediksi_pemantauan = "Lolos" if persentase_penurunan.values[0] <= input_ambang_batas_persen else "Tidak Lolos"
            hasil_prediksi_pemantauan = "Lolos" if persentase_penurunan.values[0] <= data['input_ambang_batas_persen'] else "Tidak Lolos"
            
            convert_percent_to_ambang_batas_jumlah_mahasiswa = int(row["current_students"] * (1 - data['input_ambang_batas_persen'] / 100))
            # ambang_batas_jumlah_mahasiswa = int(data_prodi["current_students"] * (1 - input_ambang_batas_persen / 100))
            # existing_djm["Hitung Persentase Penurunan"] = persentase_penurunan
            existing_djm.at[index, "Persentase Penurunan Maksimal"] = f"{data['input_ambang_batas_persen']}%"
            existing_djm.at[index, "Ambang Batas Jumlah Mahasiswa Minimal"] = convert_percent_to_ambang_batas_jumlah_mahasiswa
            existing_djm.at[index, f"Hasil Prediksi Pemantauan ({input_predict_year})"] = hasil_prediksi_pemantauan
            existing_djm.at[index, "Tahun Tidak Lolos (Prediksi)"] = str(tahun_tidak_lolos)
        
            for col, value in data['input_fields'].items():
                if col!="input_jumlah_mahasiswa_ts0":
                    existing_djm[col] = value
            ts = [f"input_jumlah_mahasiswa_ts{i}" for i in range(1, int(data['input_banyak_data_ts']-1))]
            ts = sorted(ts, reverse=True)

            ordered_data_prodi = ["Prodi"] + ["Lembaga"] + ts + ["current_students"] + data_predict_target + ["Persentase Penurunan Maksimal"] + ["Hitung Persentase Penurunan"] + [f"Hasil Prediksi Pemantauan ({input_predict_year})"] + ["Ambang Batas Jumlah Mahasiswa Minimal"] + data_predict_years + ["Tahun Tidak Lolos (Prediksi)"]
            ordered_data_prodi
            tampil_data_prodi = existing_djm[ordered_data_prodi]
            tampil_data_prodi
            tampil_data_prodi.rename(columns={'current_students': f'{input_last_year} (Saat Ini)'}, inplace=True)
            rename_ts = {f"input_jumlah_mahasiswa_ts{i+1}": f"{input_last_year-i-1}" for i in range(int(data['input_banyak_data_ts']-1))}
            tampil_data_prodi.rename(columns=rename_ts, inplace=True)
            tampil_data_prodi.rename(columns={'current_students': f'{input_last_year_data} (Saat Ini)'}, inplace=True)
            existing_djm
            # updated_dhp = pd.concat([existing_dhp, tampil_data_prodi], ignore_index=True)
            # conn.update(worksheet="Histori Prediksi Suatu Prodi", data=updated_dhp)

        return tampil_data_prodi
    


# Tampilkan hasil prediksi dan penilaian jika tombol "Prediksi" ditekan
if st.button("Prediksi"):
    hasil_prediksi = prediksi_dan_penilaian(input_prodi, input_predict_year, input_last_year, input_years_to_predict, datas)
    st.write(hasil_prediksi)
    st.success("Data berhasil ditambahkan ke worksheet!")