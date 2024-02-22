import streamlit as st
import pandas as pd
from transformers import pipeline
import altair as alt
from textblob import TextBlob

st.set_page_config(
    page_title="Sentiment Analysis", 
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

st.write("# Sentiment Analysis")

if not st.session_state.get("all_results"):
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

# Create a sentiment analysis pipeline
nlp = pipeline('sentiment-analysis', model="distilbert-base-uncased-finetuned-sst-2-english")

model_selection = st.radio("Select a model", ["TextBlob", "Hugging Face"], captions = ["TextBlob", "Hugging Face"], horizontal=True) 

def perform_sentiment_analysis():
    sentiment_input = build_sentiment_input()
    sentiment_result, df_polarity = analyze_sentiment(sentiment_input)
    df_sentiment_result = pd.DataFrame(sentiment_result).T
    display_charts(df_sentiment_result, df_polarity)

def build_sentiment_input():
    sentiment_input = {}
    for row in st.session_state["all_results"]:
        key = f"{row['supplier']} {row['focus']}"
        text = row.get('scrapped_text', row['snippet'])
        sentiment_input.setdefault(key, []).append({row['title']: text})
    return sentiment_input

def analyze_sentiment(sentiment_input):
    sentiment_result = {}
    polarity_data = []
    for company_focus, all_news in sentiment_input.items():
        sentiment_result[company_focus] = {'positive': 0, 'neutral': 0, 'negative': 0}
        for news in all_news:
            for title, text in news.items():
                if model_selection == "TextBlob":
                    polarity = TextBlob(f"{title} {text}").sentiment.polarity
                elif model_selection == "Hugging Face":
                    result = nlp(f"{title} {text}"[:512])
                    print(result)
                    polarity = result[0]['score'] if result[0]['label'] == 'POSITIVE' else -result[0]['score']
                polarity_data.append({'supplier_focus': company_focus, 'title' : title, 'polarity': polarity})
                sentiment_result[company_focus][categorize_sentiment(polarity)] += 1
    df_polarity = pd.DataFrame(polarity_data)
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
        x='value:Q',
        y='index:N',
        color=alt.Color('variable:N', scale=alt.Scale(domain=['positive', 'neutral', 'negative'], range=['#AECC53', '#DAD8CC', '#C70C6F'])),
        tooltip=['index:N', 'variable:N', 'value:Q']
    ).properties(title='Sentiment Analysis Results')
    st.altair_chart(chart, use_container_width=True)
 
def display_scatter_chart(df_polarity):
    df_polarity = df_polarity.reset_index().rename(columns={'index': 'index_col'})
    chart = alt.Chart(df_polarity).mark_circle().encode(
        x='index_col',
        y='polarity',
        color='supplier_focus',
        tooltip=['title', 'polarity']
    ).properties(title='Polarity of News Articles')
    st.altair_chart(chart, use_container_width=True)

if st.button("Sentiment Analysis"):
    perform_sentiment_analysis()



# Hugging Face pipeline for sentiment analysis
# @st.cache_resource  # 👈 Add the caching decorator
# def load_model():
#     return pipeline("sentiment-analysis")

# if st.button("Sentiment Analysis"):
#     model = load_model()
#     sentiment_input = {}
#     for row in st.session_state["all_results"]:
#         sentiment_input[row['supplier']+" "+row['focus']] = [] if row['supplier']+" "+row['focus'] not in sentiment_input else sentiment_input[row['supplier']+" "+row['focus']]
#         if 'scrapped_text' in row:
#             sentiment_input[row['supplier']+" "+row['focus']].append({row['title']:row['scrapped_text']})
#         else:
#             sentiment_input[row['supplier']+" "+row['focus']].append({row['title']:row['snippet']})

#     # Use the transformer model for sentiment analysis
#     sentiment_result = {}
#     for key, values in sentiment_input.items():
#         sentiment_result[key] = {'positive': 0, 'neutral': 0, 'negative': 0}
#         for value in values:
#             for text in value.values():
#                 text = text[:512]
#                 result = model(text)[0]
#                 if result['label'] == 'POSITIVE':
#                     sentiment_result[key]['positive'] += 1
#                 else:
#                     sentiment_result[key]['negative'] += 1

#     df_sentiment_result = pd.DataFrame(sentiment_result).T
#     st.write(df_sentiment_result)

#     # Melt the DataFrame into a long format
#     df_long = df_sentiment_result.reset_index().melt('index')

#     # Create the Altair chart
#     chart = alt.Chart(df_long).mark_bar().encode(
#         x='value:Q',
#         y='index:N',
#         color=alt.Color('variable:N', scale=alt.Scale(domain=['positive', 'neutral', 'negative'], range=['#AECC53', '#DAD8CC', '#C70C6F'])),
#         tooltip=['index:N', 'variable:N', 'value:Q']
#     ).properties(title='Sentiment Analysis Results')

#     # Display the chart in Streamlit
#     st.altair_chart(chart, use_container_width=True)


st.session_state