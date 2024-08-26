import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pickle
from datetime import date
import pandas as pd

# Buat koneksi ke Google Sheets
# conn = st.connection("gsheets", type=GSheetsConnection)

# Baca data dari Google Sheets
# data = conn.read()

# Dropdown options for Lembaga
#lembaga_options = data['Lembaga'].unique()

# CRUD Form
st.title("Halaman Prediksi Suatu Prodi")

# Input fields
input_prodi = st.text_input("Masukkan Nama Program Studi : ")

input_last_year_data = st.text_input("Masukkan Tahun Terakhir Data Jumlah Mahasiswa Baru :  ") #semua

input_years_to_predict = st.number_input("Masukkan Proyeksi Prediksi (Dalam Satuan Tahun) : ", min_value=1, max_value=10) #semua
input_kriteria = st.radio("Kriteria", ["Jumlah Minimal", "Persentase Penurunan"])

if input_kriteria == "Persentase Penurunan":
    input_ambang_batas_persen = st.number_input("Ambang Batas Persentase Maksimal (%)", min_value=1, max_value=100, step=1)
    input_ambang_batas_jumlah = None
    input_banyak_data_ts = st.number_input("Masukkan Banyak Tahun yang Dipakai untuk Persentase Penurunan : ",  min_value=1, max_value=5, step=1)
    if input_banyak_data_ts > 0:
        input_fields = {}
        for i in range(input_banyak_data_ts):
            if i == 0:
                field_name = f"input_jumlah_mahasiswa_ts"
                input_fields[field_name] = st.number_input(f"Masukkan Jumlah Mahasiswa TS:", value=0)
            else:
                field_name = f"input_jumlah_mahasiswa_ts{i-1}"
                input_fields[field_name] = st.number_input(f"Masukkan Jumlah Mahasiswa TS-{i}:", value=0)

else:
    input_ambang_batas_jumlah = st.number_input("Ambang Batas Jumlah Mahasiswa Minimal", min_value=1, step=1)
    input_ambang_batas_persen = None
    input_jumlah_mahasiswa_ts = st.number_input(f"Masukkan Jumlah Mahasiswa TS:", value=0)


#input_lembaga = st.selectbox("Pilih Lembaga", lembaga_options)

#st.header("Data Jumlah Mahasiswa Baru 2013 - " + (str(last_column_name)) + " dan Prediksi Hingga " + (str(last_column_name+input_years_to_predict)))
# st.subheader("Data Jumlah Mahasiswa Baru 2013 - " + (str(last_column_name)) + " dan Prediksi Hingga " + (str(last_column_name+5)))
# st.caption("Data Jumlah Mahasiswa Baru 2013 - " + (str(last_column_name)) + " dan Prediksi Hingga " + (str(last_column_name+5)))
# st.markdown("Data Jumlah Mahasiswa Baru 2013 - " + (str(last_column_name)) + " dan Prediksi Hingga " + (str(last_column_name+5)))
# st.dataframe(data)

# Taking actions based on user input
if st.button("Prediksi"):
    # Load model dari file .sav
    model = pickle.load(open(r"D:\jumapro\next_year_students_prediction.sav", "rb"))

    
    # Rename kolom terakhir menjadi 'current_students'
    last_year_data= int(input_last_year_data)
    #data.rename(columns={last_column_name: 'current_students'}, inplace=True)
    input_last_year_data_student = input_fields[field_name]
    new_data_prodi = {
    'Prodi': [input_prodi],
    'current_students': [input_last_year_data_student]
    }
    data_prodi = pd.DataFrame(new_data_prodi)


    # # Cek dan ganti nilai yang tidak valid (bukan angka)
    # def convert_to_numeric(val):
    #     try:
    #         return float(val)
    #     except ValueError:
    #         return 0

    # # Terapkan fungsi ke kolom current_students
    # data['current_students'] = data['current_students'].apply(convert_to_numeric)

    # Prediksi untuk 5 tahun ke depan
    # print(data_prodi)
    years_to_predict = input_years_to_predict
    current_year = int(input_last_year_data)  # Ubah nama kolom terakhir menjadi integer

# Simpan nilai asli dari 'current_students' di variabel lain
# current_students = data_prodi['current_students'].copy()

    # Prediksi untuk beberapa tahun ke depan
    for i in range(1, years_to_predict + 1):
        next_year = current_year + i
        column_name = f'{next_year} (Prediksi)'
        
        # Lakukan prediksi menggunakan nilai di current_students
        data_prodi[column_name] = model.predict(current_students.values.reshape(-1, 1))
        data_prodi[column_name] = data_prodi[column_name].astype(int)
        
        # Gunakan hasil prediksi tahun ini sebagai current_students untuk prediksi tahun berikutnya
        current_students = data_prodi[column_name].copy()


# Tampilkan hasil prediksi
# data_prodi.rename(columns={'current_students': f'{current_year} (Saat Ini)'}, inplace=True)
# st.write(f'Hasil Prediksi {years_to_predict} Tahun ke Depan: ')
# predicted_columns = [f'predicted_{current_year + i}_students' for i in range(1, years_to_predict + 1)]
# st.write(data_prodi)


    # def create_worksheet_prediction():
    #     return data

    # Create the Orders dataframe
    # prediction_result = create_worksheet_prediction()
    # last_year_pred = current_year + input_years_to_predict
    # conn.create(worksheet=f"Hasil Prediksi {current_year + 1} - {current_year + input_years_to_predict} Tanggal {date.today()}", data=prediction_result)
    # st.success("Worksheet Created 🎉")

# Fungsi untuk menghitung persentase penurunan
def hitung_persentase_penurunan(row):
    years = ['2018', '2019', '2020', '2021', '2022', '2023']
    values = [row[year] for year in years]
    
    # Menghitung penurunan tahunan dan persentase
    penurunan_total = (values[0] - values[-1]) / values[0]
    persentase_penurunan = penurunan_total * 100
    
    return persentase_penurunan

# # Menghitung persentase penurunan untuk setiap program studi
# data_prodi['persentase_penurunan'] = data_prodi.apply(hitung_persentase_penurunan, axis=1)

# # Menampilkan data
# st.write("Data dengan persentase penurunan:")
# st.write(data_prodi)

# Menyaring data berdasarkan aturan
# fakultas_batas_minimal = {
#     'FKKMK': 5,
#     'Fakultas Lain': 3
# }

# def cek_lolos(row, fakultas):
#     batas_minimal = fakultas_batas_minimal.get(fakultas, 3)
#     if row['current_students'] <= batas_minimal or row['persentase_penurunan'] > 20:
#         return "Tidak Lolos"
#     return "Lolos"

# # Misalnya kita tambahkan kolom 'Fakultas' untuk setiap prodi
# # data['Fakultas'] = ['FKKMK', 'Fakultas Lain']
# data['Lolos'] = data.apply(lambda row: cek_lolos(row, row['Fakultas']), axis=1)

# st.write("Hasil Pemantauan:")
# st.write(data[['Prodi', 'current_students', 'persentase_penurunan', 'Lolos']])

