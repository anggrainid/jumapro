import streamlit as st
import pickle
from streamlit_gsheets import GSheetsConnection

def connection_data(sheet):
    conn = st.connection("gsheets", type=GSheetsConnection)
    data = conn.read(worksheet=sheet, ttl=5)
    with open('data.pickle', 'wb') as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)

    return data



def load_data_from_gsheets(data):
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


existing_djm = load_data_from_gsheets('djm')
st.write(existing_djm)

def preprocess_data_ori(existing_djm, existing_formula):
    # Data Preprocessing
    existing_djm = existing_djm.dropna(how="all")
    existing_djm = existing_djm.replace('#N/A ()', 0)
    existing_formula = existing_formula.dropna(how="all")
    # existing_djm.columns = [str(i) for i in existing_djm.columns]
    
    # Menghapus kolom yang tidak diperlukan
    unused_columns = ['Kode Prodi', 'Kode Prodi UGM', 'Kode Fakultas', 'Program Studi', 
                      'BAN PT', 'Departemen', 'Kluster', 'PDDIKTI x BAN']
    existing_djm = existing_djm.drop(unused_columns, axis=1)
    
    return existing_djm, existing_formula

def preprocess_data(data):
    # Data Preprocessing
    data = data.dropna(how="all")
    data = data.replace('#N/A ()', 0)
    
    unused_columns = ['Kode Prodi', 'Kode Prodi UGM', 'Kode Fakultas', 'Program Studi', 
                      'BAN PT', 'Departemen', 'Kluster', 'PDDIKTI x BAN']
    
    # Gunakan errors='ignore' untuk menghindari KeyError
    data = data.drop(unused_columns, axis=1, errors='ignore')

    return data

existing_djm = preprocess_data(existing_djm)
st.write(existing_djm)