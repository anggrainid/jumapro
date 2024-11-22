import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pickle
from sklearn.metrics import r2_score, mean_squared_error
from streamlit_gsheets import GSheetsConnection

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



# def load_data(data):
#     if st.button('Refresh Data', key=f'refresh_{data}'):
#         if data == 'djm':
#             existing_data = refresh_data('djm')
#             st.success("Data berhasil dimuat ulang dari Google Sheets!")
#         elif data == 'dhp':
#             existing_data = refresh_data('dhp')
#             st.success("Data berhasil dimuat ulang dari Google Sheets!")
#         elif data == 'formula':
#             existing_data = refresh_data('formula')
#             st.success("Data berhasil dimuat ulang dari Google Sheets!")
    
#     else:
#         existing_data = get_data(data)
    
#     # Preprocess data
#     existing_data = preprocess_data(existing_data)
#     return existing_data

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
    
def histori_prediksi_new(existing_djm):

    year_columns = [col for col in existing_djm.columns if str(col).isdigit()]
    df_melted = existing_djm.melt(id_vars=['Prodi'], value_vars=year_columns, var_name='Tahun', value_name='Jumlah Mahasiswa')
    df_melted['Tahun'] = df_melted['Tahun'].astype(int)
    # df_melted['Jumlah Mahasiswa Setelahnya'] = df_melted.groupby('Prodi')['Jumlah Mahasiswa Saat Ini'].shift(-1)
    # Sortir berdasarkan Prodi dan Tahun
    # df_melted = df_melted.sort_values(['Prodi', 'Tahun'])
    df_melted['Jumlah Mahasiswa Tahun Sebelumnya'] = df_melted.groupby('Prodi')['Jumlah Mahasiswa'].shift(1)
    df_melted = df_melted.dropna()
    model = pickle.load(open("next_year_students_prediction.sav", "rb"))

    # Menambahkan kolom prediksi
    # df_melted['Prediksi Jumlah Mahasiswa Setelahnya'] = df_melted['Jumlah Mahasiswa Saat Ini'].apply(lambda x: round(model.predict([[x]])[0]))
    
    df_melted['Prediksi Jumlah Mahasiswa'] = df_melted['Jumlah Mahasiswa Tahun Sebelumnya'].apply(lambda x: round(model.predict([[x]])[0]  if pd.notnull(x) else np.nan))
    
    # Dropdown pilihan program studi
    prodi_list = df_melted['Prodi'].unique()
    prodi = st.selectbox('Pilih Program Studi', prodi_list)

    # Filter data berdasarkan prodi yang dipilih
    df_prodi = df_melted[df_melted['Prodi'] == prodi]

    
    # Menghitung total mahasiswa sebenarnya dan prediksi
    total_actual = df_prodi['Jumlah Mahasiswa'].sum()
    total_predicted = df_prodi['Prediksi Jumlah Mahasiswa'].sum()

    st.write('Total Mahasiswa Sebenarnya: ', round(total_actual))
    st.write('Total Prediksi Mahasiswa: ', total_predicted)

    df_prodi = df_prodi.dropna()    
    # Menghitung nilai R² untuk program studi yang dipilih
    r2 = r2_score(df_prodi['Jumlah Mahasiswa'], df_prodi['Prediksi Jumlah Mahasiswa'])
    r2 = round(r2, 2)
    # st.write(df_prodi)
    # st.write(f'R² untuk prediksi di {prodi}:', r2)

    # Grafik Trend Jumlah Mahasiswa
    st.write('Grafik Trend Jumlah Mahasiswa Baru')


    plt.figure(figsize=(10, 6))

    # Plot Mahasiswa Sebenarnya
    plt.plot(df_prodi['Tahun'], df_prodi['Jumlah Mahasiswa'], label='Mahasiswa Sebenarnya', marker='o', color='blue')

    # Plot Prediksi Mahasiswa
    plt.plot(df_prodi['Tahun'], df_prodi['Prediksi Jumlah Mahasiswa'], label='Prediksi Mahasiswa', marker='o', color='red')

    # Menghitung garis tren untuk Mahasiswa Sebenarnya
    z = np.polyfit(df_prodi['Tahun'], df_prodi['Jumlah Mahasiswa'], 1)
    p = np.poly1d(z)
    plt.plot(df_prodi['Tahun'], p(df_prodi['Tahun']), "g--", label='Garis Tren')

    plt.legend()
    plt.xlabel('Tahun')
    plt.ylabel('Jumlah Mahasiswa Baru')
    plt.title(f'Trend Jumlah Mahasiswa Baru di {prodi}')
    st.pyplot(plt)
    #   Menampilkan R²
    st.write(f'R² untuk prediksi di {prodi}:', r2)  # Menampilkan R²

    df_prodi['Tahun'] = df_prodi['Tahun'].astype(str)
    df_prodi = df_prodi.drop(columns=['Jumlah Mahasiswa Tahun Sebelumnya'])
    # Tabel Detail Data
    st.write('Tabel Detail Data')
    st.dataframe(df_prodi)





histori_prediksi_new(existing_djm=preprocess_data(get_data('djm')))