import streamlit as st
import pandas as pd
from gsearch import google_search
from transformers import pipeline
import requests
from boilerpy3 import extractors
import extra_streamlit_components as stx
import general_utils 
from textblob import TextBlob
from dateutil.parser import parse

# 1 / Page Config
st.set_page_config(
    page_title="News Scraping",
    page_icon="assets/page_icon.png",
    layout="wide",
)
general_utils.add_logo("assets/logo.png")

# 2 / News Search 
# 2.1 / Google Search Setup
@st.cache_data
def search_google(search_params, date_restrict=None, gl=None):
    """Search Google for the input queries and return the results."""
    all_results= []
    for params in search_params:
        search_ID = params['search_ID']
        num_search = params['num_search']
        supplier_full_name = params['supplier'] 
        supplier_input = supplier_full_name
        if 'Limited' in supplier_full_name:
            supplier_input = supplier_full_name.strip('Limited')
            supplier_input = ' '.join(supplier_input.split()[:3])
        focus_input = params['focus'] 
        if supplier_input and focus_input:
            query = supplier_input + " " + focus_input 
        elif supplier_input != "":
            query = supplier_input 
        else:
            query = focus_input 
        # returns warning if both supplier_input and focus_input don't have values
        if query == "":
            st.toast("Please either remove your blank query or enter a valid search query", icon='⚠️')
            st.stop()
        try:
            search_results = google_search(query, date_restrict=date_restrict, gl=gl, num=num_search)
        except:
            st.toast("Error: Failed to retrieve search results from Google.", icon='⚠️')
            st.stop()
        for result in search_results:
            if " ... " in result['snippet']:
                potential_date, snippet = result['snippet'].split(" ... ", 1)
                # Try to parse the potential date
                try:
                    parse(potential_date, fuzzy=True)
                    date = potential_date
                except ValueError:
                    # If parsing fails, it's not a date
                    date = ""
            else:
                date = ""
                snippet = result['snippet']
            all_results.append({'search_ID': search_ID, 'supplier': supplier_full_name, 'focus': focus_input, 'title': result['title'], 'date' : date, 'snippet':snippet, 'URL': result['link']}) 
    return all_results

# 2.2 / Web Scrapping function
## can't use cache_data here as this is incompatible in streamlit to re-display the toast message
def extract_scrapped_content(all_results):
    """Extract the main content from the scraped URLs using the boilerpy3 library."""
    with st.spinner("Retrieving and scraping the news articles – hang tight!"):
        st.toast("Scraping News Websites...", icon='⏳')
        count=0
        for i in range(len(all_results)):
            url = all_results[i]['URL']
            if url.endswith('.pdf'):
                all_results[i]['scrapped_text'] = "Failed to scrape the article content..."
                st.toast(f"Skipping PDF file - {i+1}.", icon='⚠️')
                st.sidebar.write(f"Skipping PDF file - {i+1}: {url}")
                continue
            try:
                response = requests.get(url, verify=False, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, Like Gecko) Chrome/79.0.3945.88 Safari/537.36'}, timeout=4)
                if response.status_code == 200:
                    # Instantiate the extractor
                    extractor = extractors.ArticleExtractor()
                    # Extract the main content
                    try:
                        content = extractor.get_content(response.text)
                    except AttributeError:
                        st.toast(f"Failed to scrape the article content - {i+1}. The webpage might not have a properly formatted title tag.", icon='⚠️')
                        st.sidebar.write(f"Failed to scrape the article content - {i+1}. The webpage might not have a properly formatted title tag.")
                        content = "Failed to scrape the article content..."
                    except Exception as e:      # This will catch all other exceptions
                        st.toast(f"Failed to scrape the article content - {i+1}. Error: {e}", icon='⚠️')
                        st.sidebar.write(f"Failed to scrape the article content - {i+1}. Error: {e}")
                        content = "Failed to scrape the article content..."
                    all_results[i]['scrapped_text'] = content
                    count+=1
                    st.toast(f"Scrapped News No.{i+1} Successfully! News Title: {all_results[i]['title']}", icon='🔥')
                else:
                    all_results[i]['scrapped_text'] = "Failed to scrape the article content..."
                    st.toast(f"Failed to retrieve the News website - {i+1}. Response status code: {response.status_code}", icon="⚠️")
                    st.sidebar.write(f"Failed to retrieve the News {i+1}: {url}. Response status code: {response.status_code}")
            except requests.exceptions.RequestException as e:
                all_results[i]['scrapped_text'] = "Failed to scrape the article content..."
                st.toast(f"Failed to retrieve {url} due to timeout", icon="⚠️")
                st.sidebar.write(f"Failed to retrieve the News {i+1}: {url} due to timeout")
            
        st.toast(f"News Scraping Completed. Retrieved {count}/{len(all_results)} websites successfully", icon='🎉')
        st.sidebar.write(f"Retrieved {count}/{len(all_results)} websites successfully")
    return all_results

st.write("# Results")

# 2.3 / Execute Search and display input queries
if 'search_trigger' not in st.session_state:        # Stop the script if search trigger is not activated 
    st.warning("Please return and perform a search first.")
    st.stop() 

st.write("#### Your search queries and results are as follows 👇:")
df = pd.DataFrame(st.session_state['search_inputs']).drop(columns=['search_ID'])
df.index = df.index + 1  # Adjust index to start from 1
df = df.rename(columns={'num_search': 'Search Results', 'supplier' : 'Supplier', 'focus' : 'Focus'})  # Rename column
st.table(df)

if st.session_state.search_inputs and st.session_state.search_trigger is True:
    results = search_google(st.session_state.search_inputs, st.session_state.date_restrict, st.session_state.gl)
    st.session_state['all_results'] = extract_scrapped_content(results)
    st.session_state['summary'] = [None] * len(results)  # Initialize summary state
    st.session_state['tab_id'] = None
    st.session_state['search_trigger'] = False


# 3 / Display search results
# 3.1 / Machine Learning Model Setup for Summarization and Sentiment Analysis
@st.cache_resource(show_spinner=False)
def load_summarizer():
    """Load the BART summarization model from Hugging Face, which is pre-trained on English language and fine-tuned on CNN Daily Mail."""
    return pipeline("summarization", model="facebook/bart-large-cnn")

@st.cache_data(show_spinner=False)
def summarize_content(text: str): 
    """Summarize the input text using the BART model."""
    summarizer = load_summarizer()
    # Truncate the text to the maximum input length of the model
    text = text[:1024]
    summary = summarizer(text, max_length=100, min_length=50, do_sample=False)
    return summary[0]['summary_text']

def perform_sentiment_analysis(text: str):
    """Perform sentiment analysis on the input text."""
    polarity = TextBlob(text).sentiment.polarity
    # print(polarity)
    if polarity > 0.1:
        return ":blush:"
    elif polarity < 0.0:
        return ":worried:"
    else:
        return ":neutral_face:"

# 3.2 / Display the search results in the tabs
# 3.2.1 / Initialize tabs, using created search_ID as tab_id
if "all_results" in st.session_state:
    st.session_state['tab_id'] = stx.tab_bar(
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

# 3.2.2 / Lookup the search ID and display the search results
if st.session_state['tab_id'] is not None:
    df_all_results = pd.DataFrame(st.session_state['all_results'])      # Convert the list of dictionaries to a DataFrame
    start_index = df_all_results.loc[df_all_results['search_ID'] == int(st.session_state['tab_id'])].index[0]   # convert the tab_id to int
    end_index = df_all_results.loc[df_all_results['search_ID'] == int(st.session_state['tab_id'])].index[-1] + 1

    # generate 3 containers on a row, based on number of scraped results
    for i in range(start_index, end_index, 3):    # returns 0, 3, 6, 9
        row = st.columns(3)
        for con in range(len(row)):
            result_index = i + con
            if result_index < end_index:
                tile = row[con].container(height=280)
                tile.subheader(f"**{' '.join(st.session_state['all_results'][result_index]['supplier'].split()[:2])} {st.session_state['all_results'][result_index]['focus']} - News {result_index+1}**", divider='rainbow')
                con_ = tile.container()
                row_ = con_.columns([2, 0.3])
                if row_[0].button("✨Generate Summary", key=f"summary_button_{result_index}", help="Click to generate summary"):
                    if (st.session_state['all_results'][result_index].get('scrapped_text') and 
                    st.session_state['all_results'][result_index]['scrapped_text'] != "Failed to scrape the article content..."):
                        with st.spinner("Generating summary..."):
                            summary_text = summarize_content(st.session_state['all_results'][result_index]['scrapped_text'])
                            st.session_state['summary'][result_index] = summary_text
                    else:
                        tile.error("Failed to retrieve the main content from the URL. It may be due to firewall restrictions or the website's response to the GET request. Please try again later.")
                if st.session_state['summary'][result_index] is not None:
                    tile.markdown(f":orange[Summary: {st.session_state['summary'][result_index]}]")
                # Perform sentiment analysis to display smiley or sad face
                row_[1].subheader(perform_sentiment_analysis(st.session_state['all_results'][result_index]['scrapped_text'] 
                                                             if st.session_state['all_results'][result_index].get('scrapped_text') not in ["", "Failed to scrape the article content..."] 
                                                             else st.session_state['all_results'][result_index].get('title')))
                tile.write(f"Title: {st.session_state['all_results'][result_index]['title']}")
                tile.write(f"Date: {st.session_state['all_results'][result_index]['date']}")
                tile.write(f"Snippet: {st.session_state['all_results'][result_index]['snippet']}")
                tile.write(f"URL: {st.session_state['all_results'][result_index]['URL']}")
                
# Footer
general_utils.add_footer()
general_utils.hide_markdown_anchor_button()

# st.session_state