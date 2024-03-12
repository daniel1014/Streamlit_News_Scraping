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
import general_utils

st.set_page_config(
    page_title="News Scraping",
    page_icon="assets/page_icon.png",
    menu_items={
        'Get Help': 'https://aecom.sharepoint.com/sites/HS2-LandPropertyDigitisation-ResearchIntelligence/',
        'Report a bug': "mailto:Daniel.Wong3@aecom.com",
        'About': "# This is a *News Scraping Analytics* app!"
    },
    layout="wide",
)
general_utils.add_logo()

nltk.download('stopwords')
nltk.download('punkt')

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

if not st.session_state.get("all_results"):
    st.warning("Please perform a search first.")
    st.stop()

# display input queries
df = pd.DataFrame(st.session_state['search_params']).drop(columns=['search_ID'])
df.index = df.index + 1  # Adjust index to start from 1
df = df.rename(columns={'num_search': 'Search Results', 'supplier' : 'Supplier', 'focus' : 'Focus'})  # Rename column
st.table(df)

# Initialize the trigger for the topic modelling
if "tab_id_topic" not in st.session_state:
    st.session_state['tab_id_topic'] = None

st.session_state['tab_id_topic'] = stx.tab_bar(
        data=[
            stx.TabBarItemData(
                id=st.session_state.search_params[i]['search_ID'], 
                title=' '.join(st.session_state.search_params[i]['supplier'].split()[:2]) + ' ' + st.session_state.search_params[i]['focus'], 
                description=f"Display {st.session_state.search_params[i]['num_search']} scrapped News"
            ) 
            for i in range(len(st.session_state['search_params']))
        ], 
        default=st.session_state.search_params[0]['search_ID']
    )

# Creating visualization for the LDA model, refactored from https://neptune.ai/blog/pyldavis-topic-modelling-exploration-tool-that-every-nlp-data-scientist-should-know
if st.session_state['tab_id_topic'] is not None:
    df_all_results = pd.DataFrame(st.session_state['all_results'])      # Convert the list of dictionaries to a DataFrame
    start_index = df_all_results.loc[df_all_results['search_ID'] == int(st.session_state['tab_id_topic'])].index[0]
    end_index = df_all_results.loc[df_all_results['search_ID'] == int(st.session_state['tab_id_topic'])].index[-1] + 1
    
    text_corpus = []
    # Extract the scrapped text from the DataFrame
    for i in range(start_index,end_index):
        text_corpus.append(df_all_results.iloc[i]['scrapped_text'])
    # Preprocess the text
    text_corpus_clean = preprocess_text(text_corpus)
    dictionary = corpora.Dictionary(text_corpus_clean)
    corpus = [dictionary.doc2bow(text) for text in text_corpus_clean]
    
    # Create a container for the LDA model
    with st.container(border=True):     
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

# Footer
general_utils.add_footer()

# st.session_state
