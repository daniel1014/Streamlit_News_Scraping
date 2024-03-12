import streamlit as st
import general_utils
import db_connection 
from streamlit_searchbox import st_searchbox
import pandas as pd
from typing import List, Tuple
import datetime

# Initialize the app
st.set_page_config(
    page_title="News Scraping",
    page_icon="assets/page_icon.png",
    menu_items={
        'Get Help': 'https://aecom.sharepoint.com/sites/HS2-LandPropertyDigitisation-ResearchIntelligence/',
        'Report a bug': "mailto:Daniel.Wong3@aecom.com",
        'About': "# This is a *News Scraping Analytics* app!"
    },
    initial_sidebar_state="collapsed",
    layout="centered",
    # layout="wide"
)

# Setup branding logo and customized background
general_utils.add_logo()
general_utils.set_page_background_local("assets/background.png")

for x in range(4):
    st.title("", anchor=False)        # Add some space on top

# st.markdown("<h2 style='text-align: left; color: white;'>News Scraping App</h5>", unsafe_allow_html=True)
# st.markdown("<h2 style='text-align: center; color: white;'>Let us do the search for you!</h2>", unsafe_allow_html=True)
# st.markdown("<h4 style='text-align: center; background-color: Orange;'>Start to connect the AI-chatbot and analytics insights with your search.</h3>", unsafe_allow_html=True)

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

##/ Sidebar options
# Date restriction buttons and selector
with st.sidebar:
    date_radio = st.radio(
        "Select a date range for the search",
        ("Any time", "Past 3 months", "Past 12 months", "Custom range")
    , help="Please note that this parameter restricts results to URLs indexed within the specified time period, not URLs that were created or updated within that time period. The date of indexing is determined by Google and may not be the same as the date the URL was actually created or updated.")
    if date_radio == "Any time":
        st.session_state['date_restrict'] = None
    elif date_radio == "Past 3 months":
        st.session_state['date_restrict'] = 'm3'
    elif date_radio == "Past 12 months":
        st.session_state['date_restrict'] = 'y1'
    else:
        try: 
            start_date, end_date = st.date_input('Select a date range', [datetime.date.today() - datetime.timedelta(days=30), datetime.date.today()])
        except ValueError:
            st.error("Error: End date must be after start date.")
        if start_date and end_date:
            # Convert the date range to the 'dateRestrict' format
            st.session_state['date_restrict'] = f'd{(end_date - start_date).days}'

# Geolocation selector (UK & any country)
    gl_radio = st.selectbox(
        "Select a country for the search",
        ("Any country", "United Kingdom","United States", "Australia", "Canada", "India", "Ireland", "New Zealand", "South Africa"), 
        help="This parameter boosts search results to the specified country. Although this is not required, you should use it if you want to enforce the country restriction.")
    if gl_radio == "Any country":
        st.session_state['gl'] = None
    elif gl_radio == "United Kingdom":
        st.session_state['gl'] = "uk"
    elif gl_radio == "United States":
        st.session_state['gl'] = "us"
    elif gl_radio == "Australia":
        st.session_state['gl'] = "au"
    elif gl_radio == "Canada":
        st.session_state['gl'] = "ca"
    elif gl_radio == "India":
        st.session_state['gl'] = "in"
    elif gl_radio == "Ireland":
        st.session_state['gl'] = "ie"
    elif gl_radio == "New Zealand":
        st.session_state['gl'] = "nz"
    elif gl_radio == "South Africa":
        st.session_state['gl'] = "za"

#// Main Program for Search Boxes       
# Read the CSV file
df = pd.read_csv('assets/supplier_list.csv')

# Convert the supplier names to a list
supplier_list = df['Supplier'].tolist()
def search(searchterm: str) -> List[Tuple[str, any]]:
    # Filter the supplier list based on the search term
    results = [supplier for supplier in supplier_list if searchterm.lower() in supplier.lower()]
    return results

# Initialize the session state
if 'num_searches' not in st.session_state:
    st.session_state['num_searches'] = 1
    st.session_state['searches'] = list(range(1))

# Create the main container for the search
main_container = st.container(border=False)
headers = main_container.columns([0.6,2,2,1], gap="small")

# Headers for the search form
headers[1].markdown("<h3 style='text-align: left; color: white;'>Select one of your Suppliers</h3>", unsafe_allow_html=True)
headers[2].markdown("<h3 style='text-align: left; color: white;'>Select a Focus</h3>", unsafe_allow_html=True)
headers[3].markdown("<h3 style='color: white;'>Search results</h3>", unsafe_allow_html=True)

# Add Search button
if headers[0].button(":heavy_plus_sign: Add"):
    st.session_state['num_searches'] += 1
    st.session_state['searches'].append(st.session_state['num_searches'])

# Create the search forms
for i in st.session_state['searches']:
    search_container = main_container.container()
    row = search_container.columns([0.6,2,2,1], gap="small")

    # Delete button
    if row[0].button("🗑️", key=f"search_delete_{i}"):
        st.session_state['searches'].remove(i)
        st.rerun()
        continue

    # Pass the search function to the searchbox
    with row[1].container():
        supplier_searchbox= st_searchbox(
        search,
        placeholder="Type your supplier",
        default=None,
        key=f"search_supplier_{i}",
    )

    with row[2].container():
        focus = st.selectbox(
            'Which focus would you like to search about?',
            label_visibility="collapsed",
            options=('Water Infrastructure', 'Infrastructure Maintenance', 'Supply Chain', 'Logistics Management', 'Risk Management', 'Mergers & Acquisitions', 'Financial Planning', 'Market Analysis', 'Quality Control', 'Regulatory Compliance', 'Sustainability Practices', 'Customer Service', 'Technology Integration', 'Other (Please specify)'),
            index=None,
            placeholder='Select a focus',
            key=f"search_focus_{i}"
        )
        focus_other = st.empty()
        if focus == 'Other (Please specify)':
            focus_other.text_input('Please specify', key=f"search_focus_other_{i}")
        
    with row[3].container():
        st.radio("Select the type of supplier", ('5', '10'), 
                 label_visibility="collapsed", 
                 horizontal=True, help="The number of suppliers to be displayed in the search result.",
                 key=f"search_num_{i}")

# Save the search parameters
st.session_state['search_params'] = []
for i in st.session_state['searches']:
    supplier = st.session_state[f"search_supplier_{i}"]["result"] or ""
    focus = st.session_state[f"search_focus_{i}"] or ""
    num_search = st.session_state[f"search_num_{i}"]
    st.session_state["search_params"].append({'search_ID': i, 'supplier': supplier, 'focus': focus, 'num_search': num_search})


#// Display the search results in the tabs
# Search the input queries and scrape the content from the URLs
row_last = main_container.columns([1,1,2])
if row_last[1].button("🔍 Search the web", type="primary"):
    st.session_state['search_trigger']=True
    st.switch_page("pages/01_🧊_Results.py")

# set the style
general_utils.set_radio_style()
general_utils.set_primary_button_style("#EC6642")

# Footer
general_utils.add_footer()

# st.session_state