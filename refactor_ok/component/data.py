import streamlit as st
import pickle
from streamlit_gsheets import GSheetsConnection
import pandas as pd

def refresh_data(data):
    conn = st.connection("gsheets", type=GSheetsConnection)
    # existing_dhp = conn.read(worksheet="Data Histori Prediksi Suatu Prodi", ttl=5)
    existing_djm = conn.read(worksheet="Data Jumlah Mahasiswa")
    existing_formula = conn.read(worksheet="Rumus Pemantauan", usecols=list(range(7)), ttl=5)
    existing_dhp = conn.read(worksheet="Data Histori Prediksi Suatu Prodi")
    # Simpan data ke file pickle
    # with open('existing_dhp.pickle', 'wb') as handle:
    #     pickle.dump(existing_dhp, handle, protocol=pickle.HIGHEST_PROTOCOL)

    with open('existing_djm.pickle', 'wb') as handle:
        pickle.dump(existing_djm, handle, protocol=pickle.HIGHEST_PROTOCOL)

    with open('existing_formula.pickle', 'wb') as handle:
        pickle.dump(existing_formula, handle, protocol=pickle.HIGHEST_PROTOCOL)

    with open('existing_dhp.pickle', 'wb') as handle:
        pickle.dump(existing_dhp, handle, protocol=pickle.HIGHEST_PROTOCOL)

    if data == 'djm':
        return existing_djm
    elif data == 'dhp':
        return existing_dhp
    elif data == 'formula':
        return existing_formula
    else:
        return existing_djm, existing_formula, existing_dhp


# Fungsi untuk memuat data dari pickle
def get_data(data):

    with open('existing_dhp.pickle', 'rb') as handle:
        existing_dhp = pickle.load(handle)

    with open('existing_djm.pickle', 'rb') as handle:
        existing_djm = pickle.load(handle)

    with open('existing_formula.pickle', 'rb') as handle:
        existing_formula = pickle.load(handle)

    if data == 'djm':
        return existing_djm
    elif data == 'dhp':
        return existing_dhp
    elif data == 'formula':
        return existing_formula
    else:
        return existing_djm, existing_formula, existing_dhp


def preprocess_data(data):
    # Data Preprocessing
    data = data.dropna(how="all")
    data = data.replace('#N/A ()', 0)
    
    unused_columns = ['Kode Prodi', 'Kode Prodi UGM', 'Kode Fakultas', 'Program Studi', 
                      'BAN PT', 'Departemen', 'Kluster', 'PDDIKTI x BAN']
    
    # Gunakan errors='ignore' untuk menghindari KeyError
    data = data.drop(unused_columns, axis=1, errors='ignore')

    return data
# def year():
#     available_years = [int(col) for col in existing_djm.columns if col.isdigit()]

def preprocess_data(data):
    # Data Preprocessing
    data = data.dropna(how="all")
    data = data.replace('#N/A ()', 0)
    
    unused_columns = ['Kode Prodi', 'Kode Prodi UGM', 'Kode Fakultas', 'Program Studi', 
                      'BAN PT', 'Departemen', 'Kluster', 'PDDIKTI x BAN']
    
    # Gunakan errors='ignore' untuk menghindari KeyError
    data = data.drop(unused_columns, axis=1, errors='ignore')

    return data

# def update_formula(data):
        
#     conn = st.connection("gsheets", type=GSheetsConnection)
#     # existing_dhp = conn.read(worksheet="Data Histori Prediksi Suatu Prodi", ttl=5)
#     update_formula_formula = conn.update(worksheet="Rumus Pemantauan", data=updated_df)

def add_data(existing_data, new_data, worksheet_name):
    conn = st.connection("gsheets", type=GSheetsConnection)
    try:
        # Gabungkan data yang ada dengan data baru
        updated_df = pd.concat([existing_data, new_data], ignore_index=True)

        # Perbarui data di Google Sheets
        conn.update(worksheet=worksheet_name, data=updated_df)

        # Berikan notifikasi keberhasilan
        st.success(f"Data berhasil diperbarui di worksheet '{worksheet_name}'!")
        st.write(updated_df)
        return updated_df

    except Exception as e:
        st.error(f"Gagal memperbarui data: {e}")
        return None