import streamlit as st


# Import calculator modules
from beks_calculator import render_beks_calculator
from p2h_calculator import render_p2h_calculator
from p2g_calculator import render_p2g_calculator
from dsr_calculator import render_dsr_calculator

# BE_URL = "http://0.0.0.0:80/"
BE_URL = "https://p2xapim.azure-api.net/P2X/"

# Set page title and description
st.set_page_config(page_title="Energy Optimization", layout="wide")
st.title("Energy Optimization Tools")

# Create a selector for the calculator type
calculator_type = st.radio("Select Calculator", ["BEKS", "P2H", "P2G", "DSR"], horizontal=True)

if calculator_type == "BEKS":
    render_beks_calculator(BE_URL)
elif calculator_type == "P2H":
    render_p2h_calculator(BE_URL)
elif calculator_type == "P2G":
    render_p2g_calculator(BE_URL)
elif calculator_type == "DSR":
    render_dsr_calculator(BE_URL)
