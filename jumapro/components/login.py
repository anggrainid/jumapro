# components/login.py
import streamlit as st
from components.sidebar import main as sidebar_main

def login():
    st.title("Login Page")

    # Kredensial pengguna (dapat disesuaikan atau dipindahkan ke file konfigurasi)
    valid_username = "admin"
    valid_password = "password123"

    # Form login
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_button = st.button("Login")

    # Validasi login
    if login_button:
        if username == valid_username and password == valid_password:
            st.success("Login berhasil!")
            st.session_state['login_status'] = True
            st.experimental_rerun()  # Refresh halaman agar berubah ke dashboard
        else:
            st.error("Username atau password salah!")

def main():
    # Inisialisasi status login
    if 'login_status' not in st.session_state:
        st.session_state['login_status'] = False

    # Tampilkan halaman dashboard atau login berdasarkan status
    if st.session_state['login_status']:
        sidebar_main()  # Menampilkan sidebar dan konten utama
    else:
        login()

if __name__ == "__main__":
    main()
