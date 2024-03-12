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
if row[1].button("Get Started!", key="get_started", type="primary"):
    st.switch_page("🔍️Search.py")
general_utils.set_primary_button_style("#008768")

# 2.2 / Header image
row_1 = st.columns([1,4])
row_1[1].image('assets/using_laptop.jpg', width=700, caption='Stay informed with the latest news and trends across the web')

# 3 / Introduction
st.subheader("Key Features")
col1, col2, col3 = st.columns(3, gap="large")
with col1.container(height=165):
    st.markdown("<h4 style='text-align:left; color: black;'>🔍️ Intelligent News Scraping</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:left; color: black;'> Our app uses advanced algorithms and customized Google Search Engine to scrape the web for the latest news and trends.</p>", unsafe_allow_html=True)

with col2.container(height=165):
    st.markdown("<h4 style='text-align:left; color: black;'>📈 Advanced Analysis</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:left; color: black;'> Get insights and trends from the news with our AI-powered sentiment analysis and topic modelling visualization.</p>", unsafe_allow_html=True)

with col3.container(height=165):
    st.markdown("<h4 style='text-align:left; color: black;'>💬 AI-powered Chatbot</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:left; color: black;'> Ask any question about the news with our conversational AI chatbot, powered by the latest LLM technology.</p>", unsafe_allow_html=True)

st.subheader("Comparison with OpenAI's ChatGPT")
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
with st.expander("F&Q 1: Why should I use this app rather than Google search?"):
    # st.markdown("<h5 style='text-align:left; color: black;'>This app offers several advantages over a traditional Google search:</h3>", unsafe_allow_html=True)
    st.markdown('This app offers several advantages over a traditional Google search:')         
    st.markdown('1. **Simultaneous Multiple Searches**: Instead of manually entering each query in Google, this app allows you to perform multiple searches simultaneously. This saves time and effort, especially when dealing with a large number of queries.')           
    st.markdown('2. **AI-Powered Summaries**: The app uses AI to browse websites and generate summaries of the content. This feature provides a quick overview of the content without having to read the entire article.')
    st.markdown('3. **Sentiment Analysis**: The app can recognize the sentiment of the articles. It uses intuitive design elements like smiley faces and sad faces to represent positive and negative sentiments, making it easy to understand the overall tone of the content.')
    st.markdown('By integrating these features into a single app, it provides a more efficient and streamlined experience for users, making it a powerful tool for anyone who needs to perform extensive online research.')

with st.expander("F&Q 2: How does this chatbot outperform other AI tools? (e.g. ChatGPT 3.5)?"):
    st.markdown("Our chatbot offers significant advantages over other AI tools like ChatGPT 3.5, particularly due to the integration of the RAG (Retrieval-Augmented Generation) technique:")
    st.markdown("1. **Utilization of Latest Information**: Our chatbot can utilize the latest information scraped from the internet or local documents. This ensures that the chatbot's responses are always up-to-date and relevant.")
    st.markdown("2. **Improved Contextual Understanding**: The RAG technique allows our chatbot to generate more accurate and contextually relevant responses. It retrieves relevant documents or text passages based on the latest information and uses them to generate responses.")
    st.markdown('3. **Answering Beyond Static Dataset**: Unlike traditional models that generate responses based on a fixed dataset, our chatbot can answer questions based on the information we provide. This allows it to answer questions beyond the scope of a static dataset.')

with st.expander("F&Q 3: What are the Large Language Models (LLM) being used in the chatbot?"):
    st.markdown("The chatbot utilizes two Large Language Models (LLMs): Llama 2 and Mistral 7B.")
    st.markdown("**• Llama 2**: This is a state-of-the-art open-source LLM released by Meta. Known for its creativity, Llama 2 can generate human-like responses to text prompts, making it ideal for generating diverse and innovative responses.")
    st.markdown("**• Mistral 7B**: This is an improved, fine-tuned version of Mistral-7B-Instruct-v0.1. It outperforms Llama 2 13B on all benchmarks. Known for its precision, Mistral 7B can generate highly accurate and contextually relevant responses to text prompts.")
    st.markdown("In summary, while both models are powerful and capable of generating human-like responses, Llama 2 is more suited for tasks requiring creative output, whereas Mistral 7B excels in tasks requiring precision and accuracy.")

with st.expander("F&Q 4: Will my data/my conversation leak to the external world by using this LLM chatbot?"):
    st.markdown("To ensure optimal performance of LLM models, it is often necessary to execute them on high-performance computing systems, either locally or through cloud-based hosting solutions. In our specific scenario, we have chosen to utilize **Replicate.ai's** hosting capabilities via their API, facilitating the processing of data to generate responses from the language model.") 
    st.markdown("It is worth noting that Replicate.ai, in accordance with their privacy policy, affirms that data transmitted through their API is not utilized for the enhancement of their models. During transit, data is encrypted using HTTPS, thereby mitigating the risk of interception and unauthorized access by external parties.")
    st.markdown("However, it is prudent to acknowledge that the information forwarded to the API, encompassing user inputs and model-generated responses, traverses the internet to reach Replicate's servers. Subsequently, this data may be subject to logging and temporary storage by Replicate.ai for the purpose of refining their service offerings.")
    st.markdown("For more information, please refer to Replicate.ai's privacy policy [here](https://www.replicate.ai/privacy)")

with st.expander("F&Q 5: Why the RAG technique matters to the chatbot?"):
    st.markdown("RAG (Retrieval Augmentation Generation) is the ***Secret Recipe*** in our chatbot that allows it to stay updated with the latest information. The RAG technique is a powerful architecture that combines information retrieval and language generation to produce high-quality responses to text prompts.")
    st.markdown("The retrieval component retrieves relevant documents from a large corpus, such as the latest news articles scraped from the internet or local documents. The augmentation component then augments the input prompt with information from the retrieved documents. Finally, the generation component generates a response based on the augmented input prompt.")
    st.markdown("This technique allows our chatbot to answer questions based on the most recent information we provide, rather than relying solely on a static dataset. This dynamic learning capability makes our chatbot more versatile and effective, enabling it to provide more accurate, up-to-date, and contextually relevant responses.")

with st.expander("F&Q 6: Is there any limitation of using this app?"):
    st.markdown("Yes, there are some limitations to using this app:")
    st.markdown("1. **API Rate Limit**: The app uses the Google Custom Search JSON API to scrape the web for news articles. This API has a daily limit of 100-200 queries per day. Once this limit is reached, the app will be unable to perform any further searches until the next day. Additional requests please contact the developer *(you can get more info to contact us through the build-in menu at top right corner)*.")
    st.markdown("2. **Cloud Provider Pricing**: The chatbot uses the Replicate.ai API to generate responses to user queries. Though we're purely using open-source langugage models like Llama 2 & Mistral, we still need to host them on high-performance computing systems which actuall require cost, priced by the length of questions (as input) and response generated (as output). To know more about the specific pricing, please contact the developer *(you can get more info to contact us through the build-in menu at top right corner)*.")
    st.markdown("3. **Scability and Performance**: The app is presently hosted on a free-tier cloud server, implying that its performance could be influenced by both the concurrent user load and the volume of information being fed into the language model. If the app experiences a high volume of traffic, it may slow down or become unresponsive. This is particularly true for the chatbot, which requires significant computational resources to generate responses.")

# 6/ Technical Overview
st.subheader("Technical Overview")
with st.expander('Click to view the Llama 2 Chatbot architecture diagram'):
    st.image('assets/Llama2-diagram.jpg', width=700, caption='A high-level overview of the Llama2 chatbot app')
with st.expander("Explore more about the latest LLM technology"):
    st.markdown("*Discover how Llama 2 beat OpenAI's ChatGPT [here](https://textcortex.com/post/llama-2-vs-chatgpt)*")
    st.markdown("*Learn more about how Mistral 7B outperformed OpenAI's ChatGPT [here](https://mistral.ai/news/announcing-mistral-7b/)*")
    st.markdown("*Explore the advantages of Context Augmentation and RAG techniques in enriching our LLM models. Learn more [here](https://docs.llamaindex.ai/en/stable/index.html)*")

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