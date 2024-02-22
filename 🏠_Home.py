import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Home Page",
    page_icon=":shark:",
    menu_items={
        'Get Help': 'https://aecom.sharepoint.com/sites/HS2-LandPropertyDigitisation-ResearchIntelligence/',
        'Report a bug': "mailto:Daniel.Wong3@aecom.com",
        'About': "# This is a *News Scraping Analytics* app!"
    }
)

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
add_logo()


st.write("# Welcome!")
# Instructions

if st.checkbox('Show instructions'):
    st.markdown('''
* This tool is used to scrape news from Google Search Engine. Please **Login** with your username to load your historic input data (a new username will be registered if it is not exisiting in database). 
* Please enter your desired input query(s) including supplier, focus (eg. Enercon Supply Chain), and number of search. 
* When you're ready, click **'Search'** and an output table will be generated along with the tabs corresponding to your choice of input above. 
* Next, click **'Sentiment Analysis'** and views the related results from the bar chart. 
* If you want to save the current input(s) into the database, click **"Uploaded Input to AECOM database"** so you can download your data with your unique username when you are back next time. Furthermore, both the news output and sentiment analysis results can be downloaded as Excel or CSV file. 
''')


# Username input
username = st.sidebar.text_input("Enter Your Username")

# Login callback
def login_callback():
    st.write(f"Welcome, {username}!")
    st.session_state.username = username

# Login button
login_button = st.sidebar.button('Login (import your profile)', on_click=login_callback)

