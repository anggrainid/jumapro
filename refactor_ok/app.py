import streamlit as st
from component.sidebar import sidebar_main
from component.data import refresh_data, get_data, preprocess_data
from pages_jumapro.login import login
from pages_jumapro.dashboard import dashboard
from pages_jumapro.eda import analisis_data
from pages_jumapro.history import histori_prediksi
from pages_jumapro.visualization import visualisasi_model
from pages_jumapro.monitoring.formula import formula
from pages_jumapro.prediction.calculator import kalkulator_prediksi
from pages_jumapro.prediction.one_prediction import prediksi_pemantauan_satu_prodi
from pages_jumapro.prediction.all import prediksi_pemantauan_semua_prodi
from pages_jumapro.monitoring.one_monitoring import pemantauan_satu_prodi
from pages_jumapro.monitoring.all import pemantauan_semua_prodi

# Inisialisasi data di session state
# def initialize_data():
#     if 'existing_djm' not in st.session_state:
#         st.session_state['existing_djm'] = preprocess_data(get_data('djm'))

#     if 'existing_formula' not in st.session_state:
#         st.session_state['existing_formula'] = preprocess_data(get_data('formula'))

# Fungsi untuk refresh data di sidebar
# def refresh_all_data():
#     st.session_state['existing_djm'] = preprocess_data(refresh_data('djm'))
#     st.session_state['existing_formula'] = preprocess_data(refresh_data('formula'))
#     st.success("Data berhasil dimuat ulang dari Google Sheets!")

# Fungsi utama
def main():
    # Cek apakah user sudah login
    if 'login_status' not in st.session_state:
        st.session_state['login_status'] = False  # Set default jika belum ada
    
    # Jika sudah login, tampilkan halaman dengan sidebar
    if st.session_state['login_status']:
        selected, submenu = sidebar_main()  # Panggil sidebar dan ambil pilihan menu

        # Inisialisasi data saat pertama kali aplikasi dibuka
        # if 'initialized' not in st.session_state:
        #     initialize_data()
        #     st.session_state['initialized'] = True  # Tandai bahwa inisialisasi telah dilakukan

        # Pastikan data ada
        existing_djm = preprocess_data(get_data('djm'))
        existing_formula = preprocess_data(get_data('formula'))
        if st.sidebar.button("Refresh Data"):
            existing_djm = preprocess_data(refresh_data('djm'))
            existing_formula = preprocess_data(refresh_data('formula'))

        st.title(f"Halaman {selected}")


        if selected == "Dashboard":
            dashboard(existing_djm)
        elif selected == "Analisis Data":
            analisis_data(existing_djm)
        elif selected == "Prediksi Pemantauan":
            if submenu == "Formula Pemantauan":
                formula(existing_djm, existing_formula)
            elif submenu == "Pemantauan Satu Prodi":
                pemantauan_satu_prodi(existing_formula)
            elif submenu == "Pemantauan Semua Prodi":
                pemantauan_semua_prodi(existing_djm, existing_formula)
            elif submenu == "Kalkulator Prediksi":
                kalkulator_prediksi()
            elif submenu == "Prediksi Pemantauan Satu Prodi":
                prediksi_pemantauan_satu_prodi(existing_formula)
            elif submenu == "Prediksi Pemantauan Semua Prodi":
                prediksi_pemantauan_semua_prodi(existing_djm, existing_formula)
        elif selected == "Histori Prediksi":
            histori_prediksi(existing_djm)
        elif selected == "Visualisasi Model":
            visualisasi_model(existing_djm)
    else:
        login()  # Jika belum login, tampilkan halaman login

if __name__ == "__main__":
    main()
