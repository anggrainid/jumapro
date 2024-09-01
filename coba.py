import streamlit as st
from streamlit_gsheets import GSheetsConnection

url = "https://docs.google.com/spreadsheets/d/19t1jUkRoxmU3Ir6cQO6I5394llMoKVZYqfDRrmqNFNI/edit?usp=sharing"

conn = st.connection("gsheets", type=GSheetsConnection)

data = conn.read(spreadsheet=url, usecols=[0, 1])
st.dataframe(data)