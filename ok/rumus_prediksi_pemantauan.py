import pandas as pd
import numpy as np

# gabung
def hitung_persentase_penurunan(data=None, ts_values=None, predict_year=None, index=None, banyak_data_ts=None, input_fields=None):
    """
    Menghitung persentase penurunan berdasarkan data time series.
    
    - Jika `ts_values` disediakan, fungsi akan menghitung persentase penurunan dari array time series (seperti pada fungsi pemantauan).
    - Jika `data`, `predict_year`, dan `index` disediakan, fungsi akan menghitung penurunan berdasarkan DataFrame dan tahun prediksi.
    
    Parameters:
    - data: DataFrame atau dict yang berisi data jumlah mahasiswa (untuk prediksi).
    - ts_values: List jumlah mahasiswa dari tahun-tahun sebelumnya (untuk pemantauan).
    - predict_year: Tahun prediksi yang ingin digunakan (hanya jika `data` digunakan).
    - index: (Optional) Index dari data untuk mengakses baris yang relevan (untuk prediksi).
    - banyak_data_ts: (Optional) Jumlah data tahun sebelumnya untuk menghitung penurunan rata-rata (untuk prediksi).
    - input_fields: (Optional) Field input tambahan jika digunakan (untuk prediksi).
    
    Returns:
    - persentase_penurunan: Persentase penurunan yang dihitung.
    """

    # Jika menggunakan ts_values (untuk pemantauan)
    if ts_values is not None:
        total_penurunan = 0
        valid_years = 0

        for i in range(1, len(ts_values)):
            ts_current = ts_values[i]
            ts_previous = ts_values[i - 1]

            if ts_current == 0 or pd.isna(ts_current) or (ts_current is None):
                return 0.0

            penurunan = (ts_previous - ts_current) / ts_current
            total_penurunan += penurunan
            valid_years += 1

        if valid_years == 0:
            return 0.0

        rata_rata_penurunan = total_penurunan / valid_years
        persentase_penurunan = rata_rata_penurunan * 100
        return round(-persentase_penurunan, 2)

    # Jika menggunakan data (untuk prediksi)
    elif data is not None and predict_year is not None:
        total_penurunan = 0
        valid_years = 0
        input_last_year = predict_year - 1

        # Jika hanya satu tahun data, hitung penurunan langsung dari prediksi dan jumlah mahasiswa saat ini
        if banyak_data_ts is None or banyak_data_ts <= 1:
            if index is not None:
                ts_1 = data.at[index, f"{predict_year}"]
                ts_0 = data.at[index, str(input_last_year)]
            else:
                ts_1 = data[f"{predict_year} (Prediksi)"]
                ts_0 = data["current_students"]

            if ts_1 == 0 or pd.isna(ts_1) or (ts_1 is None):
                return 0.0

            penurunan = (ts_0 - ts_1) / ts_1
            persentase_penurunan = penurunan * 100
            return round(persentase_penurunan, 2)

        # Jika banyak_data_ts lebih dari 1, hitung rata-rata penurunan dari beberapa tahun data
        else:
            for i in range(int(banyak_data_ts) - 1):
                if i == 0:
                    if index is not None:
                        ts_1 = data.at[index, f"{predict_year}"]
                        ts_0 = data.at[index, str(input_last_year)]
                    else:
                        ts_1 = data[f"{predict_year} (Prediksi)"]
                        ts_0 = data["current_students"]
                else:
                    ts_1 = input_fields[f"input_jumlah_mahasiswa_ts{i-1}"][index]
                    ts_0 = input_fields[f"input_jumlah_mahasiswa_ts{i}"][index]

                if ts_1 == 0 or pd.isna(ts_1) or (ts_1 is None):
                    return 0.0

                penurunan = (ts_0 - ts_1) / ts_1
                total_penurunan += penurunan
                valid_years += 1

            if valid_years == 0:
                return 0.0

            rata_rata_penurunan = total_penurunan / valid_years
            persentase_penurunan = rata_rata_penurunan * 100
            return round(persentase_penurunan, 2)

    # Jika tidak ada input yang valid
    else:
        raise ValueError("Either 'ts_values' or 'data' and 'predict_year' must be provided.")




# Pemantauan
# pemantauan satu prodi
def hitung_persentase_penurunan_pemantauan(ts_values):
    """
    Menghitung persentase penurunan berdasarkan data time series.
    ts_values: List of jumlah mahasiswa dari tahun-tahun sebelumnya (TS-n, ..., TS-1, TS-0)
    """
    total_penurunan = 0
    valid_years = 0
    
    for i in range(1, len(ts_values)):
        ts_current = ts_values[i]
        ts_previous = ts_values[i - 1]
        
        if ts_current == 0 or pd.isna(ts_current) or (ts_current is None):
            return 0.0
        
        penurunan = (ts_previous - ts_current) / ts_current
        total_penurunan += penurunan
        valid_years += 1
    
    if valid_years == 0:
        return 0.0
    
    rata_rata_penurunan = total_penurunan / valid_years
    persentase_penurunan = rata_rata_penurunan * 100
    return round(-persentase_penurunan, 2)

def hitung_persentase_penurunan_prediksi(data, predict_year, index=None, banyak_data_ts=None, input_fields=None):
    """
    Menghitung persentase penurunan berdasarkan data time series.
    
    Jika banyak_data_ts disediakan, fungsi akan menghitung rata-rata penurunan berdasarkan lebih dari satu tahun data.
    Jika tidak, hanya menghitung penurunan dari tahun saat ini ke tahun prediksi (default 2 tahun).
    
    Parameters:
    - data: DataFrame atau dict yang berisi data jumlah mahasiswa.
    - predict_year: Tahun prediksi yang ingin digunakan.
    - index: (Optional) Index dari data untuk mengakses baris yang relevan.
    - banyak_data_ts: (Optional) Jumlah data tahun sebelumnya untuk menghitung penurunan rata-rata.
    - input_fields: (Optional) Field input tambahan jika digunakan.
    
    Returns:
    - persentase_penurunan: Persentase penurunan yang dihitung.
    """
    
    total_penurunan = 0
    valid_years = 0
    input_last_year = predict_year - 1

    # Jika hanya satu tahun data, hitung penurunan langsung dari prediksi dan jumlah mahasiswa saat ini
    if banyak_data_ts is None or banyak_data_ts <= 1:
        if index is not None:
            ts_1 = data.at[index, f"{predict_year}"]
            ts_0 = data.at[index, str(input_last_year)]
        else:
            ts_1 = data[f"{predict_year} (Prediksi)"]
            ts_0 = data["current_students"]

        # Jika salah satu nilai tidak valid, return 0.0
        if ts_1 == 0 or pd.isna(ts_1) or (ts_1 is None):
            return 0.0

        penurunan = (ts_0 - ts_1) / ts_1
        persentase_penurunan = penurunan * 100
        return round(persentase_penurunan, 2)

    # Jika banyak_data_ts lebih dari 1, hitung rata-rata penurunan dari beberapa tahun data
    else:
        for i in range(int(banyak_data_ts) - 1):
            if i == 0:
                if index is not None:
                    ts_1 = data.at[index, f"{predict_year}"]
                    ts_0 = data.at[index, str(input_last_year)]
                else:
                    ts_1 = data[f"{predict_year} (Prediksi)"]
                    ts_0 = data["current_students"]
            else:
                ts_1 = input_fields[f"input_jumlah_mahasiswa_ts{i-1}"][index]
                ts_0 = input_fields[f"input_jumlah_mahasiswa_ts{i}"][index]

            # Jika nilai ts_1 tidak valid, return 0.0
            if ts_1 == 0 or pd.isna(ts_1) or (ts_1 is None):
                return 0.0

            penurunan = (ts_0 - ts_1) / ts_1
            total_penurunan += penurunan
            valid_years += 1

        # Jika tidak ada tahun yang valid, return 0.0
        if valid_years == 0:
            return 0.0

        # Hitung rata-rata penurunan
        rata_rata_penurunan = total_penurunan / valid_years
        persentase_penurunan = rata_rata_penurunan * 100
        return round(persentase_penurunan, 2)




# pemantauan semua prodi
# def calculate_persentase_penurunan_all(ts_values):
#     """
#     Menghitung persentase penurunan berdasarkan data time series.
#     ts_values: List of jumlah mahasiswa dari tahun-tahun sebelumnya (TS-n, ..., TS-1, TS-0)
#     """
#     total_penurunan = 0
#     valid_years = 0
    
#     for i in range(1, len(ts_values)):
#         ts_current = ts_values[i]
#         ts_previous = ts_values[i - 1]
        
#         if ts_current == 0 or pd.isna(ts_current) or (ts_current is None):
#             return 0
        
#         penurunan = (ts_previous - ts_current) / ts_current
#         total_penurunan += penurunan
#         valid_years += 1
    
#     if valid_years == 0:
#         return 0
    
#     rata_rata_penurunan = total_penurunan / valid_years
#     persentase_penurunan = rata_rata_penurunan * 100
#     return round(-persentase_penurunan, 2)

# # prediksi satu prodi

# def hitung_persentase_penurunan_prediksi_satu_prodi(data, predict_year, banyak_data_ts=None, input_fields=None):
#     """
#     Menghitung persentase penurunan berdasarkan data time series.
    
#     Jika banyak_data_ts disediakan, fungsi akan menghitung rata-rata penurunan berdasarkan lebih dari satu tahun data.
#     Jika tidak, hanya menghitung penurunan dari tahun saat ini ke tahun prediksi (default 2 tahun).
    
#     Parameters:
#     - data: DataFrame atau dict yang berisi data jumlah mahasiswa.
#     - predict_year: Tahun prediksi yang ingin digunakan.
#     - banyak_data_ts: (Optional) Jumlah data tahun sebelumnya untuk menghitung penurunan rata-rata.
#     - input_fields: (Optional) Field input tambahan jika digunakan.
    
#     Returns:
#     - persentase_penurunan: Persentase penurunan yang dihitung.
#     """
#     total_penurunan = 0
#     valid_years = 0
    
#     # Jika hanya satu prediksi (default dari predict_year dan current_students)
#     if banyak_data_ts is None or banyak_data_ts <= 1:
#         ts_1 = data[f"{predict_year} (Prediksi)"]
#         ts_0 = data["current_students"]
        
#         # Jika salah satu nilai tidak valid, return 0.0
#         if ts_1 == 0 or pd.isna(ts_1) or (ts_1 is None):
#             return 0.0
        
#         penurunan = (ts_0 - ts_1) / ts_1
#         persentase_penurunan = penurunan * 100
#         return round(persentase_penurunan, 2)

#     # Jika banyak_data_ts lebih dari 1 (menghitung rata-rata penurunan berdasarkan beberapa tahun data)
#     else:
#         for i in range(int(banyak_data_ts) - 1):
#             if i == 0:
#                 ts_1 = data[f"{predict_year} (Prediksi)"]
#                 ts_0 = data["current_students"]
#             else:
#                 ts_1 = input_fields[f"input_jumlah_mahasiswa_ts{i-1}"]
#                 ts_0 = input_fields[f"input_jumlah_mahasiswa_ts{i}"]

#             # Jika nilai ts_1 tidak valid, return 0.0
#             if ts_1 == 0 or pd.isna(ts_1) or (ts_1 is None):
#                 return 0.0
            
#             penurunan = (ts_0 - ts_1) / ts_1
#             total_penurunan += penurunan
#             valid_years += 1

#         # Jika tidak ada tahun yang valid, return 0.0
#         if valid_years == 0:
#             return 0.0

#         # Hitung rata-rata penurunan
#         rata_rata_penurunan = total_penurunan / valid_years
#         persentase_penurunan = rata_rata_penurunan * 100
#         return round(persentase_penurunan, 2)
    
# # prediksi semau prodi

# def hitung_persentase_penurunan_prediksi_semua_prodi(data, predict_year, index=None, banyak_data_ts=None, input_fields=None):
#     """
#     Menghitung persentase penurunan berdasarkan data time series.
    
#     Parameters:
#     - data: DataFrame yang berisi data jumlah mahasiswa.
#     - predict_year: Tahun prediksi yang digunakan.
#     - index: Index dari data untuk mengakses baris yang relevan.
#     - banyak_data_ts: (Optional) Jumlah tahun data time series untuk menghitung rata-rata penurunan.
#     - input_fields: (Optional) Input tambahan yang berisi jumlah mahasiswa dari tahun-tahun sebelumnya.
    
#     Returns:
#     - Persentase penurunan yang dihitung. Jika ada nilai tidak valid, akan mengembalikan 0.0.
#     """
    
#     total_penurunan = 0
#     valid_years = 0
#     input_last_year = predict_year - 1

#     # Jika hanya satu tahun data, hitung penurunan langsung dari prediksi dan jumlah mahasiswa saat ini
#     if banyak_data_ts is None or banyak_data_ts <= 1:
#         ts_1 = data.at[index, f"{predict_year}"]
#         ts_0 = data.at[index, str(input_last_year)]

#         if ts_1 == 0 or pd.isna(ts_1) or (ts_1 is None):
#             return 0.0

#         penurunan = (ts_0 - ts_1) / ts_1
#         return round(penurunan * 100, 2)

#     # Jika banyak_data_ts lebih dari 1, hitung rata-rata penurunan dari beberapa tahun data
#     else:
#         for i in range(int(banyak_data_ts) - 1):
#             if i == 0:
#                 ts_1 = data.at[index, f"{predict_year}"]
#                 ts_0 = data.at[index, str(input_last_year)]
#             else:
#                 ts_1 = input_fields[f"input_jumlah_mahasiswa_ts{i-1}"][index]
#                 ts_0 = input_fields[f"input_jumlah_mahasiswa_ts{i}"][index]

#             if ts_1 == 0 or pd.isna(ts_1) or (ts_1 is None):
#                 return 0.0

#             penurunan = (ts_0 - ts_1) / ts_1
#             total_penurunan += penurunan
#             valid_years += 1

#         if valid_years == 0:
#             return 0.0

#         rata_rata_penurunan = total_penurunan / valid_years
#         persentase_penurunan = rata_rata_penurunan * 100
#         return round(persentase_penurunan, 2)