import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pickle
from datetime import date

# Buat koneksi ke Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Fetch existing formulas data
existing_formula = conn.read(worksheet="Rumus Pemantauan", usecols=list(range(7)), ttl=5)
existing_formula = existing_formula.dropna(how="all")
#st.write(existing_formula)

data_semua_prodi = conn.read(worksheet="Data Jumlah Mahasiswa")

# Dropdown options for Lembaga
lembaga_options = existing_formula['Lembaga'].unique()
formula_options = existing_formula['Nama Rumus'].unique()


# CRUD Form
st.title("Halaman Prediksi Semua Prodi")
max_value = int(data_semua_prodi.columns[-1])
min_value = int(data_semua_prodi.columns[12])

# Input fields
input_last_year = st.slider("Masukkan Tahun Terakhir Data Jumlah Mahasiswa Baru : ", min_value=min_value, max_value=max_value)
input_predict_year = input_last_year + 1
# Error Handling kalau data[input_last_year-1] ngga ada maka tampilkan "Anda belum memiliki data jumlah mahasiswa tahun ... sehingga tidak bisa memprediksi ...."

input_years_to_predict = st.slider("Masukkan Proyeksi Prediksi (Dalam Satuan Tahun) : ", min_value=1, max_value=10)
#input_lembaga = st.selectbox("Pilih Lembaga", lembaga_options)

input_formula = st.radio("Formula yang Digunakan", ["Sudah Ada", "Baru"])

selected_formulas = {}
if input_formula == "Sudah Ada":

    
    for lembaga_name in lembaga_options:
        # Filter formulas by the selected Lembaga
        formula_options = existing_formula[existing_formula['Lembaga'] == lembaga_name]['Nama Rumus'].unique()

        # Dropdown to select formula for the current Lembaga
        selected_formulas[lembaga_name] = st.selectbox(f"Pilih Rumus yang Digunakan bagi Prodi di bawah Lembaga {lembaga_name} : ", formula_options)

        # Mengambil baris formula yang dipilih
        selected_formula = existing_formula[(existing_formula['Nama Rumus'] == selected_formulas[lembaga_name]) & (existing_formula['Lembaga'] == lembaga_name)].iloc[0]

        # Cek kriteria
        input_kriteria = selected_formula["Kriteria"]

        if input_kriteria == "Persentase Penurunan":
            input_ambang_batas_persen = selected_formula["Ambang Batas (%)"]
            input_banyak_data_ts = selected_formula["Banyak Data TS"]
            input_ambang_batas_jumlah = None

            # input_fields = {}
            # for i in range(int(input_banyak_data_ts) - 1):
            #     field_name = f"input_jumlah_mahasiswa_ts{i}"
            #     input_fields[field_name] = st.number_input(f"Masukkan Jumlah Mahasiswa TS-{i}:", value=0)

        else:
            input_ambang_batas_jumlah = selected_formula["Ambang Batas (Jumlah)"]
            # input_jumlah_mahasiswa_ts = None
            input_ambang_batas_persen = None
            input_fields = None

    

else:
    input_kriteria = st.radio("Kriteria", ["Jumlah Minimal", "Persentase Penurunan"])
    if input_kriteria == "Persentase Penurunan":
        input_ambang_batas_persen = st.slider("Ambang Batas Persentase Maksimal (%)", min_value=1, max_value=100, step=1)
        input_banyak_data_ts = st.slider("Masukkan Banyak Tahun yang Dipakai untuk Persentase Penurunan : ", min_value=2, max_value=5, step=1)
        input_ambang_batas_jumlah = None

        # input_fields = {}
        # for i in range(input_banyak_data_ts - 1):
        #     field_name = f"input_jumlah_mahasiswa_ts{i}"
        #     input_fields[field_name] = st.number_input(f"Masukkan Jumlah Mahasiswa TS-{i}:", value=0)

    else:
        input_ambang_batas_jumlah = st.number_input("Ambang Batas Jumlah Mahasiswa Minimal", min_value=1, step=1)
        # input_jumlah_mahasiswa_ts = st.number_input(f"Masukkan Jumlah Mahasiswa TS:", value=0)
        input_ambang_batas_persen = None
        input_fields = None



#st.header("Data Jumlah Mahasiswa Baru 2013 - " + (str(last_column_name)) + " dan Prediksi Hingga " + (str(last_column_name+input_years_to_predict)))
# st.subheader("Data Jumlah Mahasiswa Baru 2013 - " + (str(last_column_name)) + " dan Prediksi Hingga " + (str(last_column_name+5)))
# st.caption("Data Jumlah Mahasiswa Baru 2013 - " + (str(last_column_name)) + " dan Prediksi Hingga " + (str(last_column_name+5)))
# st.markdown("Data Jumlah Mahasiswa Baru 2013 - " + (str(last_column_name)) + " dan Prediksi Hingga " + (str(last_column_name+5)))
# st.dataframe(data)

unused_column = ['Kode Prodi', 'Kode Prodi UGM', 'Kode Fakultas', 'Program Studi', 'BAN PT', 'Departemen', 'Kluster', 'PDDIKTI x BAN']
data_semua_prodi = data_semua_prodi.drop(unused_column, axis=1)


# Prediksi beberapa tahun ke depan dan cek kapan prodi tidak lolos pemantauan
    # years_to_predict = input_years_to_predict
    # current_year = int(last_column_name)  # Ubah nama kolom terakhir menjadi integer

# Rename kolom terakhir menjadi 'current_students'
last_column_name = int(input_last_year)
data_semua_prodi.rename(columns={last_column_name: 'current_students'}, inplace=True)

# Cek dan ganti nilai yang tidak valid (bukan angka)
def convert_to_numeric(val):
    try:
        return float(val)
    except ValueError:
        return 0

# Terapkan fungsi ke kolom current_students
data_semua_prodi['current_students'] = data_semua_prodi['current_students'].apply(convert_to_numeric)

# Prediksi untuk beberapa tahun ke depan
model = pickle.load(open(r"D:\jumapro\next_year_students_prediction.sav", "rb"))

# Simpan nilai asli dari 'current_students' di variabel lain
current_students = data_semua_prodi['current_students'].copy()
tahun_tidak_lolos = f"Lebih dari {input_years_to_predict} Tahun ke Depan"

for i in range(1, input_years_to_predict + 1):
    next_year = input_last_year + i
    column_name = f'{next_year} (Prediksi)'
    
    # Lakukan prediksi menggunakan nilai di current_students
    data_semua_prodi[column_name] = model.predict(current_students.values.reshape(-1, 1))
    data_semua_prodi[column_name] = data_semua_prodi[column_name].astype(int)

    # Cek apakah prodi tidak lolos pemantauan
    if input_kriteria == "Jumlah Minimal":
        if data_semua_prodi[column_name].values[0] < input_ambang_batas_jumlah:
            tahun_tidak_lolos = next_year
            
    elif input_kriteria == "Persentase Penurunan":
        ambang_batas_jumlah_mahasiswa = int(data_semua_prodi["current_students"].values[0] * (1 - input_ambang_batas_persen / 100))
        if data_semua_prodi[column_name].values[0] < ambang_batas_jumlah_mahasiswa:
            tahun_tidak_lolos = next_year
            
    
    current_students = data_semua_prodi[column_name].copy()

# Tambahkan kolom "Tahun Tidak Lolos (Prediksi)"
data_semua_prodi["Tahun Tidak Lolos (Prediksi)"] = str(tahun_tidak_lolos)

data_semua_prodi

ts_1 = data_semua_prodi[f"{input_predict_year - i-1}"]
ts_1
# Fungsi untuk menghitung persentase penurunan
def hitung_persentase_penurunan(data, predict_year):
    ts_1 = data[f"{predict_year} (Prediksi)"]
    ts_0 = data["current_students"]
    penurunan = (ts_0 - ts_1) / ts_1
    persentase_penurunan = penurunan * 100
    return persentase_penurunan

# Fungsi untuk menghitung persentase penurunan dengan lebih dari satu tahun data
def hitung_persentase_penurunan_lebih_dari_satu(data, predict_year, banyak_data_ts):
    total_penurunan = 0

    # Iterasi dari TS-1 hingga TS-n (n = banyak_data_ts)
    for i in range(int(banyak_data_ts - 1)):
        if i == 0:
            ts_1 = data[f"{predict_year} (Prediksi)"]
            ts_0 = data["current_students"]
        else:
            ts_1 = data[f"{predict_year - i-1}"]
            ts_0 = data[f"{predict_year - i-2}"]

        penurunan = (ts_0 - ts_1) / ts_1
        total_penurunan += penurunan

    rata_rata_penurunan = total_penurunan / (banyak_data_ts - 1)
    persentase_penurunan = rata_rata_penurunan * 100
    return persentase_penurunan


# Fungsi untuk prediksi dan penilaian
def prediksi_dan_penilaian(data_prodi, input_predict_year, input_last_year, input_years_to_predict, input_kriteria, input_ambang_batas_jumlah, input_ambang_batas_persen):
    if input_kriteria == "Jumlah Minimal":
        hasil_prediksi_pemantauan = "Lolos" if data_prodi[f"{input_predict_year} (Prediksi)"].values[0] > input_ambang_batas_jumlah else "Tidak Lolos"
        data_prodi["Jumlah Mahasiswa Minimal"] = input_ambang_batas_jumlah
        data_prodi[f"Hasil Prediksi Pemantauan ({input_predict_year})"] = hasil_prediksi_pemantauan
        data_prodi.rename(columns={'current_students': f'{input_last_year} (Saat Ini)'}, inplace=True)
    elif input_kriteria == "Persentase Penurunan":
        if input_banyak_data_ts > 2:
            persentase_penurunan = hitung_persentase_penurunan_lebih_dari_satu(data_semua_prodi, input_predict_year, input_banyak_data_ts)
        else:
            persentase_penurunan = hitung_persentase_penurunan(data_prodi, input_predict_year)
        
        ambang_batas_jumlah_mahasiswa = int(data_prodi["current_students"].values[0] * (1 - input_ambang_batas_persen / 100))
        hasil_prediksi_pemantauan = "Lolos" if persentase_penurunan.values[0] < input_ambang_batas_persen else "Tidak Lolos"

        data_prodi["Hitung Persentase Penurunan"] = f"{round(persentase_penurunan.values[0])}%"
        data_prodi["Ambang Batas Persen"] = f"{input_ambang_batas_persen}%"
        data_prodi["Ambang Batas Jumlah Mahasiswa"] = ambang_batas_jumlah_mahasiswa
        data_prodi["Hasil Prediksi Pemantauan"] = hasil_prediksi_pemantauan
        data_prodi.rename(columns={'current_students': f'{input_last_year} (Saat Ini)'}, inplace=True)
    return data_prodi

# Tampilkan hasil prediksi dan penilaian jika tombol "Prediksi" ditekan
if st.button("Prediksi"):
    hasil_prediksi = prediksi_dan_penilaian(data_semua_prodi, input_predict_year, input_last_year, input_years_to_predict, input_kriteria, input_ambang_batas_jumlah, input_ambang_batas_persen)
    st.write(hasil_prediksi)


# Taking actions based on user input
# if st.button("Prediksi"):
#     # Load model dari file .sav
#     model = pickle.load(open(r"D:\jumapro\next_year_students_prediction.sav", "rb"))

    
#     # Rename kolom terakhir menjadi 'current_students'
#     last_column_name = int(input_last_year)
#     data.rename(columns={last_column_name: 'current_students'}, inplace=True)



#     # Tampilkan hasil prediksi
#     data.rename(columns={'current_students': f'{current_year} (Saat Ini)'}, inplace=True)
#     st.write(f'Hasil Prediksi {years_to_predict} Tahun ke Depan: ')
#     # predicted_columns = [f'predicted_{current_year + i}_students' for i in range(1, years_to_predict + 1)]
#     st.write(data)


#     def create_worksheet_prediction():
#         return data

#     # Create the Orders dataframe
#     prediction_result = create_worksheet_prediction()
#     last_year_pred = current_year + input_years_to_predict
#     conn.create(worksheet=f"Hasil Prediksi {current_year + 1} - {current_year + input_years_to_predict} Tanggal {date.today()}", data=prediction_result)
#     st.success("Worksheet Created 🎉")










