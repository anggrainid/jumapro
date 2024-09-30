# utils/data_access.py
import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pickle
import os

@st.cache_data
def get_gsheets_connection():
    return st.connection("gsheets", type=GSheetsConnection)

@st.cache_data
def read_worksheet(conn, worksheet, usecols=None, ttl=5):
    return conn.read(worksheet=worksheet, usecols=usecols, ttl=ttl)

@st.cache_data
def load_pickle(filepath):
    if not os.path.exists(filepath):
        return None
    with open(filepath, 'rb') as handle:
        return pickle.load(handle)

@st.cache_resource
def load_model_cached(model_path):
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at {model_path}")
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    return model
