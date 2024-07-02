import streamlit as st
import cohere
from dotenv import dotenv_values
import fitz
import os
from io import BytesIO
import tempfile
import general_utils
import cohere_utils
import uuid
from annotated_text import annotated_text
import clipboard

# App title
st.set_page_config(
    page_title="News Scraping",
    page_icon="assets/page_icon.png",
)

config = dotenv_values(".env")

general_utils.add_logo("assets/logo.png")

# if "all_results" not in st.session_state:
#     st.session_state.all_results = None
#     st.warning("Please perform a search first.")
#     st.stop()  

@st.cache_data(show_spinner=False)
def load_local_files(files):
    local_files = []
    for file in files:
        file_extension = os.path.splitext(file.name)[1]
        if file_extension == ".pdf":
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(file.getvalue())
                pdf_reader = fitz.open(temp_file.name)
                for page_num in range(pdf_reader.page_count):
                    page = pdf_reader[page_num]
                    page_text = {
                        'file': file.name,
                        'page': f'Page {page_num + 1}',
                        'text': page.get_text('text'),
                    }
                    local_files.append(page_text)
        else:
            st.warning('Please provide PDF.', icon="⚠️")
    return local_files


@st.cache_data(show_spinner=False)
def embed_documents(raw_documents):
    vectorstore = cohere_utils.Vectorstore(raw_documents)
    return vectorstore

with st.sidebar:
    st.title('🤖 AI-powered Chatbot')
    if 'COHERE_API_KEY' in config:
        cohere_api = config['COHERE_API_KEY']
    elif 'COHERE_API_KEY' in st.secrets:
        st.success('API key already provided!', icon='✅')
        cohere_api = st.secrets['COHERE_API_KEY']
    else:
        cohere_api = st.text_input('Enter Cohere API token:', type='password')
        if not (len(cohere_api)==40):
            st.warning('Please enter your credentials!', icon='⚠️')
        else:
            st.success('Proceed to entering your prompt message!', icon='👉')
    tab1, tab2 = st.tabs(["Basic", "Advanced"])
    with tab1:
        datasource_radio = st.radio("External Data Source", ["Static News", "Web Search", "Local File"],
        captions = ["Utilise the scrapped news articles to answer your question", 
                    "Leverage a dynamic web search engine to enrich the chatbot's response",
                    "Upload a PDF or TXT document to be used as an external datasource."],
        help='''Choose data source for the chatbot's response: Static news articles, dynamic web search, or a local file. 
        For instance, when 'Web Search' is specified, the model's reply will be enriched dynamically with information found by web search.''')
        
        if datasource_radio == "Static News":
            if 'all_results' in st.session_state and st.session_state.all_results:
                with st.spinner("Loading, embedding, and indexing the scrapped news articles..."):
                    vectorstore = embed_documents(st.session_state.all_results)
        if datasource_radio == "Local File":
            uploaded_files = st.file_uploader("Upload one or more PDF file", type=['pdf'], accept_multiple_files=True)
        
        if 'uploaded_files' in locals() and uploaded_files:
            # Load and process the uploaded PDF or TXT files.
            with st.spinner("Loading and processing the uploaded PDF files..."):
                local_files = load_local_files(uploaded_files)
                vectorstore = embed_documents(local_files)
            st.write(f"{len(local_files)} pages uploaded and processed.")

        citation_radio = st.radio("Include Citations", ["No", "Yes"],
        help="Enable to include highlighted citations and references in the chatbot's response."
        )

    with tab2:
        st.subheader('Advanced settings')
        preamble_template= st.text_area('Preamble Template', 
        '''
        
    ## Task and Context
    You are a helpful, respectful and honest assistant. Please summarize the salient points of the text and do so in a flowing high natural language quality text. 
    Use bullet points along with reference dates where appropriate.

    ## Style Guide
    Use British spelling of words, and be professional.
        ''',
        help="This is a system message which guides how the model should behave throughout to generate a response. It can be considered as instructions for the model which outline the goals and behaviors for the conversation (recommend to follow the specific structure and format for optimal performance).")
        rerank_top_k = st.slider('No. of docs to be retrieved', min_value=1, max_value=10, value=5, step=1, help="The number of document chunks to be retrieved for each response.")
        # max_new_tokens = st.slider('Maximum words to generate', min_value=300, max_value=1024, value=512, step=10, help="The maximum number of words(tokens) that the model will generate in response to the input.")
        # temperature = st.slider('temperature', min_value=0.01, max_value=5.0, value=0.1, step=0.1, help="The higher the temperature, the more random the output

# display the information of loaded documents and data sources
if datasource_radio == "Static News" and 'vectorstore' in locals():
    loaded_tokens = sum(len(st.session_state.all_results[i].get('scrapped_text').split()) for i in range(len(st.session_state.all_results)) if st.session_state.all_results[i].get('scrapped_text') != "Failed to scrape the article content...")
    data_sources = {search['supplier']+" "+search['focus'] for search in st.session_state.search_inputs}
    st.success(f"*Loaded {loaded_tokens} words from {len(st.session_state.all_results)} articles, including {data_sources}*", icon='✅')
if citation_radio == "Yes":
    st.info('Highlighted citations will be included in the chatbot response.')

# initialize chat 
if 'messages' not in st.session_state:
    st.session_state.messages = [{'role': 'assistant', 'message': 'Hello! How can I help you today?'}]

# display chat history
for message in st.session_state.messages:
    st.chat_message(message['role']).write(message['message'])

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "message": "Hi how may I assist you? Please ask me any question about your scrapped news articles!"}]
    st.session_state['conversation_id'] = str(uuid.uuid4())
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

def on_copy_click(text):
    clipboard.copy(text)
    st.session_state.copied = text

# def on_citation_click(placeholder, full_response, citations, datasource_radio):
#     with st.spinner('Generating citations...'):
#         text_citated = cohere_utils.annotate_citations(full_response, citations, datasource_radio)
#         placeholder.empty()
#         annotated_text(text_citated)
#         st.markdown('#### Relevant Articles:')
#         id_offset = 4 if datasource_radio == "Static News" or datasource_radio == "Local File" else 11
#         for doc in sorted(cited_documents, key=lambda d: d['id']):
#             if datasource_radio == "Local File":
#                 st.write(f"[{doc['id'][id_offset:]}] {doc['file']}: [{doc['page']}]")
#             else:
#                 st.write(f"[{doc['id'][id_offset:]}] [{doc['title']}]({doc['url']})")

if "copied" not in st.session_state: 
    st.session_state.copied = ""

prompt = st.chat_input('Enter your message:')
if prompt:
    if not cohere_api:
        st.info('Please enter your Cohere API key to continue.')
        st.stop()
    if 'conversation_id' not in st.session_state:
        st.session_state['conversation_id'] = str(uuid.uuid4())
    st.chat_message('USER').write(prompt)
    with st.chat_message('assistant'):
        status_placeholder = st.empty()
        text_placeholder = st.empty()
        button_placeholder = st.empty()
        with status_placeholder.status('Thinking...') as status:
            co = cohere.Client(cohere_api)
            # Generate search queries, if any
            response_query = co.chat(message=prompt, search_queries_only=True, conversation_id=st.session_state.conversation_id)
            # If there are search queries, retrieve document chunks and respond
            if response_query.search_queries:
                # Set the message based on the datasource_radio value
                if datasource_radio == "Static News":
                    message = "Generating response based on scrapped articles..." 
                elif datasource_radio == "Local File":
                    message = "Generating response based on uploaded files..."
                else:
                    message = "Generating response based on web search..."
                st.write(message)
                # Retrieve document chunks for each query
                documents = []
                for query in response_query.search_queries:
                    st.write(f"Retrieving information for generated query: *{query.text}*")
                    if datasource_radio == "Static News" or datasource_radio == "Local File":
                        vectorstore.retrieve_top_k = 5
                        documents.extend(vectorstore.retrieve(query.text))
                    
                if datasource_radio == "Web Search":
                    response = co.chat_stream(message=prompt, connectors=[{"id": "web-search","continue_on_failure": False}],
                                   preamble = preamble_template, conversation_id=st.session_state.conversation_id)
                
                elif datasource_radio == "Static News" or datasource_radio == "Local File":
                    # Use document chunks to respond
                    response = co.chat_stream(
                        message = prompt,
                        model="command-r",
                        documents=documents,
                        conversation_id=st.session_state.conversation_id,
                        preamble = preamble_template
                    )
            
            # If there is no search query, directly respond
            else:
                st.write(f"No search queries found. Responding directly to the user message...")
                response = co.chat_stream(
                    message = prompt,
                    model="command-r",
                    conversation_id=st.session_state.conversation_id,
                )
                                                                
            # Print the chatbot response, citations, and documents
            citations = []
            cited_documents = []
            # Display response
            full_response = ''
            for event in response:
                if event.event_type == "text-generation":
                    full_response+= str(event.text)
                    text_placeholder.markdown(full_response)
                    print(event.text, end="")
                elif event.event_type == "citation-generation":
                    citations.extend(event.citations)
                elif event.event_type == "search-results":
                    cited_documents = event.documents
            button_placeholder.button("📋", on_click=on_copy_click, args=(full_response,))
            st.session_state.messages.append({'role': 'USER', 'message': prompt})
            st.session_state.messages.append({'role': 'assistant', 'message': full_response})
            status.update(label="Complete!", state="complete")

        # for document in cited_documents:
        #     for k,v in document.items():
        #         print(f"{k}: {v}")
        # st.button("✏️", on_click=on_citation_click, args=(placeholder, full_response, citations, datasource_radio)) 
        
        if citation_radio == "Yes":
            with st.spinner('Generating citations...'):
                text_citated = cohere_utils.annotate_citations(full_response, citations, datasource_radio)
                text_placeholder.empty()
                button_placeholder.empty()
                annotated_text(text_citated)
                st.markdown('#### Relevant Articles:')
                id_offset = 4 if datasource_radio == "Static News" or datasource_radio == "Local File" else 11
                for doc in sorted(cited_documents, key=lambda d: d['id']):
                    if datasource_radio == "Local File":
                        st.write(f"[{doc['id'][id_offset:]}] {doc['file']}: [{doc['page']}]")
                    else:
                        st.write(f"[{doc['id'][id_offset:]}] [{doc['title']}]({doc['url']})")
                st.button("📋", on_click=on_copy_click, args=(full_response,), key='button_with_citation') 

if st.session_state.copied:
    st.toast("Copied to clipboard", icon='✅')
    st.session_state.copied = ""

# Footer
general_utils.add_footer()

# st.session_state