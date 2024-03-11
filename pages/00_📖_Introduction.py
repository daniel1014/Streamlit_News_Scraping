import streamlit as st
import pandas as pd
import general_utils
import db_connection 
# from streamlit_extras.stoggle import stoggle

# 1 / Page Config
st.set_page_config(
    page_title="Introduction",
    page_icon="📖",
    menu_items={
        'Get Help': 'https://aecom.sharepoint.com/sites/HS2-LandPropertyDigitisation-ResearchIntelligence/',
        'Report a bug': "mailto:Daniel.Wong3@aecom.com",
        'About': "# This is a *News Scraping Analytics* app!"
    },
    # initial_sidebar_state="collapsed",
    layout="wide"
)
general_utils.add_logo()

# 2.1 / Headers
st.markdown("<h1 style='text-align: center; color: black;'>Stay Informed with AI-powered News Scraping</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: black;'>Our app helps you stay up-to-date with the latest news and trends across the web.</h4>", unsafe_allow_html=True)
row = st.columns([1.2, 1, 1])
row[1].button("Get Started!", key="get_started", type="primary")
general_utils.set_primary_button_style("#008768")

# 2.2 / Header image
row_1 = st.columns([1,3])
row_1[1].image('assets/using_laptop.jpg', width=700, caption='Stay informed with the latest news and trends across the web')

# 3 / Introduction
st.subheader("📖 Key Features")
col1, col2, col3 = st.columns(3, gap="large")
with col1.container(height=150):
    st.subheader("🔍️ Intelligent News Scraping")
    st.markdown("<p style='text-align:left; color: black;'> Our app uses advanced algorithms and Google Search Engine to scrape the web for the latest news and trends.</p>", unsafe_allow_html=True)

with col2.container(height=150):
    st.subheader("📈 Advanced Analysis")
    st.markdown("<p style='text-align:left; color: black;'> Get insights and trends from the news with our AI-powered sentiment analysis and topic modelling.</p>", unsafe_allow_html=True)

with col3.container(height=150):
    st.subheader("💬 AI-powered Chatbot")
    st.markdown("<p style='text-align:left; color: black;'> Ask any question about the news with our conversational AI chatbot, powered by the latest LLM technology.</p>", unsafe_allow_html=True)

st.subheader("⚔️ Comparison with OpenAI's ChatGPT")
row_2 =st.columns([1,3,3,1], gap="small")
row_2[1].image('assets/example_chatgpt.jpg',  caption='Asking ChatGPT about the latest news of a company')
row_2[2].image('assets/example_news_scraping.jpg', caption='Asking our chatbot with the same question')
row_2_1 = row_2[1].columns([2,2.5], gap="small")
row_2_1[1].title('❌')
row_2_2 = row_2[2].columns([2,2.5], gap="small")
row_2_2[1].title('✅')


# 4 / Demo video
st.subheader("Demo Video")
video_file = open('assets/demo_chatbot.mp4', 'rb')
video_bytes = video_file.read()
with st.expander("Click to watch the demo video"):
    st.video(video_bytes)

# 5 / F&Q
st.subheader("Frequently Asked Questions")
# Engage with our cutting-edge Llama 2 Chatbot, a brainchild of Meta, now enhanced with the revolutionary RAG algorithms. This chatbot doesn't just converse - it intelligently generates discussions based on the freshest news articles scraped right off the web. Experience the transformative power of AI as it masterfully condenses intricate texts into crisp, comprehensible summaries. Dive into the future of communication with our advanced chatbot
with st.expander("F&Q 1: What is Llama 2?"):
    st.write("Llama 2 is a state-of-the-art open source large language model (LLM) released by Meta. It is a powerful conversational AI model that can generate human-like responses to text prompts. ")

with st.expander("F&Q 2: What is Mistral 7B?"):
    st.write("Mistral 7B is a improved instruct fine-tuned version of Mistral-7B-Instruct-v0.1, which outperforms Llama 2 13B on all benchmarks. It is a powerful conversational AI model that can generate human-like responses to text prompts.")

with st.expander("F&Q 3: What is RAG?"):
    st.write("RAG stands for Retrieval Augmentation Generation. It is a powerful architecture that combines information retrieval and language generation to produce high-quality responses to text prompts. The retrieval component retrieves relevant documents from a large corpus, the augmentation component augments the input prompt with information from the retrieved documents, and the generation component generates a response based on the augmented input prompt.")

with st.expander("F&Q 4: Will my data/my conversation leak to the external world by using this LLM chatbot?"):
    st.markdown("To ensure optimal performance of LLM models, it is often necessary to execute them on high-performance computing systems, either locally or through cloud-based hosting solutions. In our specific scenario, we have chosen to utilize Replicate.ai's hosting capabilities via their API, facilitating the processing of data to generate responses from the language model.") 
    st.markdown("It is worth noting that Replicate.ai, in accordance with their privacy policy, affirms that data transmitted through their API is not utilized for the enhancement of their models. During transit, data is encrypted using HTTPS, thereby mitigating the risk of interception and unauthorized access by external parties.")
    st.markdown("However, it is prudent to acknowledge that the information forwarded to the API, encompassing user inputs and model-generated responses, traverses the internet to reach Replicate's servers. Subsequently, this data may be subject to logging and temporary storage by Replicate.ai for the purpose of refining their service offerings.")
    st.markdown("For more information, please refer to Replicate.ai's privacy policy [here](https://www.replicate.ai/privacy)")

# 6/ Technical Overview
st.subheader("Technical Overview")
with st.expander('Click to view the Llama 2 Chatbot architecture diagram'):
    st.image('assets/Llama2-diagram.jpg', width=700, caption='A high-level overview of the Llama2 chatbot app')

# Login callback
def login_callback():
    db_conn = db_connection.DatabaseConnection()
    try:
        df_database = db_conn.df_from_db(f"SELECT supplier, focus, num_search FROM BMT.NewsInput WHERE username = '{username}'")
        if df_database.empty:
            st.sidebar.warning(f"Username {username} not found in the database", icon="⚠️")
        else:
            st.sidebar.success(f"Welcome, {username}!", icon="✅")
            st.session_state.df_input_database = df_database
            st.session_state.username = username
    except Exception as e:
        st.sidebar.error('Oops, something went wrong', icon="🚨")
        st.sidebar.write(f"Error: {str(e)}")
    
# Username input
with st.sidebar:
    st.subheader("🔒 Login")
    username = st.text_input("Enter Your Username")
    login_button = st.sidebar.button('Login (import your profile)', on_click=login_callback)

# Footer
general_utils.add_footer()