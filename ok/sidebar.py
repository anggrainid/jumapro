import streamlit as st
from streamlit_option_menu import option_menu

def sidebar():
    # Sidebar Utama
    with st.sidebar:
        selected = option_menu(
            menu_title="Menu Utama",
            options=["Dashboard", "Analisis Data", "Prediksi Pemantauan", "Histori Prediksi", "Visualisasi Model"],
            icons=["house", "bar-chart-line", "graph-up-arrow", "clock-history", "bar-chart"],
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

        submenu = None
        # Jika 'Prediksi Pemantauan' dipilih, tampilkan gabungan submenunya dengan pemisah visual
        if selected == "Prediksi Pemantauan":

            submenu = option_menu(
                menu_title=None,
                
                options=[
                    "---",
                    "Formula Pemantauan", 
                    "Pemantauan Satu Prodi",
                    "Pemantauan Semua Prodi",
                    "---",  # Pemisah visual
                    "Kalkulator Prediksi", 
                    "Prediksi Pemantauan Satu Prodi", 
                    "Prediksi Pemantauan Semua Prodi"
                ],
                icons=[
                    "clipboard", "clipboard-check", "clipboard-data", 
                    "",  # Tidak ada ikon untuk pemisah
                    "calculator", "clipboard-check", "clipboard-data"
                ],
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

def main():
    selected, submenu = sidebar()

    # Menampilkan halaman utama
    st.title(f"Halaman {selected}")

    # Prediksi Pemantauan
    if selected == "Prediksi Pemantauan":
        st.write(f"Halaman untuk {submenu}")
        if submenu == "Formula Pemantauan":
            st.write("Ini adalah halaman Formula Pemantauan.")
        elif submenu == "Pemantauan Satu Prodi":
            st.write("Ini adalah halaman Pemantauan Satu Prodi.")
        elif submenu == "Pemantauan Semua Prodi":
            st.write("Ini adalah halaman Pemantauan Semua Prodi.")
        elif submenu == "Kalkulator Prediksi":
            st.write("Ini adalah halaman Kalkulator Prediksi.")
        elif submenu == "Prediksi Pemantauan Satu Prodi":
            st.write("Ini adalah halaman Prediksi Pemantauan Satu Prodi.")
        elif submenu == "Prediksi Pemantauan Semua Prodi":
            st.write("Ini adalah halaman Prediksi Pemantauan Semua Prodi.")

    elif selected == "Dashboard":
        st.header("Dashboard")
        st.write("Konten untuk Dashboard.")

    elif selected == "Analisis Data":
        st.header("Analisis Data")
        st.write("Konten untuk Analisis Data.")

    elif selected == "Histori Prediksi":
        st.header("Histori Prediksi")
        st.write("Konten untuk Histori Prediksi.")

    elif selected == "Visualisasi Model":
        st.header("Visualisasi Model")
        st.write("Konten untuk Visualisasi Model.")

if __name__ == "__main__":
    main()
