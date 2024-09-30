# data/gsheets.py
import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

def get_gsheets_connection():
    return st.connection("gsheets", type=GSheetsConnection)

def read_worksheet(worksheet, usecols=None, ttl=5):
    conn = get_gsheets_connection()
    return conn.read(worksheet=worksheet, usecols=usecols, ttl=ttl)

def update_worksheet(worksheet, data):
    conn = get_gsheets_connection()
    conn.update(worksheet=worksheet, data=data)
