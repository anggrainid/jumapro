import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pickle

# Buat koneksi ke Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Baca data dari Google Sheets
data = conn.read()

last_column_name = data.columns[-1]
st.header("Data Jumlah Mahasiswa Baru 2013 - " + (str(last_column_name)) + " dan Prediksi Hingga " + (str(last_column_name+5)))
st.subheader("Data Jumlah Mahasiswa Baru 2013 - " + (str(last_column_name)) + " dan Prediksi Hingga " + (str(last_column_name+5)))
st.caption("Data Jumlah Mahasiswa Baru 2013 - " + (str(last_column_name)) + " dan Prediksi Hingga " + (str(last_column_name+5)))
st.markdown("Data Jumlah Mahasiswa Baru 2013 - " + (str(last_column_name)) + " dan Prediksi Hingga " + (str(last_column_name+5)))
# st.dataframe(data)

unused_column = ['Kode Prodi', 'Kode Prodi UGM', 'Kode Fakultas', 'Program Studi', 'BAN PT', 'Departemen', 'Kluster', 'PDDIKTI x BAN']
data = data.drop(unused_column, axis=1)

# Load model dari file .sav
model = pickle.load(open(r"D:\jumapro\next_year_students_prediction.sav", "rb"))

# Rename kolom terakhir menjadi 'current_students'
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
years_to_predict = 5
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
st.write("Hasil Prediksi 5 Tahun ke Depan:")
# predicted_columns = [f'predicted_{current_year + i}_students' for i in range(1, years_to_predict + 1)]
st.write(data)