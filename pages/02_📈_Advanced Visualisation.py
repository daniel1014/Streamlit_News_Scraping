import streamlit as st
import pandas as pd
import altair as alt
from textblob import TextBlob
import general_utils
import gensim.corpora as corpora
from gensim.models.coherencemodel import CoherenceModel
from gensim.models.ldamodel import LdaModel
import pyLDAvis
import pyLDAvis.gensim
import extra_streamlit_components as stx
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

st.set_page_config(
    page_title="News Scraping",
    page_icon="assets/page_icon.png",
    layout='wide', 
)

st.logo("assets/logo.png")

tab1, tab2 = st.tabs(["📈 Sentiment Analysis", "💭 Topic Modelling"])

if not st.session_state.get("all_results"):
    st.warning("Please perform a search first.")
    st.stop()

#// Container for Sentiment Analysis
tab1.write("## Sentiment Analysis")
        
df = pd.DataFrame(st.session_state['search_inputs']).drop(columns=['search_ID'])
df.index = df.index + 1  # Adjust index to start from 1
df = df.rename(columns={'num_search': 'Search Results', 'supplier' : 'Supplier', 'focus' : 'Focus'})  # Rename column
tab1.table(df)

# Create a sentiment analysis pipeline
# nlp = pipeline('sentiment-analysis', model="distilbert-base-uncased-finetuned-sst-2-english")

# model_selection = st.radio("Select a model", ["TextBlob", "Hugging Face"], captions = ["TextBlob", "Hugging Face"], horizontal=True) 

def perform_sentiment_analysis():
    sentiment_input = build_sentiment_input()
    sentiment_result, df_polarity = analyze_sentiment(sentiment_input)
    df_sentiment_result = pd.DataFrame(sentiment_result).T
    display_charts(df_sentiment_result, df_polarity)
    tab1.write(df_polarity.drop(columns=['Number of News Articles']))

def build_sentiment_input():
    sentiment_input = {}
    for row in st.session_state["all_results"]:
        key = f"{row['supplier']} {row['focus']}"
        text = row.get('scrapped_text', row['snippet'])
        text = row['title'] if row.get('scrapped_text') == "Failed to scrape the article content..." else row.get('scrapped_text', row['title'])
        sentiment_input.setdefault(key, []).append({'title': row['title'], 'text': text, 'date': row['date'], 'url': row['URL']})
    return sentiment_input

def analyze_sentiment(sentiment_input):
    sentiment_result = {}
    polarity_data = []
    for company_focus, all_news in sentiment_input.items():
        sentiment_result[company_focus] = {'positive': 0, 'neutral': 0, 'negative': 0}
        news_number = 1
        for news in all_news:
            title = news['title']
            text = news['text']
            date = news['date']
            url = news['url']
            polarity = TextBlob(f"{title} {text}").sentiment.polarity
            polarity_data.append({'Supplier & focus': company_focus, 'News Title' : title, 'Date': date, 'Sentiment Score': polarity, 'Number of News Articles': news_number, 'Link': url})
            sentiment_result[company_focus][categorize_sentiment(polarity)] += 1
            news_number += 1
    df_polarity = pd.DataFrame(polarity_data)
    df_polarity = df_polarity.reindex(columns=['Supplier & focus', 'News Title', 'Date', 'Sentiment Score', 'Number of News Articles', 'Link'])
    df_polarity.index = df_polarity.index + 1
    return sentiment_result, df_polarity

def categorize_sentiment(polarity):
    if polarity > 0.1:
        return 'positive'
    elif polarity < 0.02:
        return 'negative'
    else:
        return 'neutral'

def display_charts(df_sentiment_result, df_polarity):
    df_long = df_sentiment_result.reset_index().melt('index')
    display_bar_chart(df_long)
    display_scatter_chart(df_polarity)

def display_bar_chart(df_long):
    chart = alt.Chart(df_long).mark_bar().encode(
        x=alt.X('value:Q', title='Number of News Articles', axis=alt.Axis(format='d')),
        y=alt.Y('index:N', title='Supplier & Focus'),
        color=alt.Color('variable:N', title='Sentiment', scale=alt.Scale(domain=['positive', 'neutral', 'negative'], range=['#AECC53', '#DAD8CC', '#C70C6F'])),
        tooltip=['index:N', 'variable:N', 'value:Q']
    ).properties(title='A high-level overview of sentiment analysis results')
    tab1.altair_chart(chart, use_container_width=True, theme=None)
 
def display_scatter_chart(df_polarity):
    df_polarity = df_polarity.reset_index()
    
    base = alt.Chart(df_polarity).encode(
        x=alt.X('Number of News Articles', scale=alt.Scale(domain=(1, df_polarity['Number of News Articles'].max())), axis=alt.Axis(format='d')),
        y='Sentiment Score',
        color=alt.Color('Supplier & focus', scale=alt.Scale(range=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'])),
        tooltip=['Supplier & focus', 'News Title', 'Date', 'Sentiment Score']
    )
    
    scatter_plot = base.mark_point(size=100)
    
    text_positive = base.transform_filter(
        alt.datum['Sentiment Score'] > 0.1
    ).mark_text(
        align='left',
        baseline='middle',
        dx=7  # Nudges text to right so it doesn't appear on top of the bar
    ).encode(
        text=alt.value('Positive')
    )
    
    text_negative = base.transform_filter(
        alt.datum['Sentiment Score'] < 0.0
    ).mark_text(
        align='left',
        baseline='middle',
        dx=7  # Nudges text to right so it doesn't appear on top of the bar
    ).encode(
        text=alt.value('Negative')
    )

    text_neutral = base.transform_filter(
        alt.datum['Sentiment Score'] >= 0.00 and alt.datum['Sentiment Score'] <= 0.1
    ).mark_text(
        align='left',
        baseline='middle',
        dx=7  # Nudges text to right so it doesn't appear on top of the bar
    ).encode(
        text=alt.value('Neutral')
    )
    
    chart = (scatter_plot + text_positive + text_negative + text_neutral).properties(title='Sentiment Distribution of News Articles')
    
    tab1.altair_chart(chart, use_container_width=True, theme=None)

perform_sentiment_analysis()

#// Container for Topic Modelling 
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

tab2.write("## Topic Modelling")

if not st.session_state.get("all_results"):
    st.warning("Please perform a search first.")
    st.stop()

# display input queries
df = pd.DataFrame(st.session_state['search_inputs']).drop(columns=['search_ID'])
df.index = df.index + 1  # Adjust index to start from 1
df = df.rename(columns={'num_search': 'Search Results', 'supplier' : 'Supplier', 'focus' : 'Focus'})  # Rename column
tab2.table(df)

# Initialize the trigger for the topic modelling
if "tab_id_topic" not in st.session_state:
    st.session_state['tab_id_topic'] = None

with tab2:
    st.session_state['tab_id_topic'] = stx.tab_bar(
        data=[
            stx.TabBarItemData(
                id=st.session_state.search_inputs[i]['search_ID'], 
                title=' '.join(st.session_state.search_inputs[i]['supplier'].split()[:2]) + ' ' + st.session_state.search_inputs[i]['focus'], 
                description=f"Display {st.session_state.search_inputs[i]['num_search']} scrapped News"
            ) 
            for i in range(len(st.session_state['search_inputs']))
        ], 
        default=st.session_state.search_inputs[0]['search_ID']
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
    with tab2.container(border=True):     
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