import streamlit as st
from dotenv import dotenv_values
import os
from llama_index.core import VectorStoreIndex, Document, Settings
from llama_index.llms.replicate import Replicate
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
# from llama_index.core.llms.llama_utils import messages_to_prompt, completion_to_prompt
import general_utils

# App title
st.set_page_config(
    page_title="News Scraping",
    page_icon="assets/page_icon.png",
    # layout='wide', 
    menu_items={
    'Get Help': 'https://aecom.sharepoint.com/sites/HS2-LandPropertyDigitisation-ResearchIntelligence/',
    'Report a bug': "mailto:Daniel.Wong3@aecom.com",
    'About': "# This is a *News Scraping Analytics* app!"
    },
)

config = dotenv_values(".env")

general_utils.add_logo()

if "all_results" not in st.session_state or st.session_state.all_results == None:
    st.warning("Please perform a search first.")
    st.stop()  

# Initialize the LLM model
def initialize_llm(model, max_new_tokens):
    """
    Initialize the LLM model
    """
    llm = Replicate(
        model=model,
        temperature=0.5,        # Experimenting - higher temperature turns into faster response, but less details in the response 
        # Experimenting - control the spec of Replicate API. 
        # max_new_tokens is set to customizable to extend the generated response. Repetition penalty is set to 1 to disable repetitive responses. 
        # system prompt seems not working in both models   
        additional_kwargs = {"max_new_tokens": max_new_tokens, "repetition_penalty":1, 
                             "system_prompt": "You are a helpful, respectful and honest assistant. Please always use multiple sources to answer question if they are relevant. Also, please provide your answer along with reference and date."
                             },
        # override max tokens since it's interpreted as context window instead of max tokens
        # context_window=context_window, 
        # messages_to_prompt=messages_to_prompt,
    )
    Settings.llm = llm
    Settings.embed_model = HuggingFaceEmbedding(
        model_name="BAAI/bge-small-en-v1.5")
    # Settings.chunk_size = 1024
    return llm

## The script below is refactored from https://blog.streamlit.io/how-to-build-a-llama-2-chatbot/#3-build-the-app
# Replicate Credentials
with st.sidebar:
    st.title('🤖 AI-powered Chatbot')
    if 'REPLICATE_API_TOKEN' in config:
        # st.success('API key already provided!', icon='✅')
        replicate_api = config['REPLICATE_API_TOKEN']
        os.environ["REPLICATE_API_TOKEN"] = replicate_api
    elif 'REPLICATE_API_TOKEN' in st.secrets:
        st.success('API key already provided!', icon='✅')
        replicate_api = st.secrets['REPLICATE_API_TOKEN']
        os.environ["REPLICATE_API_TOKEN"] = replicate_api
    else:
        replicate_api = st.text_input('Enter Replicate API token:', type='password')
        if not (replicate_api.startswith('r8_') and len(replicate_api)==40):
            st.warning('Please enter your credentials!', icon='⚠️')
        else:
            st.success('Proceed to entering your prompt message!', icon='👉')
    tab1, tab2 = st.tabs(["Basic", "Advanced"])
    # activate = st.toggle("Activate: Feed Data into LLM",
    #         help="""Activate this feature to load the documents from scrapped articles into the LLM model, 
    #         empowered by Retrieval Augmentation Generation (RAG) architecture with Llama_Index library.""")
    with tab1:
        st.subheader('Model selection')
        selected_model = st.radio('Select a conversation style', ['Creative', 'Precise'], key='selected_model', help="Llama 2 offers an innovative conversation style, weaving creativity into its responses, while Mistral focuses on precision, delivering accurate and well-researched information.")
        if selected_model == 'Creative':
            # model = 'a16z-infra/llama7b-v2-chat:4f0a4744c7295c024a1de15e1a63c880d3da035fa1f49bfd344fe076074c8eea'    # withdrawn as slow to response
            model = "meta/llama-2-7b-chat"
        elif selected_model == 'Precise':
            model = 'mistralai/mistral-7b-instruct-v0.2:f5701ad84de5715051cb99d550539719f8a7fbcf65e0e62a3d1eb3f94720764e'    # withdrawn as slow to response
            # model = "mistralai/mistral-7b-instruct-v0.2"
    with tab2:
        st.subheader('Advanced settings')
        max_new_tokens = st.slider('Maximum words to generate', min_value=300, max_value=1024, value=512, step=10, help="The maximum number of words(tokens) that the model will generate in response to the input.")
        # temperature = st.slider('temperature', min_value=0.01, max_value=5.0, value=0.1, step=0.1, help="The higher the temperature, the more random the output.")
        # context_window = st.sidebar.slider('context_window', min_value=4000, max_value=int(st.session_state["loaded_tokens"]*2.5), value=int(st.session_state["loaded_tokens"]), step=2000, help="The maximum number of tokens from the input that the model will consider. Simply say one single word can equal to 1-3 tokens. Higher token can provide a more comprehensive context for the model, but potentially lead to slower response (as the model would need to handle more context).")

# Call the initialize_llm function whenever the selected model, temperature, or context window changes
llm = initialize_llm(model, max_new_tokens)
# st.session_state

@st.cache_resource(show_spinner=False)
def load_data(all_results, selected_model):
    """
    Load the data from the search results and create a VectorStoreIndex.
    the model parameter is used to determine whether to run this function again when the spec is changed.
    """
    with st.spinner(text="Loading and indexing the news articles that you just scrapped – hang tight! This should take 10 seconds to 1 minute."):
        st.session_state["loaded_tokens"] = sum(len(all_results[i].get('scrapped_text').split()) for i in range(len(all_results)) if all_results[i].get('scrapped_text') != "Failed to scrape the article content...")
        documents = [Document(text=all_results[i].get('scrapped_text'), 
                              metadata={'supplier' : all_results[i].get('supplier'), 'focus': all_results[i].get('focus'),
                                    'title' : all_results[i].get('title'), 'date': all_results[i].get('date'), 'link': st.session_state.all_results[i].get('URL')}
                              ) for i in range(len(all_results)) if all_results[i].get('scrapped_text') != ""]  # Filter out empty scraped text, as it would cause error in the VectorStoreIndex
        index = VectorStoreIndex.from_documents(documents)
        query_engine = index.as_query_engine(streaming=True, response_mode="tree_summarize")
        print(f"Data loaded successfully! I am {selected_model} Chatbot!")
        return query_engine  

# Load Data 
st.session_state.loaded_tokens = 0 if 'loaded_tokens' not in st.session_state else st.session_state.loaded_tokens       # initialize the loaded_tokens in case if load_data function is not called
if selected_model == 'Creative':
    query_engine_llama2 = load_data(st.session_state.all_results, selected_model)
elif selected_model == 'Precise':
    query_engine_mistral = load_data(st.session_state.all_results, selected_model)
data_sources = {search['supplier']+" "+search['focus'] for search in st.session_state.search_inputs}
st.info(f"*Loaded {st.session_state['loaded_tokens']} words from {len(st.session_state.all_results)} articles, including {data_sources}*", icon="ℹ️")

# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "Hi how may I assist you? Please ask me any question about your scrapped news articles!"}]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "Hi how may I assist you? Please ask me any question about your scrapped news articles!"}]
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

# User-provided prompt
if prompt := st.chat_input(disabled=not replicate_api):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # if activate:
            #     response = query_engine.query(prompt)
            #     placeholder = st.empty()
            #     full_response = ''
            #     for token in response.response_gen:
            #         full_response += str(token)
            #         placeholder.markdown(full_response)
            # else:
            #     response = llm.stream_complete(prompt)
            #     placeholder = st.empty()
            #     full_response = ''
            #     for r in response:
            #         full_response += str(r.delta)
            #         placeholder.markdown(full_response)
            if selected_model == 'Creative':
                response = query_engine_llama2.query(prompt)
            elif selected_model == 'Precise':
                response = query_engine_mistral.query(prompt)
            placeholder = st.empty()
            full_response = ''
            for token in response.response_gen:
                full_response += str(token)
                placeholder.markdown(full_response)
            message = {"role": "assistant", "content": full_response}
            st.session_state.messages.append(message) # Add response to message history

# Footer
general_utils.add_footer()

# st.session_state