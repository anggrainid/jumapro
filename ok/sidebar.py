import streamlit as st
# from dashboard import dashboard
from streamlit_option_menu import option_menu
from dashboard import dashboard
from coba_visualisasi_model import visualisasi_model
from coba_histori_prediksi import histori_prediksi
from form_formulas_new import formula
from form_prediksi_origin_only import kalkulator_prediksi
from form_prediksi_satu_prodi_fix_formula import prediksi_pemantauan_satu_prodi
from refactor_form_pemantauan_satu_prodi_fix_formula_tanpa_prediksi import pemantauan_satu_prodi
from refactor_form_pemantauan_semua_prodi import pemantauan_semua_prodi
from analisis_data_satu_prodi import analisis_data
from streamlit_gsheets import GSheetsConnection

# Establishing a Google Sheets connection
conn = st.connection("gsheets", type=GSheetsConnection)

existing_djm = conn.read(worksheet="Data Jumlah Mahasiswa", ttl=5)
existing_djm = existing_djm.dropna(how="all")
existing_djm = existing_djm.replace('#N/A ()', 0)

unused_column = ['Kode Prodi', 'Kode Prodi UGM', 'Kode Fakultas', 'Departemen', 'Kluster']
existing_djm = existing_djm.drop(unused_column, axis=1)

# Fungsi untuk membuat sidebar dan navigasi
def sidebar():
    # Sidebar Utama
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
            st.rerun()  # Paksa refresh halaman setelah logout

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

# Fungsi utama yang memanggil dashboard dan navigasi sidebar
def main():
    selected, submenu = sidebar()

    st.title(f"Halaman {selected}")

    if selected == "Dashboard":
        dashboard()
    elif selected == "Analisis Data":
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
