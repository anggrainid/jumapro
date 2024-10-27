# Establishing a Google Sheets connection
# conn = GSheetsConnection()  # Pastikan ini sesuai dengan cara Anda menginisialisasi koneksi
# existing_djm = conn.read(worksheet="Data Jumlah Mahasiswa", ttl=5)
# existing_djm = existing_djm.dropna(how="all")
# existing_djm = existing_djm.replace('#N/A ()', 0)

# unused_column = ['Kode Prodi', 'Kode Prodi UGM', 'Kode Fakultas', 'Departemen', 'Kluster']
# existing_djm = existing_djm.drop(unused_column, axis=1)

# Fungsi untuk membuat sidebar dan navigasi



# sidebar.py
import streamlit as st
from streamlit_option_menu import option_menu

def sidebar_main():
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
                default_index=1,
                styles={
                    "container": {"padding": "5!important", "background-color": "#1F1F2E"},
                    "icon": {"color": "white", "font-size": "16px"},
                    "nav-link": {"font-size": "15px", "text-align": "left", "margin": "0px", "color": "white", "--hover-color": "#FF4B4B"},
                    "nav-link-selected": {"background-color": "#FF4B4B"},
                }
            )
    return selected, submenu
