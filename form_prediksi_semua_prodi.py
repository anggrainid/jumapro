import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pickle
from datetime import date

# Buat koneksi ke Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Baca data dari Google Sheets
data = conn.read()


# Dropdown options for Lembaga
#lembaga_options = data['Lembaga'].unique()

# CRUD Form
st.title("Halaman Prediksi Semua Prodi")

# Input fields
input_last_year_data = st.text_input("Masukkan Tahun Terakhir Data Jumlah Mahasiswa Baru : ")
input_years_to_predict = st.number_input("Masukkan Proyeksi Prediksi (Dalam Satuan Tahun) : ", min_value=1, max_value=10)
#input_lembaga = st.selectbox("Pilih Lembaga", lembaga_options)

#st.header("Data Jumlah Mahasiswa Baru 2013 - " + (str(last_column_name)) + " dan Prediksi Hingga " + (str(last_column_name+input_years_to_predict)))
# st.subheader("Data Jumlah Mahasiswa Baru 2013 - " + (str(last_column_name)) + " dan Prediksi Hingga " + (str(last_column_name+5)))
# st.caption("Data Jumlah Mahasiswa Baru 2013 - " + (str(last_column_name)) + " dan Prediksi Hingga " + (str(last_column_name+5)))
# st.markdown("Data Jumlah Mahasiswa Baru 2013 - " + (str(last_column_name)) + " dan Prediksi Hingga " + (str(last_column_name+5)))
# st.dataframe(data)

unused_column = ['Kode Prodi', 'Kode Prodi UGM', 'Kode Fakultas', 'Program Studi', 'BAN PT', 'Departemen', 'Kluster', 'PDDIKTI x BAN']
data = data.drop(unused_column, axis=1)

# Taking actions based on user input
if st.button("Prediksi"):
    # Load model dari file .sav
    model = pickle.load(open(r"D:\jumapro\next_year_students_prediction.sav", "rb"))

    
    # Rename kolom terakhir menjadi 'current_students'
    last_column_name = int(input_last_year_data)
    data.rename(columns={last_column_name: 'current_students'}, inplace=True)

    # Cek dan ganti nilai yang tidak valid (bukan angka)
    def convert_to_numeric(val):
        try:
            return float(val)
        except ValueError:
            return 0

    # Terapkan fungsi ke kolom current_students
    data['current_students'] = data['current_students'].apply(convert_to_numeric)

    # Prediksi untuk 5 tahun ke depan
    years_to_predict = input_years_to_predict
    current_year = int(last_column_name)  # Ubah nama kolom terakhir menjadi integer

    # Simpan nilai asli dari 'current_students' di variabel lain
    current_students = data['current_students'].copy()

    # Prediksi untuk beberapa tahun ke depan
    for i in range(1, years_to_predict + 1):
        next_year = current_year + i
        column_name = f'{next_year} (Prediksi)'
        
        # Lakukan prediksi menggunakan nilai di current_students
        data[column_name] = model.predict(current_students.values.reshape(-1, 1))
        data[column_name] = data[column_name].astype(int)
        
        # Gunakan hasil prediksi tahun ini sebagai current_students untuk prediksi tahun berikutnya
        current_students = data[column_name].copy()

    # Tampilkan hasil prediksi
    data.rename(columns={'current_students': f'{current_year} (Saat Ini)'}, inplace=True)
    st.write(f'Hasil Prediksi {years_to_predict} Tahun ke Depan: ')
    # predicted_columns = [f'predicted_{current_year + i}_students' for i in range(1, years_to_predict + 1)]
    st.write(data)


    def create_worksheet_prediction():
        return data

    # Create the Orders dataframe
    prediction_result = create_worksheet_prediction()
    last_year_pred = current_year + input_years_to_predict
    conn.create(worksheet=f"Hasil Prediksi {current_year + 1} - {current_year + input_years_to_predict} Tanggal {date.today()}", data=prediction_result)
    st.success("Worksheet Created 🎉")










