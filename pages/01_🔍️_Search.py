import streamlit as st
import pandas as pd
from gsearch import google_search
from transformers import pipeline
import requests
from boilerpy3 import extractors
import datetime
import extra_streamlit_components as stx
import general_utils 

st.set_page_config(
    page_title="Search Engine",
    page_icon="🔍️",
    layout="wide",
    menu_items={
        'Get Help': 'https://aecom.sharepoint.com/sites/HS2-LandPropertyDigitisation-ResearchIntelligence/',
        'Report a bug': "mailto:Daniel.Wong3@aecom.com",
        'About': "# This is a *News Scraping Analytics* app!"
    }
)

general_utils.add_logo()

st.write("# Welcome to the Search Engine! 👋")
# Instructions
with st.expander('🔍Instructions and Tips', expanded=False):
     st.markdown('''
* This tool is used to scrape news from Google Search Engine. Please **Login** with your username to load your historic input data (a new username will be registered if it is not exisiting in database). 
* Please enter your desired input query(s) including supplier, focus (eg. Enercon Supply Chain), and number of search. 
* When you're ready, click **'Search'** and an output table will be generated along with the tabs corresponding to your choice of input above. 
* Next, click **'Sentiment Analysis'** and views the related results from the bar chart. 
* If you want to save the current input(s) into the database, click **"Uploaded Input to AECOM database"** so you can download your data with your unique username when you are back next time. Furthermore, both the news output and sentiment analysis results can be downloaded as Excel or CSV file. 
''')
     st.write("")

#// Sidebar
# Date restriction buttons and selector
with st.sidebar:
    date_radio = st.radio(
        "Select a date range for the search",
        ("Any time", "Past 3 months", "Past 12 months", "Custom range")
    , help="Please note that this parameter restricts results to URLs indexed within the specified time period, not URLs that were created or updated within that time period. The date of indexing is determined by Google and may not be the same as the date the URL was actually created or updated.")
    if date_radio == "Any time":
        date_restrict = None
    elif date_radio == "Past 3 months":
        date_restrict = 'm3'
    elif date_radio == "Past 12 months":
        date_restrict = 'y1'
    else:
        try: 
            start_date, end_date = st.date_input('Select a date range', [datetime.date.today() - datetime.timedelta(days=30), datetime.date.today()])
        except ValueError:
            st.error("Error: End date must be after start date.")
        if start_date and end_date:
            # Convert the date range to the 'dateRestrict' format
            date_restrict = f'd{(end_date - start_date).days}'

# Geolocation selector (UK & any country)
with st.sidebar:
    gl_radio = st.selectbox(
        "Select a country for the search",
        ("Any country", "United Kingdom","United States", "Australia", "Canada", "India", "Ireland", "New Zealand", "South Africa"), 
        help="This parameter boosts search results to the specified country. Although this is not required, you should use it if you want to enforce the country restriction.")
    if gl_radio == "Any country":
        gl = None
    elif gl_radio == "United Kingdom":
        gl = "uk"
    elif gl_radio == "United States":
        gl = "us"
    elif gl_radio == "Australia":
        gl = "au"
    elif gl_radio == "Canada":
        gl = "ca"
    elif gl_radio == "India":
        gl = "in"
    elif gl_radio == "Ireland":
        gl = "ie"
    elif gl_radio == "New Zealand":
        gl = "nz"
    elif gl_radio == "South Africa":
        gl = "za"

#// Input queries
data_demo = [{'supplier':"Enercon",'focus':'Supply Chain', 'num':'10'}]
df_database_demo = pd.DataFrame(data_demo)

input_queries = st.data_editor(df_database_demo, num_rows="dynamic", hide_index=True, width=1000, key="input_queries",
            column_config={"num": st.column_config.SelectboxColumn(
            "Number of Search",
            help="How many search results do you want to retrieve?",
            width=20,
            default=10,
            options=[5,10],
            required=True,
            )
        })
 
#// Search & Scrapping functions
@st.cache_data
def search_google(query, date_restrict=None, gl=None, num=10):
    """Search Google for the input queries and return the results."""
    all_results= []
    for index, row in input_queries.iterrows():
        supplier_input = row['supplier']
        focus_input = row['focus']
        query = supplier_input + " " + focus_input
        num = row['num']
        search_results = google_search(query, date_restrict=date_restrict, gl=gl, num=num)
        for result in search_results:
            if " ... " in result['snippet']:
                date, snippet = result['snippet'].split(" ... ", 1)
            else:
                date = ""
            all_results.append({'supplier': supplier_input, 'focus': focus_input, 'title': result['title'], 'date' : date, 'snippet':snippet, 'URL': result['link']}) 
    return all_results

# can't use cache_data here as this is incompatible to re-display the containers
def extract_scrapped_content(all_results):
    """Extract the main content from the scraped URLs using the boilerpy3 library."""
    with st.spinner(text="Retrieving and scraping the news articles – hang tight! This should take 20 seconds to 1 minute."):
        st.toast("Scraping News Websites...", icon='⏳')
        count=0
        for i in range(len(all_results)):
            try:
                response = requests.get(all_results[i]['URL'], headers={'User-Agent': 'Mozilla/5.0'}, timeout=3)
                if response.status_code == 200:
                    # Instantiate the extractor
                    extractor = extractors.ArticleExtractor()
                    # Extract the main content
                    content = extractor.get_content(response.text)
                    all_results[i]['scrapped_text'] = content
                    count+=1
                    st.toast(f"Scrapped News No.{i+1} Successfully! News Title: {all_results[i]['title']}", icon='🔥')
                else:
                    st.toast(f"Failed to retrieve the News website - {i+1}. Response status code: {response.status_code}")
                    st.sidebar.write(f"Failed to retrieve the News {i+1}: {all_results[i]['URL']}. Response status code: {response.status_code}")
            except requests.exceptions.RequestException as e:
                st.toast(f"Failed to retrieve {all_results[i]['URL']} due to timeout")
                st.sidebar.write(f"Failed to retrieve the News {i+1}: {all_results[i]['URL']} due to timeout")
        st.toast(f"News Scraping Completed!", icon='🎉')
        st.sidebar.write(f"Retrieved {count}/{len(all_results)} websites successfully")
    return all_results

#// Summarization functions
@st.cache_resource
def load_summarizer():
    """Load the BART summarization model from Hugging Face, which is pre-trained on English language and fine-tuned on CNN Daily Mail."""
    return pipeline("summarization", model="facebook/bart-large-cnn")

@st.cache_data
def summarize_content(text: str): 
    """Summarize the input text using the BART model."""
    summarizer = load_summarizer()
    # Truncate the text to the maximum input length of the model
    print(len(text))
    text = text[:2500]
    summary = summarizer(text, max_length=100, min_length=50, do_sample=False)
    return summary[0]['summary_text']


# Initialize the search trigger
if 'search_trigger' not in st.session_state:
    st.session_state['search_trigger'] = False


#// Display the search results in the tabs
# Search the input queries and scrape the content from the URLs.
if st.button('Search'):
    st.session_state['_input_queries'] = input_queries.to_dict('records')
    all_results = search_google(input_queries, date_restrict, gl)
    st.session_state['all_results'] = extract_scrapped_content(all_results)
    st.session_state['summary'] = [None] * len(all_results)  # Initialize summary state
    st.session_state['search_trigger'] = True

# Initialize tabs, used supplier as tab_id
if st.session_state['search_trigger'] is True:
    st.session_state['tab_id'] = stx.tab_bar(data=[stx.TabBarItemData(id=input_queries.iloc[i]['supplier'], title=input_queries.iloc[i]['supplier']+' '+input_queries.iloc[i]['focus'], description=f"Display {input_queries.iloc[i]['num']} scrapped News") for i in range(len(input_queries))] , default=input_queries.iloc[0]['supplier'])

# Initialize the tab_id
if "tab_id" not in st.session_state:
    st.session_state['tab_id'] = None

# Display the search results in the tabs, look up the index of the supplier in the DataFrame
if st.session_state['tab_id'] is not None:
    df_all_results = pd.DataFrame(st.session_state['all_results'])      # Convert the list of dictionaries to a DataFrame
    start_index = df_all_results.loc[df_all_results['supplier'] == st.session_state['tab_id']].index[0]
    end_index = df_all_results.loc[df_all_results['supplier'] == st.session_state['tab_id']].index[-1] + 1

    # generate 3 containers on a row, based on number of scraped results
    for i in range(start_index, end_index, 3):    # returns 0, 3, 6, 9
        row = st.columns(3)
        for con in range(len(row)):
            result_index = i + con
            if result_index < end_index:
                tile = row[con].container(height=280)
                tile.subheader(f"**{st.session_state['all_results'][result_index]['supplier']} {st.session_state['all_results'][result_index]['focus']} - News {result_index+1}**", divider='rainbow')
                if tile.button("✨Generate Summary", key=f"summary_button_{result_index}", help="Click to generate summary"):
                    if st.session_state['all_results'][result_index].get('scrapped_text'):
                        summary_text = summarize_content(st.session_state['all_results'][result_index]['scrapped_text'])
                        st.session_state['summary'][result_index] = summary_text
                    else:
                        tile.error("Failed to retrieve the main content from the URL. It may be due to firewall restrictions or the website's response to the GET request. Please try again later.")
                if st.session_state['summary'][result_index] is not None:
                    tile.markdown(f":orange[Summary: {st.session_state['summary'][result_index]}]")
                tile.write(f"Title: {st.session_state['all_results'][result_index]['title']}")
                tile.write(f"Date: {st.session_state['all_results'][result_index]['date']}")
                tile.write(f"Snippet: {st.session_state['all_results'][result_index]['snippet']}")
                tile.write(f"URL: {st.session_state['all_results'][result_index]['URL']}")

    
# st.session_state