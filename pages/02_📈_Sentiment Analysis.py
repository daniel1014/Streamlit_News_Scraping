import streamlit as st
import pandas as pd
import altair as alt
from textblob import TextBlob
import general_utils

st.set_page_config(
    page_title="News Scraping",
    page_icon="assets/page_icon.png",
    layout='wide', 
    menu_items={
        'Get Help': 'https://aecom.sharepoint.com/sites/HS2-LandPropertyDigitisation-ResearchIntelligence/',
        'Report a bug': "mailto:Daniel.Wong3@aecom.com",
        'About': "# This is a *News Scraping Analytics* app!"
    },
)

general_utils.add_logo()

st.write("# Sentiment Analysis")

if not st.session_state.get("all_results"):
    st.warning("Please perform a search first.")
    st.stop()
        
df = pd.DataFrame(st.session_state['search_inputs']).drop(columns=['search_ID'])
df.index = df.index + 1  # Adjust index to start from 1
df = df.rename(columns={'num_search': 'Search Results', 'supplier' : 'Supplier', 'focus' : 'Focus'})  # Rename column
st.table(df)

# Create a sentiment analysis pipeline
# nlp = pipeline('sentiment-analysis', model="distilbert-base-uncased-finetuned-sst-2-english")

# model_selection = st.radio("Select a model", ["TextBlob", "Hugging Face"], captions = ["TextBlob", "Hugging Face"], horizontal=True) 

def perform_sentiment_analysis():
    sentiment_input = build_sentiment_input()
    sentiment_result, df_polarity = analyze_sentiment(sentiment_input)
    df_sentiment_result = pd.DataFrame(sentiment_result).T
    display_charts(df_sentiment_result, df_polarity)
    st.write(df_polarity.drop(columns=['Number of News Articles']))

def build_sentiment_input():
    sentiment_input = {}
    for row in st.session_state["all_results"]:
        key = f"{row['supplier']} {row['focus']}"
        text = row.get('scrapped_text', row['snippet'])
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
    st.altair_chart(chart, use_container_width=True, theme=None)
 
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
        alt.datum['Sentiment Score'] < 0.02
    ).mark_text(
        align='left',
        baseline='middle',
        dx=7  # Nudges text to right so it doesn't appear on top of the bar
    ).encode(
        text=alt.value('Negative')
    )

    text_neutral = base.transform_filter(
        alt.datum['Sentiment Score'] >= 0.02 and alt.datum['Sentiment Score'] <= 0.1
    ).mark_text(
        align='left',
        baseline='middle',
        dx=7  # Nudges text to right so it doesn't appear on top of the bar
    ).encode(
        text=alt.value('Neutral')
    )
    
    chart = (scatter_plot + text_positive + text_negative + text_neutral).properties(title='Sentiment Distribution of News Articles')
    
    st.altair_chart(chart, use_container_width=True, theme=None)

perform_sentiment_analysis()

# Footer
general_utils.add_footer()

# st.session_state