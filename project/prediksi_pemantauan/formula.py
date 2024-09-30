# prediksi_pemantauan/formula.py
import streamlit as st
from utils.data_access import get_gsheets_connection, read_worksheet, save_pickle, load_pickle
import pandas as pd

def formula():
    st.markdown("Masukkan Rumus Baru di Bawah Ini")

    conn = get_gsheets_connection()
    existing_data = read_worksheet(conn, worksheet="Rumus Pemantauan", usecols=list(range(7)))
    existing_data = existing_data.dropna(how="all")

    st.write(existing_data)

    existing_djm = read_worksheet(conn, worksheet="Data Jumlah Mahasiswa")
    existing_djm = existing_djm.dropna(how="all")
    existing_djm = existing_djm.replace('#N/A ()', 0)
    unused_columns = ['Kode Prodi', 'Kode Prodi UGM', 'Kode Fakultas', 'Departemen', 'Kluster']
    existing_djm = existing_djm.drop(unused_columns, axis=1, errors='ignore')
    lembaga_options = existing_djm['Lembaga'].unique()

    input_lembaga = st.selectbox("Pilih Lembaga : ", lembaga_options)
    input_nama_rumus = st.text_input("Masukkan Nama Rumus (ex: PEMPT) :")
    input_kriteria = st.radio("Kriteria", ["Persentase Penurunan", "Jumlah Mahasiswa"])

    if input_kriteria == "Persentase Penurunan":
        input_ambang_batas_persen = st.slider("Ambang Batas Persentase Penurunan Maksimal (%)", 0, 100, 5)
        input_banyak_data_ts = st.slider("Masukkan Banyak Tahun yang Dipakai untuk Persentase Penurunan : ", min_value=2, max_value=5, step=1)
        input_ambang_batas_jumlah = None
    else:
        input_ambang_batas_jumlah = st.number_input("Ambang Batas Jumlah Mahasiswa Minimal", min_value=1, step=1)
        input_ambang_batas_persen = None
        input_banyak_data_ts = None

    input_tanggal_mulai = st.date_input("Tanggal Mulai Berlaku")
    input_keterangan = st.text_area("Keterangan")

    if st.button("Tambah Rumus"):
        if not input_lembaga or not input_nama_rumus:
            st.warning("Pastikan semua field wajib diisi.")
            st.stop()
        elif existing_data["Nama Rumus"].str.contains(input_nama_rumus).any():
            st.warning("Rumus dengan nama ini sudah ada.")
            st.stop()
        else:
            new_data = pd.DataFrame(
                [{
                    "Lembaga": input_lembaga,
                    "Nama Rumus": input_nama_rumus,
                    "Kriteria": input_kriteria,
                    "Banyak Data TS": input_banyak_data_ts,
                    "Ambang Batas (%)": input_ambang_batas_persen,
                    "Ambang Batas (Jumlah)": input_ambang_batas_jumlah,
                    "Tanggal Mulai Berlaku": input_tanggal_mulai,
                    "Keterangan": input_keterangan
                }]
            )

            updated_df = pd.concat([existing_data, new_data], ignore_index=True)
            save_pickle(updated_df, 'data/existing_formula.pickle')  # Simpan ke file pickle jika diperlukan

            # Jika ingin memperbarui Google Sheets, gunakan:
            conn.update(worksheet="Rumus Pemantauan", data=updated_df)

            st.success("Rumus berhasil ditambahkan!")
            st.write(updated_df)
