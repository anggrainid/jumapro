import streamlit as st
import pickle
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import numpy as np
from component.data import get_data, refresh_data, preprocess_data, add_data
from component.func import calculate_persentase_penurunan, calculate_ts0_minimal, hitung_persentase_penurunan, hitung_persentase_penurunan_lebih_dari_satu
import matplotlib.pyplot as plt

def prediksi_pemantauan_semua_prodi(existing_djm, existing_formula):
    # st.markdown("Form Prediksi Pemantauan Semua Program Studi")
    # 1. Connections from google sheets


    # conn = st.connection("gsheets", type=GSheetsConnection)
    # existing_dhp = conn.read(worksheet="Data Histori Prediksi Suatu Prodi", ttl=5)
    # existing_djm = conn.read(worksheet="Data Jumlah Mahasiswa")
    # existing_formula = conn.read(worksheet="Rumus Pemantauan", usecols=list(range(7)), ttl=5)

    # with open('existing_dhp.pickle', 'wb') as handle:
    #     pickle.dump(existing_dhp, handle, protocol=pickle.HIGHEST_PROTOCOL)

    # with open('existing_djm.pickle', 'wb') as handle:
    #     pickle.dump(existing_djm, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
    # with open('existing_formula.pickle', 'wb') as handle:
    #     pickle.dump(existing_formula, handle, protocol=pickle.HIGHEST_PROTOCOL)

    # 2. Connections from google sheets

    # with open('existing_djm.pickle', 'rb') as handle:
    #     existing_djm = pickle.load(handle)

    # with open('existing_djm.pickle', 'rb') as handle:
    #     existing_djm = pickle.load(handle)

    # with open('existing_formula.pickle', 'rb') as handle:
    #     existing_formula = pickle.load(handle)
        
        
    st.title("Halaman Prediksi Pemantauan Semua Program Studi")
    st.markdown("Halaman ini digunakan untuk melakukan prediksi pemantauan jumlah mahasiswa baru pada semua program studi yang tersedia")

    
    model = pickle.load(open(r"next_year_students_prediction.sav", "rb"))

    # 3. Data preprocessing

    # Djm = data jumlah mahasiswa
    # Dhp = data history prediksi

    # existing_djm = existing_djm.dropna(how="all")
    # existing_djm = existing_djm.replace('#N/A ()', 0)
    # unused_columns = ['Kode Prodi', 'Kode Prodi UGM', 'Kode Fakultas', 'Program Studi', 
    #                 'BAN PT', 'Departemen', 'Kluster', 'PDDIKTI x BAN']
    # existing_djm = existing_djm.drop(unused_columns, axis=1, errors='ignore')
    # # existing_dhp = existing_dhp.dropna(how="all")
    # existing_formula = existing_formula.dropna(how="all")


    # 1. Connections from google sheets
    # if st.button('Refresh Data'):
    #     existing_djm = refresh_data('djm')
    #     existing_formula = refresh_data('formula')
    #     st.success("Data berhasil dimuat ulang dari Google Sheets!")
    # else:
    # # 2. Connections from pickle
    #     existing_djm = get_data('djm')
    #     existing_formula = get_data('formula')
    # # st.write(existing_djm)
    #     # 3. Data preprocessing
    # existing_djm = preprocess_data(existing_djm)
    # existing_formula = preprocess_data(existing_formula)

    acc_columns = ['Peringkat', 'Awal Masa Berlaku', 'Akhir Masa Berlaku', 'Kadaluarsa']
    existing_djm = existing_djm.drop(acc_columns, axis=1, errors='ignore')
    st.write(existing_djm)

    
    existing_djm.columns = [str(i) for i in existing_djm.columns]

    
    # Dropdown options for Lembaga
    lembaga_options = existing_djm['Lembaga'].unique()
    formula_options = existing_formula['Nama Rumus'].unique()

    # unused_column = ['Kode Prodi', 'Kode Prodi UGM', 'Kode Fakultas', 'Program Studi', 'BAN PT', 'Departemen', 'Kluster', 'PDDIKTI x BAN']
    # existing_djm = existing_djm.drop(unused_column, axis=1, errors='ignore')
    existing_djm
    # st.write(existing_djm.info())

    # 4. CRUD form prediksi pemantauan semua prodi
    # djm_prodi = existing_djm["Prodi"]

    available_years = [col for col in existing_djm.columns if col.isdigit()]
    # max_year = int(existing_djm.columns[-1])
    # min_year = int(existing_djm.columns[12])
    max_year = max(available_years)
    min_year = min(available_years)

    input_predict_year = st.slider("Masukkan Tahun yang Ingin Diprediksi (ex: 2025) : ", min_value=int(min_year)+5, max_value=int(max_year)+1, value=(int(max_year)+1))
    input_last_year = input_predict_year - 1

    input_years_to_predict = st.slider("Masukkan Proyeksi Prediksi (Dalam Satuan Tahun) : ", min_value=1, max_value=10)


    # print(min_year, max_year)

    # 5. Prepare output columns

    # existing_djm[f'Hasil Prediksi Pemantauan ({input_predict_year})'] = [None]*len(existing_djm)

    for i in range(input_years_to_predict):
        existing_djm[str(input_predict_year+i)] = [None]*len(existing_djm)

    existing_djm['Hasil Proyeksi Prediksi Pemantauan'] = [None]*len(existing_djm)

    # 6. Get Data Formula Pemantauan

    selected_formulas_lembaga = {}
    banyak_data_ts_lembaga = {}
        # Pilih Formula untuk setiap lembaga
    for lembaga_name in lembaga_options:
        # Filter formulas by the selected Lembaga
        formula_options = existing_formula[existing_formula['Lembaga'] == lembaga_name]['Nama Rumus'].unique()

        # Dropdown to select formula for the current Lembaga
        selected_formulas_lembaga[lembaga_name] = st.selectbox(f"Pilih Rumus yang Digunakan bagi Prodi di bawah Lembaga {lembaga_name} : ", formula_options)
        print("selected_formula", selected_formulas_lembaga[lembaga_name]) #Rumus Pertama BAN 2024
        selected_formulas_name = existing_formula[(existing_formula['Nama Rumus'] == selected_formulas_lembaga[lembaga_name]) & (existing_formula['Lembaga'] == lembaga_name)].iloc[0]
        st.write(selected_formulas_name)


        # Ambil nilai Banyak Data TS untuk lembaga terkait
        banyak_data_ts_lembaga[lembaga_name] = selected_formulas_name['Banyak Data TS']
        

    # Ambil nilai max dari Banyak Data TS, dan jika NaN maka set ke 0
    max_banyak_data_ts = max([0 if pd.isna(banyak_data_ts_lembaga[lembaga_name]) else banyak_data_ts_lembaga[lembaga_name] for lembaga_name in lembaga_options])

    max_banyak_data_ts = int(max_banyak_data_ts)
    # st.write(max_banyak_data_ts)

    # # 7. Fungsi hitung persentase penurunan
    # def hitung_persentase_penurunan(index, data, predict_year):
    #     # data_mahasiswa_start_year = input_fields["input_jumlah_mahasiswa_ts0"]
    #     # end_year = predict_year
    #     # penurunan_total = (data[f"{end_year} (Prediksi)"] - data_mahasiswa_start_year)
    #     # persentase_penurunan = (penurunan_total / 2) * 100
    #     # return persentase_penurunan
    #     ts_1 = data.at[index, f"{predict_year}"]
    #     ts_0 = data.at[index, str(input_last_year)]
    #     try:
    #         if ts_1==0.0 or np.isnan(ts_1) or (ts_1 is None):
    #             return 0.0
    #     except Exception as e:
    #         print('ERRROR: ts0 ts1', index, type(ts_1), ts_0, ts_1)
    #         raise e
                
    #     penurunan = (ts_0 - ts_1) / ts_1

    #     persentase_penurunan = penurunan * 100

    #     return round(persentase_penurunan, 2)

    # # print('input_fields:', input_fields)
    # # input_fields
    # # Fungsi untuk menghitung persentase penurunan dengan lebih dari satu tahun data
    # def hitung_persentase_penurunan_lebih_dari_satu(index, data, predict_year, banyak_data_ts):
    #     print('function ppls: ', (index, 'existing_djm', predict_year, banyak_data_ts))
    #     global input_fields

    #     total_penurunan = 0
        
    #     # Iterasi dari TS-1 hingga TS-n (n = banyak_data_ts)
    #     for i in range(int(banyak_data_ts) - 1):
    #         if i == 0:
    #             data = data.iloc[index]
    #             ts_0 = data[str(predict_year)]
    #             ts_1 = data[str(input_last_year)]

                
    #         else:
    #             # input_fields = input_fields[]
    #             ts_1 = input_fields[f"input_jumlah_mahasiswa_ts{i}"][index]
    #             ts_0 = input_fields[f"input_jumlah_mahasiswa_ts{i-1}"][index]

    #         print(i, (ts_0), (ts_1))
            
    #         if ts_1==0 or np.isnan(ts_1) or (ts_1 is None):
    #             return 0.0     
                    
    #         penurunan = (ts_0 - ts_1) / ts_1
    #         total_penurunan += penurunan
            
        
    #     # print('data:', type(data))
        
    #     # Hitung rata-rata penurunan
        
    #     rata_rata_penurunan = total_penurunan / (banyak_data_ts - 1)
    #     persentase_penurunan = rata_rata_penurunan * 100

    #     print(f'out {index}:', ' | ', total_penurunan, ' | ', persentase_penurunan)
        
    #     return round(-persentase_penurunan, 2)

    # 8. Prediksi setiap prodi
    model_results = {
        "index": [],
        "X": [],
        "Y": [],
    }

    existing_djm['index'] = existing_djm.index


    for index, row in existing_djm.iterrows():
        lembaga_prodi = row['Lembaga']
        # prodi_name = row['Prodi']        
        # current_students = row[str(input_last_year)]
        # tahun_tidak_lolos = f"Lebih dari {input_years_to_predict} Tahun ke Depan"  # Default value
        
        selected_formula = existing_formula[(existing_formula['Nama Rumus'] == selected_formulas_lembaga[lembaga_prodi]) & (existing_formula['Lembaga'] == lembaga_prodi)].iloc[0]
        input_kriteria = selected_formula["Kriteria"]
        existing_djm.at[index, 'Kriteria'] = input_kriteria
        # input_ambang_batas_jumlah = selected_formula["Ambang Batas (Jumlah)"]
            # looping isi prediksi
        tahun_tidak_lolos_found = False
        existing_djm.at[index, 'Hasil Proyeksi Prediksi Pemantauan'] = f"Lebih dari {input_years_to_predict} Tahun ke Depan"
        
        input_banyak_data_ts = selected_formula["Banyak Data TS"]
        existing_djm.at[index, 'Banyak Data TS'] = input_banyak_data_ts
        
        
        # input_fields = {}
        # input_fields["input_jumlah_mahasiswa_ts0"] = existing_djm[str(input_predict_year)]
        # for i in range(max_banyak_data_ts-1):
        #     field_name = f"input_jumlah_mahasiswa_ts{i}"            
        #     try:
        #         input_fields[field_name] = existing_djm[str(input_predict_year-i-1)]
        #         # print(f'jmlh {i} | {field_name} | {input_predict_year-i} | { existing_djm[input_predict_year-i]}')
        #     except KeyError:
        #         # MUNGKIN datanya ga cukup, misal pilih 2014, tapi datanya cmn ada dari 2013, trus ambil -3 tahun
        #         raise ValueError("Data TS tidak tersedia")
        
        # for col, value in input_fields.items():
        #     existing_djm[col] = value
        # ts = [f"input_jumlah_mahasiswa_ts{i}" for i in range(1, int(max_banyak_data_ts-1))]
        # ts = sorted(ts, reverse=True)
        
        # Ubah input_fields menjadi list (ts_values)
    
        # ts_values.append(existing_djm.at[index, str(input_last_year)])  # TS-0

        # for i in range(1, max_banyak_data_ts):
        #     try:
        #         ts_values.append(existing_djm.at[index, str(input_last_year - i)])  # TS-1, TS-2, dst.
        #     except KeyError:
        #         ts_values.append(None)  # Jika data tidak tersedia
        # Buat ts_values untuk prodi ini berdasarkan tahun-tahun sebelumnya
        
        # for i in range(max_banyak_data_ts-1):
        #     # field_name = f"input_jumlah_mahasiswa_ts{i}"            
        #     try:
        #         input_fields[field_name] = existing_djm[str(input_predict_year-i-1)]
        #         # print(f'jmlh {i} | {field_name} | {input_predict_year-i} | { existing_djm[input_predict_year-i]}')
        #     except KeyError:
        #         # MUNGKIN datanya ga cukup, misal pilih 2014, tapi datanya cmn ada dari 2013, trus ambil -3 tahun
        #         raise ValueError("Data TS tidak tersedia")
        
        ts = []
        ts_values = []
        for i in range(int(input_banyak_data_ts-1)):
            year = input_last_year - i
            ts_value = row.get(str(year), 0)
            ts_values.append(ts_value)
            ts.append(str(year))
            
        for i in range(input_years_to_predict):
            next_year = input_last_year + i
            
            column_name = next_year#f'{next_year} (Prediksi)'

            # Lakukan prediksi menggunakan model untuk current_students dari baris ini
            
            # print('X:', index, next_year, existing_djm.at[index, next_year])
            prediksi_mahasiswa = model.predict([[existing_djm.at[index, str(next_year)]]])[0]
            
            input_ambang_batas_persen = selected_formula["Ambang Batas (%)"]
            ts_values.insert(0, round(prediksi_mahasiswa))
            konversi_jmm = calculate_ts0_minimal(ts_values, input_ambang_batas_persen)
            model_results['index'].append(index)
            model_results['X'].append(existing_djm.at[index, str(next_year)])
            model_results['Y'].append(prediksi_mahasiswa)
            
                
            existing_djm.at[index, str(column_name+1)] = round(prediksi_mahasiswa)
            input_ambang_batas_jumlah = selected_formula["Ambang Batas (Jumlah)"]
            
            # print('Y:', column_name+1, existing_djm.at[index, column_name+1])

            # Perbarui current_students untuk iterasi berikutnya
            # current_students = prediksi_mahasiswa

            # Cek apakah jumlah mahasiswa di bawah ambang batas untuk kriteria Jumlah Mahasiswa
            
            
            if (tahun_tidak_lolos_found==False):
                if (input_kriteria=='Jumlah Mahasiswa') and (prediksi_mahasiswa<input_ambang_batas_jumlah):
                    existing_djm.at[index, 'Hasil Proyeksi Prediksi Pemantauan'] = f"Tidak Lolos pada {next_year+1}"
                    tahun_tidak_lolos_found = True
                elif (input_kriteria=='Persentase Penurunan') and (prediksi_mahasiswa<konversi_jmm):
                    existing_djm.at[index, 'Hasil Proyeksi Prediksi Pemantauan'] = f"Tidak Lolos pada {next_year+1}"
                    tahun_tidak_lolos_found = True

            # print('loop:', prediksi_mahasiswa, input_ambang_batas_jumlah, tahun_tidak_lolos_found, input_kriteria, existing_djm.at[index, 'Hasil Proyeksi Prediksi Pemantauan'])    

                # Cek apakah jumlah mahasiswa di bawah ambang batas untuk kriteria Persentase Penurunan
        # st.write(ts_values)

        # Perbarui ts_values untuk prediksi berikutnya
            # ts_values = [prediksi_mahasiswa] + ts_values[:-1]
        # st.write(next_year)
        # st.write(existing_djm[f'{next_year+1}'])
        # st.write(row[f'{next_year+1}'])
        # ts_values.insert(0, row[f'{next_year+1}'])
        if input_kriteria == "Persentase Penurunan":
            # print(index, 'PERSENTASE PENURUNAN')
            input_ambang_batas_persen = existing_formula[(existing_formula['Nama Rumus'] == selected_formulas_lembaga[existing_djm.at[index, 'Lembaga']]) & (existing_formula['Lembaga'] == existing_djm.at[index, 'Lembaga'])].iloc[0]['Ambang Batas (%)']
            input_ambang_batas_persen = 0 if np.isnan(input_ambang_batas_persen) else input_ambang_batas_persen
            input_ambang_batas_jumlah = None
            selected_formula = existing_formula[(existing_formula['Nama Rumus'] == selected_formulas_lembaga[lembaga_prodi]) & (existing_formula['Lembaga'] == lembaga_prodi)].iloc[0]
            input_banyak_data_ts = selected_formula["Banyak Data TS"]
            # input_fields = {}
            # input_fields["input_jumlah_mahasiswa_ts0"] = existing_djm[str(input_predict_year)]
            # for i in range(int(input_banyak_data_ts)-1):
            #     field_name = f"input_jumlah_mahasiswa_ts{i}"            
            #     try:
            #         input_fields[field_name] = existing_djm[str(input_predict_year-i-1)]
            #         # print(f'jmlh {i} | {field_name} | {input_predict_year-i} | { existing_djm[input_predict_year-i]}')
            #     except KeyError:
            #         # MUNGKIN datanya ga cukup, misal pilih 2014, tapi datanya cmn ada dari 2013, trus ambil -3 tahun
            #         raise ValueError("Data TS tidak tersedia")
                
            # for col, value in input_fields.items():
            #     existing_djm[col] = value
            # ts = [f"input_jumlah_mahasiswa_ts{i}" for i in range(1, int(input_banyak_data_ts-1))]
            # ts = sorted(ts, reverse=True)
            # dari looping function
            input_ambang_batas_persen = existing_formula[(existing_formula['Nama Rumus'] == selected_formulas_lembaga[existing_djm.at[index, 'Lembaga']]) & (existing_formula['Lembaga'] == existing_djm.at[index, 'Lembaga'])].iloc[0]['Ambang Batas (%)']
            input_ambang_batas_persen = 0 if np.isnan(input_ambang_batas_persen) else input_ambang_batas_persen
            round(input_ambang_batas_persen, 2)
            
            
            # if input_banyak_data_ts > 2:
            #     persentase_penurunan = hitung_persentase_penurunan_lebih_dari_satu(index, existing_djm, input_predict_year, input_banyak_data_ts, input_last_year, input_fields)
            # else:
            #     persentase_penurunan = hitung_persentase_penurunan(index, existing_djm, input_predict_year, input_last_year)
                
            persentase_penurunan = calculate_persentase_penurunan(ts_values)
            existing_djm.at[index, 'Hitung Persentase Penurunan'] = f"{persentase_penurunan}%"
            hasil_prediksi_pemantauan = str(("Lolos" if persentase_penurunan <= input_ambang_batas_persen else "Tidak Lolos"))
            existing_djm.at[index, f"Hasil Prediksi Pemantauan ({input_predict_year})"] = hasil_prediksi_pemantauan
                
            #print('persentase penurunan:', persentase_penurunan)
            # hasil_prediksi_pemantauan = "Lolos" if persentase_penurunan.values[0] <= input_ambang_batas_persen else "Tidak Lolos"
            
            #"Lolos" if float(persentase_penurunan.iloc[1]) <= input_ambang_batas_persen else "Tidak Lolos"
            convert_percent_to_ambang_batas_jumlah_mahasiswa = int(row[str(input_last_year)] * (1 - input_ambang_batas_persen / 100))
            # ambang_batas_jumlah_mahasiswa = int(data_prodi["current_students"] * (1 - input_ambang_batas_persen / 100))
            existing_djm.at[index, "Persentase Penurunan Maksimal"] = f"{input_ambang_batas_persen}%"
            # existing_djm.at[index, "Ambang Batas Jumlah Mahasiswa Minimal"] = convert_percent_to_ambang_batas_jumlah_mahasiswa
            
            # existing_djm.at[index, "Persentase Penurunan Maksimal"]
            # print(f'row existing djm at index {index}: ', existing_djm.loc[index])
            



            existing_djm.at[index, "Jumlah Mahasiswa Minimal"] = calculate_ts0_minimal(ts_values, input_ambang_batas_persen)

        elif input_kriteria == "Jumlah Mahasiswa":
            print(index, 'JUMLAH MAHASISWA')
            
            existing_djm.at[index, "Hitung Persentase Penurunan"] = "-"

            existing_djm.at[index, "Persentase Penurunan Maksimal"] = "-"

            hasil_prediksi_pemantauan = str(("Lolos" if existing_djm.at[index, str(input_predict_year)] >= input_ambang_batas_jumlah else "Tidak Lolos"))
            input_ambang_batas_persen = None
            # input_fields = None

            
            existing_djm.at[index, "Jumlah Mahasiswa Minimal"] = int(input_ambang_batas_jumlah)
            existing_djm.at[index, f"Hasil Prediksi Pemantauan ({input_predict_year})"] = hasil_prediksi_pemantauan

    # 9. wrapping op columns
    # st.write(ts_values)
    data_predict_years = [f"{next_year}" for next_year in range(input_predict_year+1, input_predict_year+input_years_to_predict)]
    data_predict_target= [f"{input_predict_year}"]

    ts = sorted(ts)
    ordered_data_prodi = ["Prodi"] + ["Jenjang"] + ["Lembaga"] +  ["Kriteria"] + ["Banyak Data TS"]  + ts  + data_predict_target +  ["Hitung Persentase Penurunan"] +  ["Persentase Penurunan Maksimal"]+ ["Jumlah Mahasiswa Minimal"] +  [f"Hasil Prediksi Pemantauan ({input_predict_year})"] + data_predict_years + ['Hasil Proyeksi Prediksi Pemantauan']
    tampil_data_prodi = existing_djm[ordered_data_prodi]



    rename_ts = {f"input_jumlah_mahasiswa_ts{i+1}": f"{input_last_year-i-1} (TS-{i+1})" for i in range(int(max_banyak_data_ts-1))}
    rename_predict_years = {f"{next_year}": f"{next_year} (Prediksi)" for next_year in range(input_predict_year+1, input_predict_year+input_years_to_predict)}
    tampil_data_prodi.rename(columns=rename_ts, inplace=True)
    tampil_data_prodi.rename(columns=rename_predict_years, inplace=True)
    tampil_data_prodi.rename(columns={f"{input_predict_year}": f"{input_predict_year} (Prediksi)"}, inplace=True)
    # tampil_data_prodi.rename(columns={f"{input_last_year}": f"{input_last_year} (TS)"}, inplace=True)

    st.write("**Hasil Prediksi Pemantauan:**")
    
    prodi_options = tampil_data_prodi['Prodi'].unique()
    selected_prodi = st.selectbox("Pilih Program Studi", options=prodi_options)
    st.write(tampil_data_prodi[tampil_data_prodi['Prodi'] == selected_prodi])
    filtered_data = tampil_data_prodi[tampil_data_prodi['Prodi'] == selected_prodi].iloc[0].copy()
    

    predict_years = [input_predict_year + i for i in range(input_years_to_predict)]
    predict_values_column = [f'{predict_year} (Prediksi)' for predict_year in predict_years ]
    predict_values = [filtered_data[(year)] for year in predict_values_column]
    
    ts_years = ts
    int_ts_years = [int(i) for i in ts_years]
    ts_values = filtered_data[ts_years].astype(int).tolist()

    # st.write(ts_years)
    # st.write(ts_values)

  
    # st.write(predict_years)
    # st.write(predict_values_column)
    # st.write(predict_values)
    # predict_years = [next_year for next_year in range(input_predict_year, input_predict_year+input_years_to_predict)]
    # predict_years_column =[col for col in tampil_data_prodi.columns if col in data_predict_years]
    all_years = int_ts_years + predict_years
    all_values = ts_values + predict_values
        # Scatter Plot
    plt.figure(figsize=(10, 6))
    
    # Plot TS data
    plt.scatter(int_ts_years, ts_values, color='blue', label='Data TS')
    # plt.plot(ts_years, ts_values, color='orange', label='Trend TS')
    
    # Plot predicted data
    plt.scatter(predict_years, predict_values, color='red', label='Data Prediksi')
    # plt.plot(predict_years, predict_values, color='green', linestyle='--', label='Trend Prediksi')
    plt.plot(all_years, all_values)
    # Add title, labels, and grid
    plt.title('Jumlah Mahasiswa Baru Tahun ke Tahun')
    plt.xlabel('Tahun')
    plt.ylabel('Jumlah Mahasiswa Baru')
    # plt.xticks(ticks=range(min(ts_years + predict_years), max(ts_years + predict_years)+1))  # Label X-axis
    plt.legend()
    plt.grid()

    # st.write(all_years)
    # st.write(all_values)
    plt.axhline(y=filtered_data['Jumlah Mahasiswa Minimal'], color='red', linestyle='--', label='Ambang Batas Jumlah Mahasiswa Baru Minimal')
    plt.xticks(ticks=range(int(min(all_years)), int(max(all_years)+1)), labels=range(min(all_years), max(all_years)+1))
    
    # Display the plot in Streamlit
    st.pyplot(plt)
    
    st.write(tampil_data_prodi)
    
   
    
    
    # Ambil data yang dibutuhkan
    # ts_data = filtered_data['Jumlah Mahasiswa TS']
    # kriteria = filtered_data['Kriteria']
    # ambang_batas = filtered_data['Konversi Jumlah Mahasiswa Minimal']
    # banyak_data_ts = filtered_data['Banyak Data TS']
    
    # Grafik Scatter Plot
    # plt.figure(figsize=(10, 6))
    # years = list(range(current_year - int(banyak_data_ts) + 1,current_year + 1))
    # plt.scatter(years,ts_data[::-1], color='blue', label='Jumlah Mahasiswa')
    # plt.plot(years, ts_data[::-1], color='orange', label='Trend')
    # plt.axhline(y=ambang_batas, color='red', linestyle='--', label='Ambang Batas Jumlah Mahasiswa Minimal')
    # plt.title('Jumlah Mahasiswa Tahun ke Tahun')
    # plt.xlabel('Tahun')
    # plt.ylabel('Jumlah Mahasiswa')
    # plt.xticks(years)  # X-axis labels
    # plt.legend()
    # plt.grid()
    # # prodi_banyak_data = prodi_formula["Banyak Data TS"]
    # st.pyplot(plt)
    

    # if st.button("Prediksi Pemantauan Semua Prodi"):
        # st.write(tampil_data_prodi)
    # st.success("Data berhasil ditambahkan ke worksheet!")
    # st.write(ts_values)



# prediksi_pemantauan_semua_prodi()