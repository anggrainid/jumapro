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
formula_options = existing_formula['Nama Rumus'].unique()

# Input fields
# input_prodi = st.text_input("Masukkan Nama Program Studi : ")
input_prodi = existing_djm["Prodi"]

input_predict_year = st.number_input("Masukkan Tahun yang Ingin Diprediksi (ex: 2025) : ", min_value=2024)
input_last_year = input_predict_year - 1

input_years_to_predict = st.number_input("Masukkan Proyeksi Prediksi (Dalam Satuan Tahun) : ", min_value=1, max_value=10)

input_formula = st.radio("Formula yang Digunakan", ["Sudah Ada", "Baru"])

if input_formula == "Sudah Ada":
    input_existing_formula = st.selectbox("Pilih Rumus yang Digunakan : ", formula_options)
    # Mengambil baris formula yang dipilih
    selected_formula = existing_formula[existing_formula['Nama Rumus'] == input_existing_formula].iloc[0]
    st.write(selected_formula)
    # Cek kriteria
    input_kriteria = selected_formula["Kriteria"]
    if input_kriteria == "Persentase Penurunan":
        input_ambang_batas_persen = selected_formula["Ambang Batas (%)"]
        input_banyak_data_ts = selected_formula["Banyak Data TS"]
        input_ambang_batas_jumlah = None

        input_fields = {}
        for i in range(int(input_banyak_data_ts-1)):
            field_name = f"input_jumlah_mahasiswa_ts{i}"
            # input_fields[field_name] = st.number_input(f"Masukkan Jumlah Mahasiswa TS-{i}:", value=0)
            input_fields[field_name] = existing_djm[input_predict_year-1]

    else:
        input_ambang_batas_jumlah = selected_formula["Ambang Batas (Jumlah)"]
        # input_jumlah_mahasiswa_ts = st.number_input(f"Masukkan Jumlah Mahasiswa TS:", value=0)
        input_jumlah_mahasiswa_ts = existing_djm[input_predict_year-1]
        input_ambang_batas_persen = None
        input_fields = None

else:
    input_kriteria = st.radio("Kriteria", ["Jumlah Mahasiswa", "Persentase Penurunan"])
    if input_kriteria == "Persentase Penurunan":
        input_ambang_batas_persen = st.slider("Ambang Batas Persentase Maksimal (%)", min_value=1, max_value=100, step=1)
        input_banyak_data_ts = st.slider("Masukkan Banyak Tahun yang Dipakai untuk Persentase Penurunan : ", min_value=2, max_value=5, step=1)
        input_ambang_batas_jumlah = None

        input_fields = {}
        for i in range(input_banyak_data_ts - 1):
            field_name = f"input_jumlah_mahasiswa_ts{i}"
            input_fields[field_name] = existing_djm[input_predict_year-1]
                
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

# Prediksi beberapa tahun ke depan

current_students = existing_djm['current_students'].copy()

tahun_tidak_lolos = f"Lebih dari {input_years_to_predict} Tahun ke Depan"  # Default value

for i in range(1, input_years_to_predict + 1):
    next_year = input_last_year + i
    column_name = f'{next_year} (Prediksi)'

    # Lakukan prediksi menggunakan nilai di current_students
    
    
    existing_djm[column_name] = model.predict(current_students.values.reshape(-1, 1))
    existing_djm[column_name] = existing_djm[column_name].astype(int)

     # Gunakan hasil prediksi tahun ini sebagai current_students untuk prediksi tahun berikutnya
    current_students = existing_djm[column_name].copy()
    
    if tahun_tidak_lolos == f"Lebih dari {input_years_to_predict} Tahun ke Depan":  # Only update if no year has been set yet
        if input_kriteria == "Jumlah Mahasiswa":
            if existing_djm[column_name].values[0] < input_ambang_batas_jumlah:
                tahun_tidak_lolos = next_year
                
        elif input_kriteria == "Persentase Penurunan":
            ambang_batas_jumlah_mahasiswa = int(existing_djm["current_students"].values[0] * (1 - input_ambang_batas_persen / 100))
            if existing_djm[column_name].values[0] < ambang_batas_jumlah_mahasiswa:
                tahun_tidak_lolos = next_year





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


# Fungsi untuk menghitung persentase penurunan dengan lebih dari satu tahun data
def hitung_persentase_penurunan_lebih_dari_satu(data, predict_year, banyak_data_ts):
    total_penurunan = 0

    # Iterasi dari TS-1 hingga TS-n (n = banyak_data_ts)
    for i in range(int(banyak_data_ts) - 1):
        if i == 0:
            ts_1 = data[f"{predict_year} (Prediksi)"]
            ts_0 = data["current_students"]
        else:
            ts_1 = input_fields[f"input_jumlah_mahasiswa_ts{i-1}"]
            ts_0 = input_fields[f"input_jumlah_mahasiswa_ts{i}"]

        penurunan = (ts_0 - ts_1) / ts_1
        total_penurunan += penurunan

    # Hitung rata-rata penurunan
    rata_rata_penurunan = total_penurunan / (banyak_data_ts - 1)
    persentase_penurunan = rata_rata_penurunan * 100

    return persentase_penurunan

# Perbarui fungsi prediksi_dan_penilaian untuk menggunakan fungsi yang baru

def prediksi_dan_penilaian(input_prodi, input_predict_year, input_last_year_data, input_years_to_predict, input_kriteria, input_ambang_batas_jumlah, input_ambang_batas_persen, input_fields):

    # Penilaian kelolosan berdasarkan kriteria
    if input_kriteria == "Jumlah Mahasiswa":
        hasil_prediksi_pemantauan = "Lolos" if existing_djm[f"{input_predict_year} (Prediksi)"].values[0] > input_ambang_batas_jumlah else "Tidak Lolos"
        existing_djm["Jumlah Mahasiswa Minimal"] = input_ambang_batas_jumlah
        existing_djm[f"Hasil Prediksi Pemantauan ({input_predict_year})"] = hasil_prediksi_pemantauan
        existing_djm["Tahun Tidak Lolos (Prediksi)"] = str(tahun_tidak_lolos)

        ordered_data_prodi = ["Prodi"] + ["current_students"] + data_predict_target + ["Jumlah Mahasiswa Minimal"] + [f"Hasil Prediksi Pemantauan ({input_predict_year})"] + data_predict_years + ["Tahun Tidak Lolos (Prediksi)"]
        tampil_data_prodi = existing_djm[ordered_data_prodi]
        tampil_data_prodi.rename(columns={'current_students': f'{input_last_year} (Saat Ini)'}, inplace=True)

        # updated_dhp = pd.concat([existing_dhp, tampil_data_prodi], ignore_index=True)
        # conn.update(worksheet="Histori Prediksi Suatu Prodi", data=updated_dhp)

    elif input_kriteria == "Persentase Penurunan":

        if input_banyak_data_ts > 2:
            persentase_penurunan = hitung_persentase_penurunan_lebih_dari_satu(existing_djm, input_predict_year, input_banyak_data_ts)
        else:
            persentase_penurunan = hitung_persentase_penurunan(existing_djm, input_predict_year)
        
        hasil_prediksi_pemantauan = "Lolos" if persentase_penurunan.values[0] <= input_ambang_batas_persen else "Tidak Lolos"
        
        
        convert_percent_to_ambang_batas_jumlah_mahasiswa = int(existing_djm["current_students"].values[0] * (1 - input_ambang_batas_persen / 100))
        # ambang_batas_jumlah_mahasiswa = int(data_prodi["current_students"] * (1 - input_ambang_batas_persen / 100))
        existing_djm["Hitung Persentase Penurunan"] = persentase_penurunan
        existing_djm["Persentase Penurunan Maksimal"] = f"{input_ambang_batas_persen}%"
        existing_djm["Ambang Batas Jumlah Mahasiswa Minimal"] = convert_percent_to_ambang_batas_jumlah_mahasiswa
        existing_djm[f"Hasil Prediksi Pemantauan ({input_predict_year})"] = hasil_prediksi_pemantauan
        existing_djm["Tahun Tidak Lolos (Prediksi)"] = str(tahun_tidak_lolos)
    
        for col, value in input_fields.items():
            if col!="input_jumlah_mahasiswa_ts0":
                existing_djm[col] = value
        ts = [f"input_jumlah_mahasiswa_ts{i}" for i in range(1, int(input_banyak_data_ts-1))]
        ts = sorted(ts, reverse=True)

        ordered_data_prodi = ["Prodi"] + ts + ["current_students"] + data_predict_target + ["Persentase Penurunan Maksimal"] + ["Hitung Persentase Penurunan"] + [f"Hasil Prediksi Pemantauan ({input_predict_year})"] + ["Ambang Batas Jumlah Mahasiswa Minimal"] + data_predict_years + ["Tahun Tidak Lolos (Prediksi)"]
        tampil_data_prodi = existing_djm[ordered_data_prodi]
        tampil_data_prodi.rename(columns={'current_students': f'{input_last_year} (Saat Ini)'}, inplace=True)
        rename_ts = {f"input_jumlah_mahasiswa_ts{i+1}": f"{input_last_year-i-1}" for i in range(int(input_banyak_data_ts-1))}
        tampil_data_prodi.rename(columns=rename_ts, inplace=True)
        tampil_data_prodi.rename(columns={'current_students': f'{input_last_year_data} (Saat Ini)'}, inplace=True)

        # updated_dhp = pd.concat([existing_dhp, tampil_data_prodi], ignore_index=True)
        # conn.update(worksheet="Histori Prediksi Suatu Prodi", data=updated_dhp)

    return tampil_data_prodi
    


# Tampilkan hasil prediksi dan penilaian jika tombol "Prediksi" ditekan
if st.button("Prediksi"):
    hasil_prediksi = prediksi_dan_penilaian(input_prodi, input_predict_year, input_last_year, input_years_to_predict, input_kriteria, input_ambang_batas_jumlah, input_ambang_batas_persen, input_fields)
    st.write(hasil_prediksi)
    st.success("Data berhasil ditambahkan ke worksheet!")
    