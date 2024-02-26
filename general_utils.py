import streamlit as st

def add_logo():
    st.markdown(
        """
        <style>
            [data-testid="stSidebarNav"] {
                background-image: url(https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/AECOM_logo.svg/2560px-AECOM_logo.svg.png);
                background-repeat: no-repeat;
                padding-top: 15px;
                background-position: 20px 20px;
                background-size: 200px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )