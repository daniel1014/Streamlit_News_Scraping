import streamlit as st
import gensim.corpora as corpora
from gensim.models.coherencemodel import CoherenceModel
from gensim.models.ldamodel import LdaModel

import pyLDAvis
import pyLDAvis.gensim

import pandas as pd

import extra_streamlit_components as stx
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

nltk.download('stopwords')
nltk.download('punkt')

st.set_page_config(
    page_title="Topic Modelling", 
    page_icon="📊",
    layout='wide', 
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

# def download_nltk_packages():
#     nltk_packages = ['stopwords', 'punkt']
#     for package in nltk_packages:
#         try:
#             nltk.data.find(f'tokenizers/{package}')
#         except LookupError:
#             nltk.download(package)

def preprocess_text(text_ls):
    preprocess_text = []
    for text in text_ls:
        if isinstance(text, str):  # Check if text is a string
            # Tokenization
            tokenized_text = word_tokenize(text)
            # Lowercasing
            lower_text = [word.lower() for word in tokenized_text]
            # Removing punctuation
            lower_text = [word for word in lower_text if word.isalpha()]
            # Removing stop words
            stop_words = set(stopwords.words('english'))
            filtered_text = [word for word in lower_text if word not in stop_words]
            preprocess_text.append(filtered_text)
        else:
            print(f"Text is not a string: {text}")
    return preprocess_text

st.write("# Topic Modelling")

if not st.session_state.get("all_results") or not st.session_state.get("_input_queries"):
    st.warning("Please perform a search first.")
    st.stop()

input_queries = st.dataframe(st.session_state['_input_queries'],  hide_index=True, width=1000,
            column_config={"num": st.column_config.SelectboxColumn(
            "Number of Search",
            help="How many search results do you want to retrieve?",
            width=20,
            default=10,
            options=[5,10],
            required=True,
            )
        })

# Initialize the trigger for the topic modelling
if "tab_id_topic" not in st.session_state:
    st.session_state['tab_id_topic'] = None

st.session_state['tab_id_topic'] = stx.tab_bar(data=[stx.TabBarItemData(id=st.session_state['_input_queries'][i]['supplier'], title=st.session_state['_input_queries'][i]['supplier']+' '+st.session_state['_input_queries'][i]['focus'], description=f"Display {st.session_state['_input_queries'][i]['num']} scrapped News") for i in range(len(st.session_state['_input_queries']))] , default=st.session_state['_input_queries'][0]['supplier'])

# Display the search results in the tabs, look up the index of the supplier in the DataFrame
if st.session_state['tab_id_topic'] is not None:
    df_all_results = pd.DataFrame(st.session_state['all_results'])      # Convert the list of dictionaries to a DataFrame
    start_index = df_all_results.loc[df_all_results['supplier'] == st.session_state['tab_id_topic']].index[0]
    end_index = df_all_results.loc[df_all_results['supplier'] == st.session_state['tab_id_topic']].index[-1] + 1
 
    text_corpus = []
    for i in range(start_index,end_index):
        text_corpus.append(df_all_results.iloc[i]['scrapped_text'])
    text_corpus_clean = preprocess_text(text_corpus)
    dictionary = corpora.Dictionary(text_corpus_clean)
    corpus = [dictionary.doc2bow(text) for text in text_corpus_clean]
    with st.container(border=True):     # Create a container for the LDA model
        col1, col2 = st.columns([1, 2], gap="large")
        num_topics = col1.slider("Number of Topics", min_value=1, max_value=(end_index-start_index)*2, value=end_index-start_index, help="The number of topics to be extracted from the scrapped News")
        lda_model = LdaModel(corpus=corpus, id2word=dictionary, num_topics=num_topics, passes=num_topics)
        # Compute Coherence Score
        coherence_model_lda = CoherenceModel(model=lda_model, texts=text_corpus_clean, dictionary=dictionary, coherence='u_mass')
        coherence_lda = coherence_model_lda.get_coherence()
        col2.markdown(f"**{num_topics} topics** are extracted from the scrapped articles using LDA model. Please check the **interactive visualization** below :point_down:")
        with col2.expander("Show Coherence Score"):
            st.subheader(f"Coherence Score: {coherence_lda}")
            st.markdown('''***Coherence score measures the semantic similarity between high-scoring words in topics. 
                        Higher scores indicate more coherent topics, aligning with the underlying theme. 
                        Negative scores suggest low coherence,  implies that the words within the topics are not semantically related, and the observed word co-occurrences are less likely to have occurred by chance 
                        Therefore, a negative coherence score does not necessarily imply poor performance.***''')

        # Prepare the visualization of the LDA model using pyLDAvis
        vis = pyLDAvis.gensim.prepare(lda_model, corpus, dictionary)

        # Convert the visualization to HTML
        vis_html = pyLDAvis.prepared_data_to_html(vis)

        # Display the HTML in the Streamlit app
        st.components.v1.html(vis_html, width=1400, height=800, scrolling=True)

# st.session_state
