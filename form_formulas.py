import streamlit as st
from streamlit_gsheets import GSheetsConnection
# import pickle
from datetime import date
import pandas as pd

# Buat koneksi ke Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Baca data dari Google Sheets
data = conn.read()
st.write(data)

# Dropdown options for Lembaga
lembaga_options = data['Lembaga'].unique()

# CRUD Form
st.title("Halaman Manajemen Rumus Pemantauan")

# Input fields
# input_last_year_data = st.text_input("Masukkan Tahun Terakhir Data Jumlah Mahasiswa Baru : ")
# input_years_to_predict = st.number_input("Masukkan Proyeksi Prediksi (Dalam Satuan Tahun) : ", min_value=1, max_value=10)
input_lembaga = st.selectbox("Pilih Lembaga : ", lembaga_options)
input_nama_rumus = st.text_input("Masukkan Nama Rumus (ex: PEMPT) :")
input_kriteria = st.radio("Kriteria", ["Persentase Penurunan", "Jumlah Minimal"])


if input_kriteria == "Persentase Penurunan":
    input_ambang_batas_persen = st.number_input("Ambang Batas Persentase Maksimal (%)", min_value=0.0, max_value=100.0, step=0.1)
    input_ambang_batas_jumlah = None
else:
    input_ambang_batas_jumlah = st.number_input("Ambang Batas Jumlah Mahasiswa Minimal", min_value=1, step=1)
    input_ambang_batas_persen = None

input_tanggal_mulai = st.date_input("Tanggal Mulai Berlaku", value=date.today())
input_keterangan = st.text_area("Keterangan")

#st.header("Data Jumlah Mahasiswa Baru 2013 - " + (str(last_column_name)) + " dan Prediksi Hingga " + (str(last_column_name+input_years_to_predict)))
# st.subheader("Data Jumlah Mahasiswa Baru 2013 - " + (str(last_column_name)) + " dan Prediksi Hingga " + (str(last_column_name+5)))
# st.caption("Data Jumlah Mahasiswa Baru 2013 - " + (str(last_column_name)) + " dan Prediksi Hingga " + (str(last_column_name+5)))
# st.markdown("Data Jumlah Mahasiswa Baru 2013 - " + (str(last_column_name)) + " dan Prediksi Hingga " + (str(last_column_name+5)))
# st.dataframe(data)

# unused_column = ['Kode Prodi', 'Kode Prodi UGM', 'Kode Fakultas', 'Program Studi', 'BAN PT', 'Departemen', 'Kluster', 'PDDIKTI x BAN']
# data = data.drop(unused_column, axis=1)

# Taking actions based on user input
# if st.button("Prediksi"):
#     # Load model dari file .sav
#     model = pickle.load(open(r"D:\jumapro\next_year_students_prediction.sav", "rb"))

    
#     # Rename kolom terakhir menjadi 'current_students'
#     last_column_name = int(input_last_year_data)
#     data.rename(columns={last_column_name: 'current_students'}, inplace=True)

#     # Cek dan ganti nilai yang tidak valid (bukan angka)
#     def convert_to_numeric(val):
#         try:
#             return float(val)
#         except ValueError:
#             return 0

#     # Terapkan fungsi ke kolom current_students
#     data['current_students'] = data['current_students'].apply(convert_to_numeric)

#     # Prediksi untuk 5 tahun ke depan
#     years_to_predict = input_years_to_predict
#     current_year = int(last_column_name)  # Ubah nama kolom terakhir menjadi integer

#     # Simpan nilai asli dari 'current_students' di variabel lain
#     current_students = data['current_students'].copy()

#     # Prediksi untuk beberapa tahun ke depan
#     for i in range(1, years_to_predict + 1):
#         next_year = current_year + i
#         column_name = f'{next_year} (Prediksi)'
        
#         # Lakukan prediksi menggunakan nilai di current_students
#         data[column_name] = model.predict(current_students.values.reshape(-1, 1))
#         data[column_name] = data[column_name].astype(int)
        
#         # Gunakan hasil prediksi tahun ini sebagai current_students untuk prediksi tahun berikutnya
#         current_students = data[column_name].copy()

#     # Tampilkan hasil prediksi
#     data.rename(columns={'current_students': f'{current_year} (Saat Ini)'}, inplace=True)
#     st.write(f'Hasil Prediksi {years_to_predict} Tahun ke Depan: ')
#     # predicted_columns = [f'predicted_{current_year + i}_students' for i in range(1, years_to_predict + 1)]
#     st.write(data)

new_formula = pd.DataFrame(
    {
    "Lembaga": [input_lembaga],
    "Nama Rumus": [input_nama_rumus],
    "Kriteria": [input_kriteria],
    "Ambang Batas (%)": [input_ambang_batas_persen],
    "Ambang Batas (Jumlah)": [input_ambang_batas_jumlah],
    "Tanggal Mulai Berlaku": [input_tanggal_mulai],
    "Keterangan": [input_keterangan]
}

)

def create_formulas_df():
    return new_formula

df_new_formula = create_formulas_df()


#     # Create the Orders dataframe
#     prediction_result = create_worksheet_prediction()
#     last_year_pred = current_year + input_years_to_predict
#     conn.create(worksheet=f"Hasil Prediksi {current_year + 1} - {current_year + input_years_to_predict} Tanggal {date.today()}", data=prediction_result)
#     st.success("Worksheet Created 🎉")

if st.button("Tambah Rumus"):
    conn.create(worksheet="Rumus Pemantauan", data=df_new_formula)
    st.write(df_new_formula)
    st.success("Worksheet Created 🎉")

# Add, Update, Delete buttons
# if st.button("Tambah Rumus"):
#     new_formula = {
#         "Lembaga": input_lembaga,
#         "Nama Rumus": input_nama_rumus,
#         "Kriteria": input_kriteria,
#         "Ambang Batas (%)": input_ambang_batas_persen,
#         "Ambang Batas (Jumlah)": input_ambang_batas_jumlah,
#         "Tanggal Mulai Berlaku": input_tanggal_mulai,
#         "Keterangan": input_keterangan
#     }
#     # Append the new formula to the Google Sheet or local dataframe
#     sheet.append_row(list(new_formula.values()))
#     st.success("Rumus berhasil ditambahkan!")

# # Display existing formulas
# st.subheader("Daftar Rumus Pemantauan")
# existing_formulas = pd.DataFrame(sheet.get_all_records())
# st.dataframe(existing_formulas)

# # Option to edit or delete existing formulas
# st.subheader("Edit atau Hapus Rumus")
# selected_formula = st.selectbox("Pilih Rumus untuk Edit atau Hapus", existing_formulas["Nama Rumus"].unique())

# if st.button("Hapus Rumus"):
#     row_to_delete = existing_formulas[existing_formulas["Nama Rumus"] == selected_formula].index[0] + 2  # +2 karena Google Sheets index starts at 1 and the first row is the header
#     sheet.delete_row(row_to_delete)
#     st.success("Rumus berhasil dihapus!")

# if st.button("Edit Rumus"):
#     st.warning("Fitur edit ini belum diimplementasikan secara penuh. Silakan tambahkan fitur edit di bagian ini.")








