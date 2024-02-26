import streamlit as st
import pandas as pd
import general_utils

st.set_page_config(
    page_title="Home Page",
    page_icon="🏠",
    menu_items={
        'Get Help': 'https://aecom.sharepoint.com/sites/HS2-LandPropertyDigitisation-ResearchIntelligence/',
        'Report a bug': "mailto:Daniel.Wong3@aecom.com",
        'About': "# This is a *News Scraping Analytics* app!"
    },
    # layout="wide"
)


general_utils.add_logo()


st.title("News Scraping Analytics Enhanced by :rainbow[Llama 2 & Mistral] chatbot" + "  🦙💬  ")

## Demo video
video_file = open('assets/demo_chatbot.mp4', 'rb')
video_bytes = video_file.read()

st.video(video_bytes)

## Introduction
col1, col2 = st.columns(2)
with col1.container(height=310):
    st.subheader("🦙💬 Llama 2 Chatbot")
    st.markdown("Engage with our cutting-edge Llama 2 Chatbot, a brainchild of Meta, now enhanced with the revolutionary RAG algorithms. This chatbot doesn't just converse - it intelligently generates discussions based on the freshest news articles scraped right off the web. Experience the transformative power of AI as it masterfully condenses intricate texts into crisp, comprehensible summaries. Dive into the future of communication with our advanced chatbot.")
    st.markdown("*Discover how Llama 2 beat OpenAI's ChatGPT [here](https://textcortex.com/post/llama-2-vs-chatgpt)*")
    st.markdown("*Learn more about how Mistral 7B outperformed OpenAI's ChatGPT [here](https://mistral.ai/news/announcing-mistral-7b/)*")
    st.markdown("*Explore the advantages of Context Augmentation and RAG techniques in enriching our LLM models. Learn more [here](https://docs.llamaindex.ai/en/stable/index.html)*")


with col2.container(height=150):
    st.subheader("🔍️ Customized Searching")
    st.markdown("Utilize the search engine API to retrieve latest news from Google. Intelligently parse and scrape the news article from each website, logged your historic input, and store the data in the database.")

with col2.container(height=150):
    st.subheader("📈 Advanced Analysis")
    st.markdown("Perform sentiment analysis and topic modelling based on the scrapped news article and visualize the result in an intuitive bar chart or an interactive dashboard.")

st.image('assets/Llama2-diagram.jpg', width=700, caption='A high-level overview of the Llama2 chatbot app')


# Username input
username = st.sidebar.text_input("Enter Your Username")

# Login callback
def login_callback():
    st.write(f"Welcome, {username}!")
    st.session_state.username = username

# Login button
login_button = st.sidebar.button('Login (import your profile)', on_click=login_callback)

