import numpy as np

def hitung_persentase_penurunan(data, predict_year, index=None):
    # Jika index disediakan, gunakan akses berbasis index dan `.at`, jika tidak, langsung dari data
    input_last_year = predict_year - 1

    if index is not None:
        ts_previous = data.at[index, f"{predict_year}"]
        ts_current = data.at[index, str(input_last_year)]
    else:
        ts_previous = data[f"{predict_year} (Prediksi)"]
        ts_current = data["current_students"]

    try:
        if ts_previous == 0.0 or np.isnan(ts_previous) or (ts_previous is None):
            return 0
    except Exception as e:
        print('ERROR:', index, type(ts_previous), ts_current, ts_previous)
        raise e

    # Hitung penurunan
    penurunan = (ts_current - ts_previous) / ts_previous
    persentase_penurunan = penurunan * 100

    return round(-persentase_penurunan, 2)

def hitung_persentase_penurunan_lebih_dari_satu(data, predict_year, banyak_data_ts, index=None, input_fields=None):
    """
    Menghitung persentase penurunan berdasarkan beberapa tahun data.
    Jika `index` disertakan, maka data diakses berdasarkan index,
    jika tidak, data diakses langsung dari parameter `data`.
    """
    total_penurunan = 0
    input_last_year = predict_year - 1
    
    for i in range(int(banyak_data_ts) - 1):
        if i == 0:
            # Jika index diberikan, ambil data dengan `iloc`
            if index is not None:
                ts_current = data.iloc[index][str(predict_year)]
                ts_previous = data.iloc[index][str(input_last_year)]
            else:
                ts_current = data[f"{predict_year} (Prediksi)"]
                ts_previous = data["current_students"]
        else:
            # Jika menggunakan input_fields
            if input_fields is not None and index is not None:
                ts_current = input_fields[f"input_jumlah_mahasiswa_ts{i}"][index]
                ts_previous = input_fields[f"input_jumlah_mahasiswa_ts{i-1}"][index]
            else:
                ts_current = input_fields[f"input_jumlah_mahasiswa_ts{i}"]
                ts_previous = input_fields[f"input_jumlah_mahasiswa_ts{i-1}"]

                
        # Cek apakah ts_previous valid
        if ts_previous == 0 or np.isnan(ts_previous) or (ts_previous is None):
            return 0
        
        # Hitung penurunan
        penurunan = (ts_current - ts_previous) / ts_previous
        total_penurunan += penurunan

    # Hitung rata-rata penurunan
    rata_rata_penurunan = total_penurunan / (banyak_data_ts - 1)
    persentase_penurunan = rata_rata_penurunan * 100

    return round(persentase_penurunan, 2)
