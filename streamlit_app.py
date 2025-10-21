import streamlit as st

# Configuration for local development
LOCAL_MODE = False  # Set to False for production/Azure deployment
P2X_APIM_SECRET = "test"  # APIM secret for local backend authentication


# Import calculator modules
from beks_calculator import render_beks_calculator
from p2h_calculator import render_p2h_calculator
from p2g_calculator import render_p2g_calculator
from dsr_calculator import render_dsr_calculator

# Automatically set BE_URL based on LOCAL_MODE
BE_URL = "http://0.0.0.0:80/" if LOCAL_MODE else "https://p2xapim.azure-api.net/P2X/"

# Set page title and description
st.set_page_config(page_title="Energy Optimization", layout="wide")
st.title("Energy Optimization Tools")

# Create a selector for the calculator type
calculator_type = st.radio("Select Calculator", ["BEKS", "P2H", "P2G", "DSR"], horizontal=True)

if calculator_type == "BEKS":
    render_beks_calculator(BE_URL, LOCAL_MODE, P2X_APIM_SECRET)
elif calculator_type == "P2H":
    render_p2h_calculator(BE_URL, LOCAL_MODE, P2X_APIM_SECRET)
elif calculator_type == "P2G":
    render_p2g_calculator(BE_URL, LOCAL_MODE, P2X_APIM_SECRET)
elif calculator_type == "DSR":
    render_dsr_calculator(BE_URL, LOCAL_MODE, P2X_APIM_SECRET)
