# pages/dashboard.py
import streamlit as st
from data.gsheets import read_worksheet
import pandas as pd

def dashboard():
    existing_djm = read_worksheet("Data Jumlah Mahasiswa")
    existing_djm = existing_djm.dropna(how="all")
    existing_djm = existing_djm.replace('#N/A ()', 0)

    unused_columns = ['Kode Prodi', 'Kode Prodi UGM', 'Kode Fakultas', 'Departemen', 'Kluster']
    existing_djm = existing_djm.drop(unused_columns, axis=1, errors='ignore')

    # Menghitung jumlah prodi berdasarkan fakultas
    fakultas_counts = existing_djm['Fakultas'].value_counts()

    # Menghitung jumlah prodi berdasarkan peringkat
    peringkat_counts = existing_djm['Peringkat'].value_counts()

    # Menghitung jumlah prodi berdasarkan jenjang
    jenjang_counts = existing_djm['Jenjang'].value_counts()

    # Menghitung jumlah prodi berdasarkan lembaga akreditasi
    lembaga_counts = existing_djm['Lembaga'].value_counts()

    st.markdown("Dashboard Historis Jumlah Mahasiswa Semua Program Studi")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Peringkat")
        data_peringkat = {
            "Akreditasi": peringkat_counts.index.tolist(),
            "Jumlah Prodi": peringkat_counts.values.tolist()
        }
        st.table(data_peringkat)

        # Menghitung jumlah prodi berdasarkan nilai Kadaluarsa
        lebih_dari_1_tahun = len(existing_djm[existing_djm['Kadaluarsa'] > 365])
        enam_duabelas_bulan = len(existing_djm[(existing_djm['Kadaluarsa'] >= 184) & (existing_djm['Kadaluarsa'] <= 365)])
        satu_enam_bulan = len(existing_djm[(existing_djm['Kadaluarsa'] >= 31) & (existing_djm['Kadaluarsa'] <= 183)])
        kurang_dari_satu_bulan = len(existing_djm[existing_djm['Kadaluarsa'] < 30])

    with col2:
        st.subheader("Masa Berlaku Akreditasi")
        data_pemantauan = {
            "Masa Berlaku Akreditasi": ["Lebih Dari 1 Tahun", "6-12 Bulan", "1-6 Bulan", "Kurang Dari 1 Bulan"],
            "Jumlah Prodi": [lebih_dari_1_tahun, enam_duabelas_bulan, satu_enam_bulan, kurang_dari_satu_bulan]
        }
        st.table(data_pemantauan)

    # Menampilkan DataFrame
    st.write(existing_djm)

    col3, col4, col5 = st.columns(3)

    with col3:
        st.subheader("Fakultas")
        data_fakultas = {
            "Fakultas": fakultas_counts.index.tolist(),
            "Jumlah Prodi": fakultas_counts.values.tolist()
        }
        st.table(data_fakultas)

    with col4:
        st.subheader("Lembaga Akreditasi")
        data_lembaga = {
            "Lembaga Akreditasi": lembaga_counts.index.tolist(),
            "Jumlah Prodi": lembaga_counts.values.tolist()
        }
        st.table(data_lembaga)

    with col5:
        st.subheader("Jenjang")
        data_jenjang = {
            "Jenjang": jenjang_counts.index.tolist(),
            "Jumlah Prodi": jenjang_counts.values.tolist()
        }
        st.table(data_jenjang)

    # Optional: Menyimpan data yang dibersihkan ke file pickle untuk digunakan di modul lain
    # from data.gsheets import save_pickle
    # save_pickle(existing_djm, 'data/existing_djm.pickle')
