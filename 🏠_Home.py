import streamlit as st
import pandas as pd
import general_utils
import db_connection 

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