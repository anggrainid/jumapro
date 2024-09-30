# dashboard.py
import streamlit as st
from utils.data_access import get_gsheets_connection, read_worksheet, load_pickle
from utils.data_processing import clean_data
import pandas as pd

def dashboard():
    conn = get_gsheets_connection()
    existing_djm = read_worksheet(conn, worksheet="Data Jumlah Mahasiswa")
    existing_djm = clean_data(existing_djm, unused_columns=['Kode Prodi', 'Kode Prodi UGM', 'Kode Fakultas', 'Departemen', 'Kluster'])

    st.markdown("Dashboard Historis Jumlah Mahasiswa Semua Program Studi")

    # Menghitung statistik
    fakultas_counts = existing_djm['Fakultas'].value_counts()
    peringkat_counts = existing_djm['Peringkat'].value_counts()
    jenjang_counts = existing_djm['Jenjang'].value_counts()
    lembaga_counts = existing_djm['Lembaga'].value_counts()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Peringkat")
        st.table({
            "Akreditasi": peringkat_counts.index.tolist(),
            "Jumlah Prodi": peringkat_counts.values.tolist()
        })

        lebih_dari_1_tahun = len(existing_djm[existing_djm['Kadaluarsa'] > 365])
        enam_duabelas_bulan = len(existing_djm[(existing_djm['Kadaluarsa'] >= 184) & (existing_djm['Kadaluarsa'] <= 365)])
        satu_enam_bulan = len(existing_djm[(existing_djm['Kadaluarsa'] >= 31) & (existing_djm['Kadaluarsa'] <= 183)])
        kurang_dari_satu_bulan = len(existing_djm[existing_djm['Kadaluarsa'] < 30])

    with col2:
        st.subheader("Masa Berlaku Akreditasi")
        st.table({
            "Masa Berlaku Akreditasi": ["Lebih Dari 1 Tahun", "6-12 Bulan", "1-6 Bulan", "Kurang Dari 1 Bulan"],
            "Jumlah Prodi": [lebih_dari_1_tahun, enam_duabelas_bulan, satu_enam_bulan, kurang_dari_satu_bulan]
        })

    # Menampilkan DataFrame
    st.write(existing_djm)

    col3, col4, col5 = st.columns(3)

    with col3:
        st.subheader("Fakultas")
        st.table({
            "Fakultas": fakultas_counts.index.tolist(),
            "Jumlah Prodi": fakultas_counts.values.tolist()
        })

    with col4:
        st.subheader("Lembaga Akreditasi")
        st.table({
            "Lembaga Akreditasi": lembaga_counts.index.tolist(),
            "Jumlah Prodi": lembaga_counts.values.tolist()
        })

    with col5:
        st.subheader("Jenjang")
        st.table({
            "Jenjang": jenjang_counts.index.tolist(),
            "Jumlah Prodi": jenjang_counts.values.tolist()
        })

    # Optional: Menyimpan data yang dibersihkan ke file pickle untuk digunakan di modul lain
    from utils.data_access import save_pickle
    save_pickle(existing_djm, 'data/existing_djm.pickle')
