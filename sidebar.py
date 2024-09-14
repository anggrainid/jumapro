# multihalaman streamlit

import streamlit as st
import form_prediksi_satu_prodi_fix_formula

st.title('My Multipage App')

# Create a sidebar with selectbox to choose page
page = st.sidebar.selectbox(
    "Pilih Halaman",
    ["Home", "Data", "About"]
)

prediksi_satu_prodi = "(form_prediksi_satu_prodi_fix_formula.py)"
# Display the selected page
if page == "Home":
    form_prediksi_satu_prodi_fix_formula.load_form_prediksi()
elif page == "Data":
    form_prediksi_satu_prodi_fix_formula.load_form_prediksi()
else:
    form_prediksi_satu_prodi_fix_formula.load_form_prediksi()


