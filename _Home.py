import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Home Page",
    page_icon="🏠",
    menu_items={
        'Get Help': 'https://aecom.sharepoint.com/sites/HS2-LandPropertyDigitisation-ResearchIntelligence/',
        'Report a bug': "mailto:Daniel.Wong3@aecom.com",
        'About': "# This is a *News Scraping Analytics* app!"
    },
    layout="wide"
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


st.title("News Scraping Analytics Enhanced by :rainbow[Llama 2 & Mistral] chatbot" + "  🦙💬  ")

## Demo video
video_file = open('assets/demo_chatbot.mp4', 'rb')
video_bytes = video_file.read()

st.video(video_bytes)

## Introduction
col1, col2 = st.columns(2)
with col1.container(height=310):
    st.subheader("Llama 2 Chatbot")
    st.markdown("Chat with the Llama 2 Chatbot (invented by Meta) and the state-of-the-art RAG algorithms to generate a conversation based on the latest news article that we just scraped. Harness the power of AI to distill complex texts into concise, easily digestible summaries.")
    st.caption("Explore more about how did Llama 2 (& Mistral) outperform OpenAI's ChatGPT: [here](https://textcortex.com/post/llama-2-vs-chatgpt)")
    st.caption("And how can the context augmentation/RAG techniques benefit to this LLM system: [here](https://docs.llamaindex.ai/en/stable/index.html)")

with col2.container(height=150):
    st.subheader("Customized Searching")
    st.markdown("Utilize the search engine API to retrieve latest news from Google. Intelligently parse and scrape the news article from each website, logged your historic input, and store the data in the database.")

with col2.container(height=150):
    st.subheader("Advanced Analysis")
    st.markdown("Perform sentiment analysis and topic modelling based on the scrapped news article and visualize the result in an intuitive bar chart or an interactive dashboard.")

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

