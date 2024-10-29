import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pickle
import pandas as pd
from datetime import date
from component.data import get_data, refresh_data, preprocess_data
from component.func import calculate_persentase_penurunan, calculate_ts0_minimal
import matplotlib.pyplot as plt

def prediksi_pemantauan_satu_prodi(existing_formula):


    # Halaman Prediksi Suatu Prodi
    # st.title("Halaman Prediksi Suatu Prodi Dengan Formula")
    st.markdown("Form Prediksi Pemantauan Suatu Program Studi")



    # Establishing a Google Sheets connection
    # conn = st.connection("gsheets", type=GSheetsConnection)

    # # Fetch data dhp = data history prediction
    # existing_dhp = conn.read(worksheet="Data Histori Prediksi Suatu Prodi", ttl=5)
    # existing_dhp = existing_dhp.dropna(how="all")

    # # Fetch data djm = data jumlah mahasiswa
    # existing_djm = conn.read(worksheet="Data Jumlah Mahasiswa")

    # with open('D:\\jumapro\\existing_djm.pickle', 'wb') as handle:
    #     pickle.dump(existing_djm, handle, protocol=pickle.HIGHEST_PROTOCOL)

    # with open('D:\\jumapro\\existing_djm.pickle', 'rb') as handle:
    #     existing_djm = pickle.load(handle)
  

    # existing_djm = existing_djm.dropna(how="all")

    # # Fetch existing formulas data
    # existing_formula = conn.read(worksheet="Rumus Pemantauan", usecols=list(range(7)), ttl=5)
    # existing_formula = existing_formula.dropna(how="all")

    # if st.button('Refresh Data'):
    #     existing_dhp = refresh_data('dhp')
    #     existing_formula = refresh_data('formula')
    #     st.success("Data berhasil dimuat ulang dari Google Sheets!")
    # else:
    # # 2. Connections from pickle
    #     existing_dhp = get_data('dhp')
    #     existing_formula = get_data('formula')
    # # st.write(existing_djm)
    #     # 3. Data preprocessing
    # existing_dhp = preprocess_data(existing_dhp)
    # existing_formula = preprocess_data(existing_formula)


    # Input fields
    input_prodi = st.text_input("Masukkan Nama Program Studi : ")

    input_predict_year = st.number_input("Masukkan Tahun yang Ingin Diprediksi (ex: 2025) : ", min_value=2024)
    input_last_year = input_predict_year - 1

    input_years_to_predict = st.number_input("Masukkan Proyeksi Prediksi (Dalam Satuan Tahun) : ", min_value=1, max_value=10)

    input_formula = st.radio("Formula yang Digunakan", ["Sudah Ada", "Baru"])

    if input_formula == "Sudah Ada":
        # Dropdown options for Lembaga
        formula_options = existing_formula['Nama Rumus'].unique()
        input_existing_formula = st.selectbox("Pilih Rumus yang Digunakan : ", formula_options)
        # Mengambil baris formula yang dipilih
        selected_formula = existing_formula[existing_formula['Nama Rumus'] == input_existing_formula].iloc[0]
        st.write(selected_formula)
        # Cek kriteria
        input_kriteria = selected_formula["Kriteria"]
        input_banyak_data_ts = selected_formula["Banyak Data TS"]
        if input_kriteria == "Persentase Penurunan":
            input_ambang_batas_persen = selected_formula["Ambang Batas (%)"]
            input_ambang_batas_jumlah = None

            # input_fields = {}
            # for i in range(int(input_banyak_data_ts-1)):
            #     field_name = f"input_jumlah_mahasiswa_ts{i}"
            #     input_fields[field_name] = st.number_input(f"Masukkan Jumlah Mahasiswa TS-{i}:", value=0)
            ts_values = []
            for i in range(int(input_banyak_data_ts-1)):
                year = input_last_year - i
                value = st.number_input(f"Masukkan Jumlah Mahasiswa Tahun {year} (TS-{i}):", step=0)
                ts_values.append(value)
                # if i == 0:
                #     # Placeholder untuk hasil prediksi
                #     ts_values.append(0)  # Will be replaced with prediction
                # else:
                #     value = st.number_input(f"Masukkan Jumlah Mahasiswa TS-{i}:", value=0)
                #     ts_values.append(value)

        else:
            input_ambang_batas_jumlah = selected_formula["Ambang Batas (Jumlah)"]
            input_jumlah_mahasiswa_ts = st.number_input(f"Masukkan Jumlah Mahasiswa Tahun {input_last_year} (TS-0) :", value=0)
            input_ambang_batas_persen = None
            input_fields = None
            ts_values = [input_jumlah_mahasiswa_ts]

    else:
        input_kriteria = st.radio("Kriteria", ["Jumlah Mahasiswa", "Persentase Penurunan"])
        ts_values = []
        
        if input_kriteria == "Persentase Penurunan":
            input_ambang_batas_persen = st.slider("Ambang Batas Persentase Maksimal (%)", min_value=1, max_value=100, step=1)
            input_banyak_data_ts = st.slider("Masukkan Banyak Tahun yang Dipakai untuk Persentase Penurunan : ", min_value=2, max_value=5, step=1)
            input_ambang_batas_jumlah = None

            # input_fields = {}
            # for i in range(input_banyak_data_ts - 1):
            #     field_name = f"input_jumlah_mahasiswa_ts{i}"
            #     input_fields[field_name] = st.number_input(f"Masukkan Jumlah Mahasiswa TS-{i}:", value=0)
            for i in range(input_banyak_data_ts-1):
                value = st.number_input(f"Masukkan Jumlah Mahasiswa TS-{i}:", step=0)
                ts_values.append(value)     
        else:
            input_banyak_data_ts = 1
            input_ambang_batas_jumlah = st.number_input("Ambang Batas Jumlah Mahasiswa Minimal", min_value=1, step=1)
            input_jumlah_mahasiswa_ts = st.number_input(f"Masukkan Jumlah Mahasiswa Tahun {input_last_year} (TS-0):", step=0)
            input_ambang_batas_persen = None
            input_fields = None
            ts_values.append(input_jumlah_mahasiswa_ts)

    model = pickle.load(open(r"D:\jumapro\next_year_students_prediction.sav", "rb"))


    # if input_kriteria == "Jumlah Mahasiswa":
    #     new_data_prodi = {
    #         'Prodi': [input_prodi],
    #         'current_students': [input_jumlah_mahasiswa_ts]
    #     }
    # else:
    #     new_data_prodi = {
    #         'Prodi': [input_prodi],
    #         'current_students': [input_fields[list(input_fields.keys())[0]]]
    #     }
    # st.write(ts_values)
    new_data_prodi = {
        'Prodi': [input_prodi],
        'current_students': ts_values[0]
    }

    data_prodi = pd.DataFrame(new_data_prodi)

    # Prediksi beberapa tahun ke depan
    current_students = data_prodi['current_students'].copy()

    tahun_tidak_lolos = f"Lebih dari {input_years_to_predict} Tahun ke Depan"  # Default value

    for i in range(1, input_years_to_predict + 1):
        next_year = input_last_year + i
        column_name = f'{next_year} (Prediksi)'
        data_prodi[column_name] = model.predict(current_students.values.reshape(-1, 1))
        data_prodi[column_name] = data_prodi[column_name].astype(int)
        current_students = data_prodi[column_name].copy()
        if tahun_tidak_lolos == f"Lebih dari {input_years_to_predict} Tahun ke Depan":  # Only update if no year has been set yet
            if input_kriteria == "Jumlah Mahasiswa":
                if data_prodi[column_name].values[0] < input_ambang_batas_jumlah:
                    tahun_tidak_lolos = next_year
                    
            elif input_kriteria == "Persentase Penurunan":
                ambang_batas_jumlah_mahasiswa = int(data_prodi["current_students"].values[0] * (1 - input_ambang_batas_persen / 100))
                if data_prodi[column_name].values[0] < ambang_batas_jumlah_mahasiswa:
                    tahun_tidak_lolos = next_year

    ts_values.insert(0, data_prodi[f"{input_predict_year} (Prediksi)"].item())
    # st.write(ts_values)

    data_predict_years = [f"{next_year} (Prediksi)" for next_year in range(input_predict_year+1, input_predict_year+input_years_to_predict)]
    data_predict_target= [f"{input_predict_year} (Prediksi)"]
    
    # Fungsi untuk menghitung persentase penurunan
    # def hitung_persentase_penurunan(data, predict_year):
    #     # data_mahasiswa_start_year = input_fields["input_jumlah_mahasiswa_ts0"]
    #     # end_year = predict_year
    #     # penurunan_total = (data[f"{end_year} (Prediksi)"] - data_mahasiswa_start_year)
    #     # persentase_penurunan = (penurunan_total / 2) * 100
    #     # return persentase_penurunan
    #     ts_1 = data[f"{predict_year} (Prediksi)"]
    #     ts_0 = data["current_students"]
    #     penurunan = (ts_0 - ts_1) / ts_1

    #     persentase_penurunan = penurunan * 100

    #     return persentase_penurunan


    # # Fungsi untuk menghitung persentase penurunan dengan lebih dari satu tahun data
    # def hitung_persentase_penurunan_lebih_dari_satu(data, predict_year, banyak_data_ts):
    #     total_penurunan = 0

    #     # Iterasi dari TS-1 hingga TS-n (n = banyak_data_ts)
    #     for i in range(int(banyak_data_ts) - 1):
    #         if i == 0:
    #             ts_1 = data[f"{predict_year} (Prediksi)"]
    #             ts_0 = data["current_students"]
    #         else:
    #             ts_1 = input_fields[f"input_jumlah_mahasiswa_ts{i-1}"]
    #             ts_0 = input_fields[f"input_jumlah_mahasiswa_ts{i}"]

    #         penurunan = (ts_0 - ts_1) / ts_1
    #         total_penurunan += penurunan

    #     # Hitung rata-rata penurunan
    #     rata_rata_penurunan = total_penurunan / (banyak_data_ts - 1)
    #     persentase_penurunan = rata_rata_penurunan * 100

    #     return persentase_penurunan

    # Perbarui fungsi prediksi_dan_penilaian untuk menggunakan fungsi yang baru

    # def prediksi_dan_penilaian(input_predict_year, input_last_year_data, input_kriteria, input_ambang_batas_jumlah, input_ambang_batas_persen, input_fields):
    if st.button("Prediksi Pemantauan Satu Prodi"):
    # Penilaian kelolosan berdasarkan kriteria
        if input_kriteria == "Jumlah Mahasiswa":
            current_students = input_jumlah_mahasiswa_ts
            hasil_prediksi_pemantauan = "Lolos" if data_prodi[f"{input_predict_year} (Prediksi)"].values[0] > input_ambang_batas_jumlah else "Tidak Lolos"
            ambang_batas_jumlah_mahasiswa = input_ambang_batas_jumlah
            data_prodi["Jumlah Mahasiswa Minimal"] = input_ambang_batas_jumlah
            data_prodi[f"Hasil Prediksi Pemantauan ({input_predict_year})"] = hasil_prediksi_pemantauan
            data_prodi["Tahun Tidak Lolos (Prediksi)"] = str(tahun_tidak_lolos)

            ordered_data_prodi = ["Prodi"] + ["current_students"] + data_predict_target + ["Jumlah Mahasiswa Minimal"] + [f"Hasil Prediksi Pemantauan ({input_predict_year})"] + data_predict_years + ["Tahun Tidak Lolos (Prediksi)"]
            tampil_data_prodi = data_prodi[ordered_data_prodi]
            tampil_data_prodi.rename(columns={'current_students': f'{input_last_year} (Saat Ini)'}, inplace=True)
            tampil_data_prodi["Tanggal Prediksi"] = date.today()
            ts_years = [input_last_year]

            # updated_dhp = pd.concat([existing_dhp, tampil_data_prodi], ignore_index=True)
            # conn.update(worksheet="Data Histori Prediksi Suatu Prodi", data=updated_dhp)
            # hasil_prodi = pd.DataFrame({
            #     'Prodi': [input_prodi],
            #     'Jumlah Mahasiswa TS': [input_jumlah_mahasiswa_ts],
            #     f'Jumlah Mahasiswa {input_predict_year} (Prediksi)': [ts_values[0]],
            #     f'Jumlah Mahasiswa Minimal': [input_ambang_batas_jumlah],
            #     f'Hasil Prediksi Pemantauan ({input_predict_year})': [hasil_prediksi_pemantauan],
            #     f'Jumlah Mahasiswa TS (Prediksi)': [data_predict_years],
            #     f'Tahun Tidak Lolos (Prediksi)': [tahun_tidak_lolos],
            #     'Tanggal Pemantauan': [date.today()]
            # })
    # [f"Hasil Prediksi Pemantauan ({input_predict_year})"] + data_predict_years + ["Tahun Tidak Lolos (Prediksi)"]
            # tampil_data_prodi = data_prodi[ordered_data_prodi]
        elif input_kriteria == "Persentase Penurunan":

            # if input_banyak_data_ts > 2:
            #     persentase_penurunan = hitung_persentase_penurunan_lebih_dari_satu(data_prodi, input_predict_year, input_banyak_data_ts)
            # else:
            #     persentase_penurunan = hitung_persentase_penurunan(data_prodi, input_predict_year)
            
            persentase_penurunan=calculate_persentase_penurunan(ts_values)
            hasil_prediksi_pemantauan = "Lolos" if persentase_penurunan <= input_ambang_batas_persen else "Tidak Lolos"
            ambang_batas_jumlah_mahasiswa = calculate_ts0_minimal(ts_values, input_ambang_batas_persen)
            
            # convert_percent_to_ambang_batas_jumlah_mahasiswa = int(data_prodi["current_students"].values[0] * (1 - input_ambang_batas_persen / 100))
            # ambang_batas_jumlah_mahasiswa = int(data_prodi["current_students"] * (1 - input_ambang_batas_persen / 100))
            data_prodi["Hitung Persentase Penurunan"] = persentase_penurunan
            data_prodi["Persentase Penurunan Maksimal"] = f"{input_ambang_batas_persen}%"
            data_prodi["Ambang Batas Jumlah Mahasiswa Minimal"] = ambang_batas_jumlah_mahasiswa
            data_prodi[f"Hasil Prediksi Pemantauan ({input_predict_year})"] = hasil_prediksi_pemantauan
            data_prodi["Tahun Tidak Lolos (Prediksi)"] = str(tahun_tidak_lolos)
            # for i in ts_values:
            #     data_prodi["Jumlah Mahasiswa TS"] = ts_values

            # for i in ts_values:
            #     for i in range(int(input_banyak_data_ts-1))


            # {f"input_jumlah_mahasiswa_ts{i+1}": f"{input_last_year-i-1}" for i in range(int(input_banyak_data_ts-1))}
            ts_years = [input_last_year-i for i in range(int(input_banyak_data_ts-1))]
            ts_years.sort()
            ts = {year: [ts_values[len(ts_years)-i]] for i, year in enumerate(ts_years)} 
            for col, value in ts.items():
                if col!={input_predict_year}:
                    data_prodi[col] = value
            # ts_years.sort
            # ts_years = sorted(ts_years, reverse=True)
            # years = sorted(years, reverse=True)
            # ts = [f"input_jumlah_mahasiswa_ts{i}" for i in range(1, int(input_banyak_data_ts-1))]
            # ts = sorted(ts, reverse=True)

            # years = [input_last_year-i for i in range(int(input_banyak_data_ts-1))]
            # ts = {year: [ts_values[i + 1]] for i, year in enumerate(years)} 
            # st.write(ts.items())
            # df_ts = pd.DataFrame(ts)
            
            # st.write(df_ts)

            # for col, value in ts:
            #     st.write(col, value)




            # data_ts = [f"{input_last_year-i}" for i in range(int(input_banyak_data_ts-1))]
            

            ordered_data_prodi = ["Prodi"]  + ts_years + data_predict_target + ["Persentase Penurunan Maksimal"] + ["Hitung Persentase Penurunan"] + [f"Hasil Prediksi Pemantauan ({input_predict_year})"] + ["Ambang Batas Jumlah Mahasiswa Minimal"] + data_predict_years + ["Tahun Tidak Lolos (Prediksi)"]
            tampil_data_prodi = data_prodi[ordered_data_prodi]
            tampil_data_prodi.rename(columns={'current_students': f'{input_last_year} (Saat Ini)'}, inplace=True)
            rename_ts = {f"input_jumlah_mahasiswa_ts{i+1}": f"{input_last_year-i-1}" for i in range(int(input_banyak_data_ts-1))}
            tampil_data_prodi.rename(columns=rename_ts, inplace=True)
            tampil_data_prodi.rename(columns={'current_students': f'{input_last_year} (Saat Ini)'}, inplace=True)
            tampil_data_prodi["Tanggal Prediksi"] = date.today()
            # updated_dhp = pd.concat([existing_dhp, tampil_data_prodi], ignore_index=True)
            # conn.update(worksheet="Data Histori Prediksi Suatu Prodi", data=updated_dhp)

            # hasil_prodi = pd.DataFrame({
            #     'Prodi': [input_prodi],
            #     'Jumlah Mahasiswa TS': [ts_values],
            #     # f'Jumlah Mahasiswa {input_predict_year} (Prediksi)': [ts_values[0]],
            #     'Persentase Penurunan Maksimal': [f"{input_ambang_batas_persen}%"],
            #     'Hitung Persentase Penurunan': [f"{persentase_penurunan:.2f}%"],
            #     f'Hasil Prediksi Pemantauan ({input_predict_year})': [hasil_prediksi_pemantauan],
            #     f'Jumlah Mahasiswa Minimal': [ambang_batas_jumlah],
            #     f'Jumlah Mahasiswa TS (Prediksi)': [data_predict_years],
            #     f'Tahun Tidak Lolos (Prediksi)': [tahun_tidak_lolos],
            #     'Tanggal Pemantauan': [date.today()]
            # })
        # return tampil_data_prodi
        # st.write(hasil_prodi)
        st.table(tampil_data_prodi)
        
        # st.write(data_prodi)
        # Grafik Scatter Plot
        predict_years = [next_year for next_year in range(input_predict_year, input_predict_year+input_years_to_predict)]
        predict_years_column =[col for col in data_prodi.columns if col in data_predict_years]
        predict_values = [ts_values[0]] + data_prodi[predict_years_column].iloc[0].tolist()
        
        # st.write(predict_years)
        # st.write(predict_values)

        ts_years = ts_years
        ts_values = ts_values[1:][::-1]

        # st.write(ts_years)
        # st.write(ts_values)

        
        all_years = ts_years + predict_years
        all_values = ts_values + predict_values


        # data = sorted(zip(all_years, all_values))
        # all_years, all_values = zip(*data)
        # sorted_indices = sorted(range(len(all_years)), key=lambda i: all_years[i])
        # all_years = [all_years[i] for i in sorted_indices]
        # all_values = [all_values[i] for i in sorted_indices]
        
        # all_years = [input_last_year - i for i in range(int(input_banyak_data_ts) - 1, -1, -1)] + [input_predict_year + i for i in range(input_years_to_predict)]
        # all_values = ts_values + predict_values.tolist()
        # st.write(all_years)
        # st.write(all_values)
        
        # st.write(ts_years)
        # st.write(ts_values)
        # st.write(predict_values)
        plt.figure(figsize=(10, 6))
        # years = list(range(input_last_year - int(input_banyak_data_ts) + 2, input_last_year + 2))
        # plt.scatter(years, ts_values[::-1], color='blue', label='Jumlah Mahasiswa')
        # plt.plot(years, ts_values[::-1], color='orange', label='Trend')
        
        # years = list(range(max(years) + 1, range(max(years) + input_years_to_predict)))
        # plt.scatter(predict_years, predict_values, color='green', marker='s', label='Nilai Prediksi')
        # plt.plot([input_predict_year] + predict_years, [ts_values[0]] + predict_values, 
        #  color='green', linestyle=':', alpha=0.7, label='Trend Prediksi')
        # predict_years = data_prodi.columns[data_predict_years]
        # st.write(predict_years)
        # st.write(predict_values)
        # plt.scatter(predict_years, predict_values, color='green', marker='s', label='Nilai Prediksi')
        # plt.plot(predict_years, predict_values, color='green', marker='s', label='Nilai Prediksi')
        # plt.plot([input_predict_year] + predict_years, [ts_values[0]] + predict_values, 
        # Plot data dengan warna berbeda untuk ts dan prediksi
        plt.scatter(ts_years, ts_values, color='blue', label='Data TS')
        plt.scatter(predict_years, predict_values, color='red', label='Data Prediksi')
        plt.plot(all_years, all_values)
        # plt.plot(all_years, all_values, color='orange')
        # Urutkan tahun dan nilai berdasarkan tahun
        # sorted_data = sorted(zip(all_years, all_values))
        # all_years_sorted, all_values_sorted = zip(*sorted_data)
        # st.write(all_years)
        # st.write(all_values)

        # # Plot data dan prediksi
        # plt.plot(all_years_sorted, all_values_sorted, color='orange', label='Prediksi Terhubung')
                
        plt.axhline(y=ambang_batas_jumlah_mahasiswa, color='red', linestyle='--', label='Ambang Batas Jumlah Mahasiswa Minimal')
        plt.title('Jumlah Mahasiswa Tahun ke Tahun')
        plt.xlabel('Tahun')
        plt.ylabel('Jumlah Mahasiswa')
        # plt.xticks(predict_years)  # X-axis labels
        plt.xticks(ticks=range(min(all_years), max(all_years)+1), labels=range(min(all_years), max(all_years)+1))
        
        plt.legend()
        plt.grid()

        # Display the plot in Streamlit
        st.pyplot(plt)


    # Tampilkan hasil prediksi dan penilaian jika tombol "Prediksi" ditekan
    # if st.button("Prediksi Pemantauan Satu Prodi"):
        # hasil_prediksi = prediksi_dan_penilaian(input_prodi, input_predict_year, input_last_year, input_years_to_predict, input_kriteria, input_ambang_batas_jumlah, input_ambang_batas_persen, input_fields)
        # st.write(hasil_prediksi)
        # st.success("Data berhasil ditambahkan ke worksheet!")
        
# load_form_prediksi()
# prediksi_pemantauan_satu_prodi()