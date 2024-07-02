import streamlit as st
import base64

def add_logo(img_path: str):
    with open(img_path, "rb") as img_file:
        b64_string = base64.b64encode(img_file.read()).decode()

    st.markdown(
        f"""
        <style>
            [data-testid="stSidebarNav"] {{
                background-image: url("data:image/png;base64,{b64_string}");
                background-repeat: no-repeat;
                padding-top: 15px;
                background-position: 20px 20px;
                background-size: 200px;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )

def set_page_background_local(img_path: str):
    with open(img_path, "rb") as img_file:
        b64_string = base64.b64encode(img_file.read()).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background: url("data:image/png;base64,{b64_string}");
            background-size: cover;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

def set_page_background_local_1(img_path: str):
    with open(img_path, "rb") as img_file:
        b64_string = base64.b64encode(img_file.read()).decode()

    st.markdown(
        f"""
        <style>
        body {{
            background-image: url("data:image/png;base64,{b64_string}");
            background-size: cover;
        }}
        .stApp {{
            background-color: transparent;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

def set_page_background_online(img_url: str):
    st.markdown(
        f"""
        <style>
        body {{
            background-image: url({img_url});
            background-size: cover;
        }}
        .stApp {{
            background-color: transparent;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

def set_primary_button_style(color: str):
    st.markdown(
        f"""
        <style>
        button[kind="primary"][data-testid="baseButton-primary"] {{
            width: 300px;
            height: 45px;
            background-color: {color};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

def set_radio_style():
    st.markdown("""
    <style>
    div[role="radiogroup"][aria-label = "Select the type of supplier"] > label[data-baseweb="radio"] > div > div > p {
        color: white;
    }
    # label[data-baseweb="radio"] {
    #     background-color: #000000;
    #     padding-right: 20px;
    #     padding-left: 10px;
    #     padding-bottom: 4px;
    #     margin: 5px;
    # }
    </style>
    """, unsafe_allow_html=True)

def set_selectbox_style():
    st.markdown(
        """
        <style>
        div[data-baseweb="select"] > div {
        background-color: white;
        color: black;
        }
        .st-ce {
            color: black;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

def set_text_input_style():
    st.markdown(
        """
        <style>
        div[data-testid="stTextInput"] > label > div > p {
        color: white;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

def hide_markdown_anchor_button():
    st.markdown("""
    <style>
    div[data-testid="stMarkdown"] > div > div > h3 > div > a {
        display: none;
    }
    </style>
    """, unsafe_allow_html=True)

def add_footer():
    st.sidebar.markdown(f"*:gray[logged in as {st.session_state.username}]*" if st.session_state.get("username") else "*Not logged in*")

def insert_citations(text: str, citations: list[dict]):
    """
    A helper function to pretty print citations.
    """
    offset = 0
    # Process citations in the order they were provided
    for citation in citations:
        # Adjust start/end with offset
        start, end = citation.start + offset, citation.end + offset
        if len(citation.document_ids) == 1:
            cited_docs = [citation.document_ids[0][11:]]
        elif len(citation.document_ids) == 2:
            cited_docs = [citation.document_ids[0][11:], citation.document_ids[1][11:]]
        elif len(citation.document_ids) == 3:
            cited_docs = [citation.document_ids[0][11:], citation.document_ids[1][11:], citation.document_ids[2][11:]]
        else:
            cited_docs = [citation.document_ids[0][11:], citation.document_ids[1][11:], citation.document_ids[2][11:], citation.document_ids[3][11:]]
        # Shorten citations if they're too long for convenience
        if len(cited_docs) > 3:
            placeholder = "[" + ", ".join(cited_docs[:3]) + "...]"
        else:
            placeholder = "[" + ", ".join(cited_docs) + "]"
        # ^ doc[4:] removes the 'doc_' prefix, and leaves the quoted document
        modification = f'**{text[start:end]} {placeholder}'
        # Replace the cited text with its bolded version + placeholder
        text = text[:start] + modification + text[end:]
        # Update the offset for subsequent replacements
        offset += len(modification) - (end - start)

    return text