import streamlit as st

# Initialize session state with some default values
if "slider" not in st.session_state:
    st.session_state.slider = 50
if "text" not in st.session_state:
    st.session_state.text = "Hello"

# Define a callback function that resets the widget values
def reset_values():
    st.session_state.slider = 0
    st.session_state.text = ""

# Display a slider with session state as initial value
slider = st.slider("Slider", 0, 100, key="slider")
# Display a text input with session state as initial value
text = st.text_input("Text", key="text")
# Display a button with a callback that calls the reset function
button = st.button("Reset", on_click=reset_values)

# Display the current widget values
st.write(f"Slider value: {slider}")
st.write(f"Text value: {text}")
