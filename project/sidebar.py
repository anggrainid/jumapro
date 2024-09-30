# sidebar.py
import streamlit as st
from streamlit_option_menu import option_menu
from dashboard import dashboard
from analisis_data import analisis_data
from prediksi_pemantauan.formula import formula
from prediksi_pemantauan.pemantauan_satu_prodi import pemantauan_satu_prodi
from prediksi_pemantauan.pemantauan_semua_prodi import pemantauan_semua_prodi
from prediksi_pemantauan.kalkulator_prediksi import kalkulator_prediksi
from prediksi_pemantauan.prediksi_pemantauan_satu_prodi import prediksi_pemantauan_satu_prodi
# Tambahkan impor lainnya sesuai kebutuhan

from utils.data_access import get_gsheets_connection, read_worksheet
from utils.data_processing import clean_data

# Definisikan fungsi sidebar
def sidebar():
    conn = get_gsheets_connection()
    existing_djm = read_worksheet(conn, worksheet="Data Jumlah Mahasiswa")
    existing_djm = clean_data(existing_djm, unused_columns=['Kode Prodi', 'Kode Prodi UGM', 'Kode Fakultas', 'Departemen', 'Kluster'])

    with st.sidebar:
        selected = option_menu(
            menu_title="Menu Utama",
            options=["Dashboard", "Analisis Data", "Prediksi Pemantauan", "Histori Prediksi", "Visualisasi Model", "Logout"],
            icons=["house", "bar-chart-line", "graph-up-arrow", "clock-history", "bar-chart", "box-arrow-left"],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "5!important", "background-color": "#262730"},
                "icon": {"color": "white", "font-size": "18px"},
                "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "color": "white", "--hover-color": "#4B4BFF"},
                "nav-link-selected": {"background-color": "#FF4B4B"},
                "menu-title": {"color": "white", "font-size": "18px"},
            }
        )

        if selected == "Logout":
            st.session_state['login_status'] = False
            st.experimental_rerun()  # Menggunakan rerun eksperimental

        submenu = None
        if selected == "Prediksi Pemantauan":
            submenu = option_menu(
                menu_title=None,
                options=[
                    "---",
                    "Formula Pemantauan",
                    "Pemantauan Satu Prodi",
                    "Pemantauan Semua Prodi",
                    "---",
                    "Kalkulator Prediksi",
                    "Prediksi Pemantauan Satu Prodi",
                    "Prediksi Pemantauan Semua Prodi"
                ],
                icons=["", "clipboard", "clipboard-check", "clipboard-data", "", "calculator", "clipboard-check", "clipboard-data"],
                menu_icon="cast",
                default_index=0,
                styles={
                    "container": {"padding": "5!important", "background-color": "#1F1F2E"},
                    "icon": {"color": "white", "font-size": "16px"},
                    "nav-link": {"font-size": "15px", "text-align": "left", "margin": "0px", "color": "white", "--hover-color": "#FF4B4B"},
                    "nav-link-selected": {"background-color": "#FF4B4B"},
                }
            )
        return selected, submenu

# Fungsi utama sidebar
def main():
    selected, submenu = sidebar()
    st.title(f"Halaman {selected}")

    if selected == "Dashboard":
        dashboard()
    elif selected == "Analisis Data":
        from utils.data_access import load_pickle
        existing_djm = load_pickle('data/existing_djm.pickle')
        analisis_data(existing_djm)
    elif selected == "Prediksi Pemantauan":
        if submenu == "Formula Pemantauan":
            formula()
        elif submenu == "Pemantauan Satu Prodi":
            pemantauan_satu_prodi()
        elif submenu == "Pemantauan Semua Prodi":
            pemantauan_semua_prodi()
        elif submenu == "Kalkulator Prediksi":
            kalkulator_prediksi()
        elif submenu == "Prediksi Pemantauan Satu Prodi":
            prediksi_pemantauan_satu_prodi()
        elif submenu == "Prediksi Pemantauan Semua Prodi":
            st.markdown("Prediksi Pemantauan Semua Program Studi")
    elif selected == "Histori Prediksi":
        histori_prediksi()
    elif selected == "Visualisasi Model":
        visualisasi_model()

if __name__ == "__main__":
    main()
