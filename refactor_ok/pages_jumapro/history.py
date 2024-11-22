import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pickle
from sklearn.metrics import r2_score, mean_squared_error
from component.data import get_data, refresh_data, preprocess_data

# def histori_prediksi(existing_djm):

#     year_columns = [col for col in existing_djm.columns if str(col).isdigit()]
#     df_melted = existing_djm.melt(id_vars=['Prodi'], value_vars=year_columns, var_name='Tahun', value_name='Jumlah Mahasiswa')
#     df_melted['Tahun'] = df_melted['Tahun'].astype(int)

#     model = pickle.load(open("next_year_students_prediction.sav", "rb"))

#     # Menambahkan kolom prediksi
#     df_melted['Prediksi Jumlah Mahasiswa'] = df_melted['Jumlah Mahasiswa'].apply(lambda x: round(model.predict([[x]])[0]))

#     # Dropdown pilihan program studi
#     prodi_list = df_melted['Prodi'].unique()
#     prodi = st.selectbox('Pilih Program Studi', prodi_list)

#     # Filter data berdasarkan prodi yang dipilih
#     df_prodi = df_melted[df_melted['Prodi'] == prodi]

#     # Menghitung total mahasiswa sebenarnya dan prediksi
#     total_actual = df_prodi['Jumlah Mahasiswa'].sum()
#     total_predicted = df_prodi['Prediksi Jumlah Mahasiswa'].sum()

#     st.write('Total Mahasiswa Sebenarnya: ', total_actual)
#     st.write('Total Prediksi Mahasiswa: ', total_predicted)

#     # Menghitung nilai R² untuk program studi yang dipilih
#     r2 = r2_score(df_prodi['Jumlah Mahasiswa'], df_prodi['Prediksi Jumlah Mahasiswa'])
#     r2 = round(r2, 2)

#     # Grafik Trend Jumlah Mahasiswa
#     st.write('Grafik Trend Jumlah Mahasiswa Baru')


#     plt.figure(figsize=(10, 6))

#     # Plot Mahasiswa Sebenarnya
#     plt.plot(df_prodi['Tahun'], df_prodi['Jumlah Mahasiswa'], label='Mahasiswa Sebenarnya', marker='o', color='blue')

#     # Plot Prediksi Mahasiswa
#     plt.plot(df_prodi['Tahun'], df_prodi['Prediksi Jumlah Mahasiswa'], label='Prediksi Mahasiswa', marker='o', color='red')

#     # Menghitung garis tren untuk Mahasiswa Sebenarnya
#     z = np.polyfit(df_prodi['Tahun'], df_prodi['Jumlah Mahasiswa'], 1)
#     p = np.poly1d(z)
#     plt.plot(df_prodi['Tahun'], p(df_prodi['Tahun']), "g--", label='Garis Tren')

#     plt.legend()
#     plt.xlabel('Tahun')
#     plt.ylabel('Jumlah Mahasiswa Baru')
#     plt.title(f'Trend Jumlah Mahasiswa Baru di {prodi}')
#     st.pyplot(plt)
#     st.write(f'R² untuk prediksi di {prodi}:', r2)  # Menampilkan R²

#     df_prodi['Tahun'] = df_prodi['Tahun'].astype(str)
#     # Tabel Detail Data
#     st.write('Tabel Detail Data')
#     st.dataframe(df_prodi)

#     def evaluasi_model_per_prodi(existing_djm):

#         year_columns = [col for col in existing_djm.columns if str(col).isdigit()]
#         df_melted = existing_djm.melt(id_vars=['Prodi'], value_vars=year_columns, var_name='Tahun', value_name='Jumlah Mahasiswa')
#         df_melted['Tahun'] = df_melted['Tahun'].astype(int)

#         model = pickle.load(open("next_year_students_prediction.sav", "rb"))

#         # Menyimpan nilai evaluasi untuk setiap program studi
#         evaluasi_list = []

#         # Menghitung RMSE dan R² untuk setiap program studi
#         for prodi in df_melted['Prodi'].unique():
#             df_prodi = df_melted[df_melted['Prodi'] == prodi].copy()
#             df_prodi['Prediksi Jumlah Mahasiswa'] = df_prodi['Jumlah Mahasiswa'].apply(lambda x: round(model.predict([[x]])[0]))

#             # Menghitung nilai R²
#             r2 = r2_score(df_prodi['Jumlah Mahasiswa'], df_prodi['Prediksi Jumlah Mahasiswa'])
            
#             # Menghitung nilai RMSE
#             rmse = np.sqrt(mean_squared_error(df_prodi['Jumlah Mahasiswa'], df_prodi['Prediksi Jumlah Mahasiswa']))
            
#             # Menyimpan hasil evaluasi dalam list
#             evaluasi_list.append({
#                 'Program Studi': prodi,
#                 'RMSE': round(rmse, 3),
#                 'R²': round(r2, 3)
#             })

#         # Mengonversi hasil evaluasi menjadi DataFrame
#         df_evaluasi = pd.DataFrame(evaluasi_list)

#         # Menampilkan tabel evaluasi di Streamlit
#         st.write("Tabel Evaluasi Model Linear Regression per Program Studi")
#         st.dataframe(df_evaluasi)

#     # Contoh penggunaan fungsi di Streamlit
#     # existing_djm = preprocess_data(get_data())
#     evaluasi_model_per_prodi(existing_djm)

def histori_prediksi(existing_djm):

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
