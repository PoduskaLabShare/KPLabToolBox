import streamlit as st

def load_instructions(path):
    """Load and return the markdown content from the instructions file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        st.error("Instructions file not found.")
        return ""
    except UnicodeDecodeError:
        st.error("Failed to decode instructions file. Ensure it is saved with UTF-8 encoding.")
        return ""

st.title("Welcome")
st.markdown(load_instructions("assets/instructions.md"), unsafe_allow_html=True)