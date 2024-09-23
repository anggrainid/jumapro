import streamlit as st
from streamlit_option_menu import option_menu

def menu():
    # Sidebar dengan menu
    with st.sidebar:
        selected = option_menu(
            menu_title="Main Menu",  # Judul menu
            options=["Form 1", "Form 2", "About"],  # Pilihan menu
            icons=["pencil-fill", "clipboard-data", "info-circle"],  # Ikon menu
            menu_icon="cast",  # Ikon utama menu
            default_index=0,  # Opsi default
        )

    # Menampilkan input berdasarkan pilihan menu
    if selected == "Form 1":
        st.sidebar.header("Form 1")
        input_name = st.sidebar.text_input("Masukkan Nama Anda:")
        input_age = st.sidebar.number_input("Masukkan Umur Anda:", min_value=0, max_value=120)
        if st.sidebar.button("Submit"):
            st.write(f"Nama: {input_name}, Umur: {input_age}")

    elif selected == "Form 2":
        st.header("Form 2")
        input_email = st.text_input("Masukkan Email Anda:")
        input_phone = st.text_input("Masukkan Nomor Telepon:")
        if st.button("Submit"):
            st.write(f"Email: {input_email}, Nomor Telepon: {input_phone}")

    elif selected == "About":
        st.header("Tentang Aplikasi")
        st.write("Ini adalah aplikasi demo menggunakan Streamlit.")

# Memanggil fungsi menu untuk dijalankan
if __name__ == "__main__":
    menu()
