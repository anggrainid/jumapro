from coba_visualisasi_model import visualisasi_model
from coba_histori_prediksi import histori_prediksi
from dashboard import dashboard

def sidebar():

    import streamlit as st
    from streamlit_option_menu import option_menu

    # Membuat sidebar dengan menu pilihan menggunakan option_menu
    with st.sidebar:
        # Menu utama
        selected = option_menu(
            menu_title="Menu Utama",  # Judul menu sidebar
            options=["Dashboard", "Analisis Data", "Prediksi Pemantauan", "Histori Prediksi", "Visualisasi Model"],
            icons=["house", "bar-chart-line", "graph-up-arrow", "clock-history", "bar-chart"],  # Ikon untuk setiap menu
            menu_icon="cast",  # Ikon untuk menu sidebar
            default_index=0,  # Menu yang aktif secara default
            orientation="vertical",  # Orientasi vertikal (sidebar)
            styles={
                "container": {"padding": "5!important", "background-color": "#262730"},
                "icon": {"color": "white", "font-size": "18px"}, 
                "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "color": "white", "--hover-color": "#4B4BFF"},
                "nav-link-selected": {"background-color": "#FF4B4B"},  # Warna saat menu dipilih
                "menu-title": {"color": "white", "font-size": "18px"},  # Mengubah warna judul menu jadi putih
            }
        )

        # Submenu jika "Prediksi Pemantauan" dipilih
        if selected == "Prediksi Pemantauan":
            submenu = option_menu(
                menu_title="Submenu Pemantauan",
                options=["Formula Pemantauan", "Prediksi Pemantauan Satu Prodi", "Prediksi Pemantauan Semua Prodi"],
                icons=["clipboard", "clipboard-check", "clipboard-data"],
                menu_icon="cast",
                default_index=0,
                orientation="vertical",
                styles={
                    "container": {"padding": "5!important", "background-color": "#1F1F2E"},
                    "icon": {"color": "white", "font-size": "18px"}, 
                    "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "color": "white", "--hover-color": "#FF4B4B"},
                    "nav-link-selected": {"background-color": "#FF4B4B"},
                    "menu-title": {"color": "white", "font-size": "18px"},  # Mengubah warna judul submenu jadi putih
                }
            )

    # Konten utama berdasarkan menu yang dipilih
    st.title(f"Halaman {selected}")

    # Dashboard
    if selected == "Dashboard":
        # st.write("Ini adalah halaman Dashboard.")
        dashboard()
    # Analisis Data
    elif selected == "Analisis Data":
        st.write("Ini adalah halaman Analisis Data.")
        # Tambahkan konten analisis data di sini

    # Prediksi Pemantauan
    elif selected == "Prediksi Pemantauan":
        if submenu == "Formula Pemantauan":
            st.write("Ini adalah halaman Formula Pemantauan.")
        elif submenu == "Prediksi Satu Prodi":
            st.write("Ini adalah halaman Prediksi Satu Prodi.")
        elif submenu == "Prediksi Semua Prodi":
            st.write("Ini adalah halaman Prediksi Semua Prodi.")

    # Histori Prediksi
    elif selected == "Histori Prediksi":
        histori_prediksi()
        # st.write("Ini adalah halaman Histori Prediksi.")
        # Tambahkan konten histori prediksi di sini

    # Visualisasi Model
    elif selected == "Visualisasi Model":
        visualisasi_model()
        # st.write("Ini adalah halaman Visualisasi Model.")
        # Tambahkan konten visualisasi model di sini

sidebar()