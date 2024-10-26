import streamlit as st

# Fungsi untuk halaman login
def login():
    st.title("Login Page")

    # Hardcode user credentials (bisa disesuaikan)
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
            # Menyimpan status login ke session state
            st.session_state['login_status'] = True
            st.rerun()  # Refresh halaman agar berubah ke dashboard
        else:
            st.error("Username atau password salah!")

# # Fungsi utama
# def main():
#     # Cek apakah user sudah login
#     if 'login_status' not in st.session_state:
#         st.session_state['login_status'] = False  # Set default jika belum ada

#     # Jika sudah login, tampilkan halaman dashboard dengan sidebar
#     if st.session_state['login_status']:
#         selected = sidebar_main()  # Panggil sidebar dan dashboard
#         if selected == "Dashboard":
#             dashboard()
#     else:
#         login()  # Jika belum login, tampilkan halaman login

# if __name__ == "__main__":
#     main()
