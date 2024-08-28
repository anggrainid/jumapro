import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Display Title and Description
st.title("Halaman Manajemen Rumus Pemantauan")
st.markdown("Masukkan Rumus Baru di Bawah Ini.")

# Establishing a Google Sheets connection
conn = st.connection("gsheets", type=GSheetsConnection)

# Fetch existing vendors data
existing_data = conn.read(worksheet="Rumus Pemantauan", usecols=list(range(7)), ttl=5)
existing_data = existing_data.dropna(how="all")
st.write(existing_data)

# Dropdown options for Lembaga
lembaga_options = existing_data['Lembaga'].unique()

# List of Business Types and Products
# BUSINESS_TYPES = [
#     "Manufacturer",
#     "Distributor",
#     "Wholesaler",
#     "Retailer",
#     "Service Provider",
# ]
# PRODUCTS = [
#     "Electronics",
#     "Apparel",
#     "Groceries",
#     "Software",
#     "Other",
# ]

# Onboarding New Vendor Form
# with st.form(key="vendor_form"):
#     company_name = st.text_input(label="Company Name*")
#     business_type = st.selectbox("Business Type*", options=BUSINESS_TYPES, index=None)
#     products = st.multiselect("Products Offered", options=PRODUCTS)
#     years_in_business = st.slider("Years in Business", 0, 50, 5)
#     onboarding_date = st.date_input(label="Onboarding Date")
#     additional_info = st.text_area(label="Additional Notes")

#     # Mark mandatory fields
#     st.markdown("**required*")

#     submit_button = st.form_submit_button(label="Submit Vendor Details")

#     # If the submit button is pressed
#     if submit_button:
#         # Check if all mandatory fields are filled
#         if not company_name or not business_type:
#             st.warning("Ensure all mandatory fields are filled.")
#             st.stop()
#         elif existing_data["CompanyName"].str.contains(company_name).any():
#             st.warning("A vendor with this company name already exists.")
#             st.stop()
#         else:
#             # Create a new row of vendor data
#             vendor_data = pd.DataFrame(
#                 [
#                     {
#                         "CompanyName": company_name,
#                         "BusinessType": business_type,
#                         "Products": ", ".join(products),
#                         "YearsInBusiness": years_in_business,
#                         "OnboardingDate": onboarding_date.strftime("%Y-%m-%d"),
#                         "AdditionalInfo": additional_info,
#                     }
#                 ]
#             )

#             # Add the new vendor data to the existing data
#             updated_df = pd.concat([existing_data, vendor_data], ignore_index=True)

#             # Update Google Sheets with the new vendor data
#             conn.update(worksheet="Vendors", data=updated_df)

#             st.success("Vendor details successfully submitted!")

with st.form(key="formula_form"):
    input_lembaga = st.selectbox("Pilih Lembaga : ", lembaga_options)
    input_nama_rumus = st.text_input("Masukkan Nama Rumus (ex: PEMPT) :")
    input_kriteria = st.radio("Kriteria", ["Persentase Penurunan", "Jumlah Minimal"])


    if input_kriteria == "Persentase Penurunan":
        input_ambang_batas_persen = st.number_input("Ambang Batas Persentase Maksimal (%)", min_value=0.0, max_value=100.0, step=0.1)
        input_ambang_batas_jumlah = None
    else:
        input_ambang_batas_jumlah = st.number_input("Ambang Batas Jumlah Mahasiswa Minimal", min_value=1, step=1)
        input_ambang_batas_persen = None

    input_tanggal_mulai = st.date_input("Tanggal Mulai Berlaku")
    input_keterangan = st.text_area("Keterangan")

    # Mark mandatory fields
    st.markdown("**required*")

    submit_button = st.form_submit_button(label="Submit New Formula")

    # If the submit button is pressed
    if submit_button:
        # Check if all mandatory fields are filled
        if not input_lembaga or not input_nama_rumus:
            st.warning("Ensure all mandatory fields are filled.")
            st.stop()
        elif existing_data["Nama Rumus"].str.contains(input_nama_rumus).any():
            st.warning("Rumus dengan nama ini sudah ada.")
            st.stop()
        else:
            # Create a new row of vendor data
            new_data = pd.DataFrame(
                [
                    {
                        "Lembaga": [input_lembaga],
                        "Nama Rumus": [input_nama_rumus],
                        "Kriteria": [input_kriteria],
                        "Ambang Batas (%)": [input_ambang_batas_persen],
                        "Ambang Batas (Jumlah)": [input_ambang_batas_jumlah],
                        "Tanggal Mulai Berlaku": [input_tanggal_mulai],
                        "Keterangan": [input_keterangan]
                    }
                ]
            )

            # Add the new vendor data to the existing data
            updated_df = pd.concat([existing_data, new_data], ignore_index=True)

            # Update Google Sheets with the new vendor data
            conn.update(worksheet="Rumus Pemantauan", data=updated_df)

            st.success("Rumus berhasil ditambahkan!")
            st.write(updated_df)