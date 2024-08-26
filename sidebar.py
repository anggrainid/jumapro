import streamlit as st

st.title('My Multipage App')

# Create a sidebar with selectbox to choose page
page = st.sidebar.selectbox(
    "Pilih Halaman",
    ["Home", "Data", "About"]
)

# Display the selected page
if page == "Home":
    st.write("Ini adalah halaman home")
elif page == "Data":
    st.write("Ini adalah halaman data")
else:
    st.write("Ini adalah halaman about")