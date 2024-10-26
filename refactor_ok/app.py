# app.py
import streamlit as st
from pages_jumapro.dashboard import dashboard
# from analisis_data_satu_prodi import analisis_data
# from coba_visualisasi_model import visualisasi_model
# from coba_histori_prediksi import histori_prediksi
# from form_formulas_new import formula
# from form_prediksi_origin_only import kalkulator_prediksi
# from form_prediksi_satu_prodi_fix_formula import prediksi_pemantauan_satu_prodi
# from refactor_form_pemantauan_satu_prodi_fix_formula_tanpa_prediksi import pemantauan_satu_prodi
# from refactor_form_pemantauan_semua_prodi import pemantauan_semua_prodi
# from form_prediksi_semua_last_func import prediksi_pemantauan_semua_prodi
from component.sidebar import sidebar_main
from pages_jumapro.login import login
from pages_jumapro.eda import analisis_data
from pages_jumapro.history import histori_prediksi
from pages_jumapro.visualization import visualisasi_model
from pages_jumapro.monitoring.formula import formula
from pages_jumapro.prediction.calculator import kalkulator_prediksi


# Fungsi utama
def main():
    # Cek apakah user sudah login
    if 'login_status' not in st.session_state:
        st.session_state['login_status'] = False  # Set default jika belum ada

    # Jika sudah login, tampilkan halaman dengan sidebar
    if st.session_state['login_status']:
        selected, submenu = sidebar_main()  # Panggil sidebar dan ambil pilihan menu

        st.title(f"Halaman {selected}")

        if selected == "Dashboard":
            dashboard()
        elif selected == "Analisis Data":
            analisis_data()
        elif selected == "Prediksi Pemantauan":
            if submenu == "Formula Pemantauan":
                formula()
        #     elif submenu == "Pemantauan Satu Prodi":
        #         pemantauan_satu_prodi()
        #     elif submenu == "Pemantauan Semua Prodi":
        #         pemantauan_semua_prodi()
            elif submenu == "Kalkulator Prediksi":
                kalkulator_prediksi()
        #     elif submenu == "Prediksi Pemantauan Satu Prodi":
        #         prediksi_pemantauan_satu_prodi()
        #     elif submenu == "Prediksi Pemantauan Semua Prodi":
        #         prediksi_pemantauan_semua_prodi()
        elif selected == "Histori Prediksi":
            histori_prediksi()
        elif selected == "Visualisasi Model":
            visualisasi_model()
    else:
        login()  # Jika belum login, tampilkan halaman login

if __name__ == "__main__":
    main()
