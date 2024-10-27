    # import streamlit as st
    # from streamlit_gsheets import GSheetsConnection

    # # Establishing a Google Sheets connection
    # conn = st.connection("gsheets", type=GSheetsConnection)

    # # # Fetch data dhp = data history prediction
    # # existing_dhp = conn.read(worksheet="Data Histori Prediksi Suatu Prodi", ttl=5)
    # # existing_dhp = existing_dhp.dropna(how="all")

    # # Fetch data djm = data jumlah mahasiswa
    # existing_djm = conn.read(worksheet="Data Jumlah Mahasiswa", ttl=5)
    # existing_djm = existing_djm.dropna(how="all")
    # existing_djm = existing_djm.replace('#N/A ()', 0)

    # unused_column = ['Kode Prodi', 'Kode Prodi UGM', 'Kode Fakultas', 'Departemen', 'Kluster']
    # existing_djm = existing_djm.drop(unused_column, axis=1)
    # existing_djm


import streamlit as st
from component.data import get_data, refresh_data, preprocess_data

def dashboard(existing_djm):

    # 1. Connections from google sheets
    # if st.button('Refresh Data'):
    #     existing_djm = refresh_data('djm')
    #     st.success("Data berhasil dimuat ulang dari Google Sheets!")
    # else:
    # # 2. Connections from pickle
    #     existing_djm = get_data('djm')
    # # st.write(existing_djm)
    #  # 3. Data preprocessing
    # existing_djm = preprocess_data(existing_djm)


    # Menghitung jumlah prodi berdasarkan fakultas
    fakultas_counts = existing_djm['Fakultas'].value_counts()
    
    # Menghitung jumlah prodi berdasarkan peringkat
    peringkat_counts = existing_djm['Peringkat'].value_counts()

    # Menghitung jumlah prodi berdasarkan jenjang
    jenjang_counts = existing_djm['Jenjang'].value_counts()

    # Menghitung jumlah prodi berdasarkan lembaga akreditasi
    lembaga_counts = existing_djm['Lembaga'].value_counts()

    # Membuat dashboard header
    # st.title("Dashboard Program Studi")
    st.markdown("Dashboard Historis Jumlah Mahasiswa Program Studi Magister dan Doktor di Universitas Gadjah Mada")


    col9, col10 = st.columns([1, 1])

    with col9:
        # st.subheader("Peringkat")
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
    
    with col10:
        data_pemantauan = {
            "Masa Berlaku Akreditasi": ["Lebih Dari 1 Tahun", "6-12 Bulan", "1-6 Bulan", "Kurang Dari 1 Bulan"],
            "Jumlah Prodi": [lebih_dari_1_tahun, enam_duabelas_bulan, satu_enam_bulan, kurang_dari_satu_bulan]
        }
        st.table(data_pemantauan)

        # Membuat kolom untuk tabel ranking dan jumlah
    # data = {
    #     "Keterangan": ["Jumlah Prodi", "Jumlah Fakultas/Sekolah"],
    #     "Jumlah": [144, 94]
    # }
    # st.table(data)

    # existing_djm
    st.write(existing_djm)

    col6, col7, col8 = st.columns([1, 1, 1])

    # Tabel Peringkat
    with col6:
        # st.subheader("Peringkat")
        data_fakultas = {
            "Fakultas": fakultas_counts.index.tolist(),
            "Jumlah Prodi": fakultas_counts.values.tolist()
        }
        st.table(data_fakultas)

    # Tabel Jenjang
    with col7:
        # st.subheader("Jenjang")
        data_lembaga = {
            "Lembaga Akreditasi": lembaga_counts.index.tolist(),
            "Jumlah Prodi": lembaga_counts.values.tolist()
        }
        st.table(data_lembaga)
    # Tabel Lembaga Akreditasi
    with col8:
        # st.subheader("Lembaga")
        data_jenjang = {
            "Jenjang": jenjang_counts.index.tolist(),
            "Jumlah Prodi": jenjang_counts.values.tolist()
        }
        st.table(data_jenjang)

    # st.write(existing_djm[2013])