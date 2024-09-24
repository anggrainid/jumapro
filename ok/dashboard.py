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

