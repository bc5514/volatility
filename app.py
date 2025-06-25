import streamlit as st
import surface
import smile

# Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "Volatility Surface"

# Sidebar "tab" buttons
st.sidebar.title("Navigation")
if st.sidebar.button("Volatility Surface"):
    st.session_state.page = "Volatility Surface"

if st.sidebar.button("Volatility Smile"):
    st.session_state.page = "Volatility Smile"

# Display current page
if st.session_state.page == "Volatility Surface":
    surface.run()
elif st.session_state.page == "Volatility Smile":
    smile.run()