
def dashboard():

    import streamlit as st
    from streamlit_gsheets import GSheetsConnection

    # Establishing a Google Sheets connection
    conn = st.connection("gsheets", type=GSheetsConnection)

    # # Fetch data dhp = data history prediction
    # existing_dhp = conn.read(worksheet="Data Histori Prediksi Suatu Prodi", ttl=5)
    # existing_dhp = existing_dhp.dropna(how="all")

    # Fetch data djm = data jumlah mahasiswa
    existing_djm = conn.read(worksheet="Data Jumlah Mahasiswa")
    existing_djm = existing_djm.dropna(how="all")
    existing_djm = existing_djm.replace('#N/A ()', 0)

    import streamlit as st

    # Membuat dashboard header
    st.title("Dashboard Program Studi")

    # Membuat kolom untuk input
    with st.form(key='search_form'):
        col1, col2, col3 = st.columns([3, 2, 2])
        with col1:
            st.text_input("Cari Program Studi", placeholder="Masukkan nama program studi")
        with col2:
            fakultas = st.selectbox("Fakultas", ["Semua Fakultas", "Fakultas Kedokteran", "Fakultas Teknik", "Fakultas Ekonomi"])
        with col3:
            st.text_input("Prodi", placeholder="Masukkan prodi")

        # Tombol submit
        submitted = st.form_submit_button("SPMRU UGM")
        if submitted:
            st.write(f"Mencari Program Studi di {fakultas}")

    # Membuat metrik untuk jumlah prodi dan jumlah fakultas
    col4, col5 = st.columns([1, 1])
    with col4:
        st.metric("Jumlah Prodi", 289)
    with col5:
        st.metric("Jumlah Fakultas/Sekolah", 20)

    # Membuat kolom untuk tabel ranking dan jumlah
    col6, col7, col8 = st.columns([1, 1, 1])

    # Tabel Peringkat
    with col6:
        st.subheader("Peringkat")
        data_peringkat = {
            "Peringkat": ["Unggul", "A", "Baik Sekali", "Baik", "Minimum"],
            "Jumlah Prodi": [144, 94, 31, 14, 6]
        }
        st.table(data_peringkat)

    # Tabel Jenjang
    with col7:
        st.subheader("Jenjang")
        data_jenjang = {
            "Jenjang": ["S-1", "D4", "S-3", "S-2", "Sp1", "Sp2"],
            "Jumlah Prodi": [71, 12, 19, 51, 32, 4]
        }
        st.table(data_jenjang)

    # Tabel Lembaga Akreditasi
    with col8:
        st.subheader("Lembaga Akreditasi")
        data_lembaga = {
            "Lembaga Akreditasi": ["LAMEMBA", "LAMTEKNIK", "LAMKES", "LAMINFORM", "BAN-PT"],
            "Jumlah Prodi": [23, 29, 21, 34, 142]
        }
        st.table(data_lembaga)


        
