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

data = conn.read(worksheet="Data Jumlah Mahasiswa")

# Dropdown options for Lembaga
lembaga_options = existing_formula['Lembaga'].unique()
formula_options = existing_formula['Nama Rumus'].unique()


# CRUD Form
st.title("Halaman Prediksi Semua Prodi")
max_value = int(data.columns[-1])
min_value = int(data.columns[12])

# Input fields
input_last_year = st.slider("Masukkan Tahun Terakhir Data Jumlah Mahasiswa Baru : ", min_value=min_value, max_value=max_value)
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

            input_fields = {}
            for i in range(int(input_banyak_data_ts) - 1):
                field_name = f"input_jumlah_mahasiswa_ts{i}"
                input_fields[field_name] = st.number_input(f"Masukkan Jumlah Mahasiswa TS-{i}:", value=0)

        else:
            input_ambang_batas_jumlah = selected_formula["Ambang Batas (Jumlah)"]
            input_jumlah_mahasiswa_ts = st.number_input(f"Masukkan Jumlah Mahasiswa TS:", value=0)
            input_ambang_batas_persen = None
            input_fields = None

    

else:
    input_kriteria = st.radio("Kriteria", ["Jumlah Minimal", "Persentase Penurunan"])
    if input_kriteria == "Persentase Penurunan":
        input_ambang_batas_persen = st.slider("Ambang Batas Persentase Maksimal (%)", min_value=1, max_value=100, step=1)
        input_banyak_data_ts = st.slider("Masukkan Banyak Tahun yang Dipakai untuk Persentase Penurunan : ", min_value=2, max_value=5, step=1)
        input_ambang_batas_jumlah = None

        input_fields = {}
        for i in range(input_banyak_data_ts - 1):
            field_name = f"input_jumlah_mahasiswa_ts{i}"
            input_fields[field_name] = st.number_input(f"Masukkan Jumlah Mahasiswa TS-{i}:", value=0)

    else:
        input_ambang_batas_jumlah = st.number_input("Ambang Batas Jumlah Mahasiswa Minimal", min_value=1, step=1)
        input_jumlah_mahasiswa_ts = st.number_input(f"Masukkan Jumlah Mahasiswa TS:", value=0)
        input_ambang_batas_persen = None
        input_fields = None



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
    last_column_name = int(input_last_year)
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










