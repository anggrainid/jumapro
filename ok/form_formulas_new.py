def formula():
    import streamlit as st
    from streamlit_gsheets import GSheetsConnection
    import pandas as pd

    # Display Title and Description
    # st.title("Manajemen Rumus Pemantauan")
    st.markdown("Masukkan Rumus Baru di Bawah Ini")

    # Establishing a Google Sheets connection
    conn = st.connection("gsheets", type=GSheetsConnection)

    # Fetch existing vendors data
    existing_data = conn.read(worksheet="Rumus Pemantauan", usecols=list(range(7)), ttl=5)
    existing_data = existing_data.dropna(how="all")
    st.write(existing_data)


    existing_djm = conn.read(worksheet="Data Jumlah Mahasiswa")
    existing_djm = existing_djm.dropna(how="all")
    # Dropdown options for Lembaga
    lembaga_options = existing_djm['Lembaga'].unique()


    input_lembaga = st.selectbox("Pilih Lembaga : ", lembaga_options)
    input_nama_rumus = st.text_input("Masukkan Nama Rumus (ex: PEMPT) :")
    input_kriteria = st.radio("Kriteria", ["Persentase Penurunan", "Jumlah Mahasiswa"])


    if input_kriteria == "Persentase Penurunan":
        input_ambang_batas_persen = st.slider("Ambang Batas Persentase Penurunan Maksimal (%)",0,100,5)
        input_banyak_data_ts = st.slider("Masukkan Banyak Tahun yang Dipakai untuk Persentase Penurunan : ", min_value=2, max_value=5, step=1)
        input_ambang_batas_jumlah = None
    else:
        input_ambang_batas_jumlah = st.number_input("Ambang Batas Jumlah Mahasiswa Minimal", min_value=1, step=1)
        input_ambang_batas_persen = None
        input_banyak_data_ts = None

    input_tanggal_mulai = st.date_input("Tanggal Mulai Berlaku", value="default_value_today")
    input_keterangan = st.text_area("Keterangan")


    # If the submit button is pressed
    if st.button("Tambah Rumus"):
        # Check if all mandatory fields are filled
        if not input_lembaga or not input_nama_rumus:
            st.warning("Ensure all mandatory fields are filled.")
            st.stop()
        elif existing_data["Nama Rumus"].str.contains(input_nama_rumus).any():
            st.warning("Rumus dengan nama ini sudah ada.")
            st.stop()
        else:
            # Create a new row of vendor data
            new_data = pd.DataFrame(
                [
                    {
                        "Lembaga": input_lembaga,
                        "Nama Rumus": input_nama_rumus,
                        "Kriteria": input_kriteria,
                        "Banyak Data TS" : input_banyak_data_ts,
                        "Ambang Batas (%)": input_ambang_batas_persen,
                        "Ambang Batas (Jumlah)": input_ambang_batas_jumlah,
                        "Tanggal Mulai Berlaku": input_tanggal_mulai,
                        "Keterangan": input_keterangan
                    }
                ]
            )

            # Add the new vendor data to the existing data
            updated_df = pd.concat([existing_data, new_data], ignore_index=True)

            # Update Google Sheets with the new vendor data
            conn.update(worksheet="Rumus Pemantauan", data=updated_df)
            # update_worksheet("Rumus Pemantauan", updated_df)
            st.success("Rumus berhasil ditambahkan!")
            st.write(updated_df)