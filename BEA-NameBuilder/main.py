import streamlit as st
import json
from datetime import datetime

@st.cache_data(ttl="1h")
def get_json(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        st.error("File not found!")
        return {}
    except json.JSONDecodeError:
        st.error("Invalid JSON format in categories file!")
        return {}

st.set_page_config(page_title="BEA NameBuilder", page_icon="🔨", layout="wide")

current_date = datetime.today().strftime('%Y%m%d')
if "current_date" not in st.session_state:
    st.session_state.current_date = current_date

if 'convention' not in st.session_state:
    st.session_state['convention'] = get_json(file_path="assets/template.json")
    st.session_state['convention']["ConventionName"] = f"{current_date}_naming_convention"
    st.session_state['convention']["ConventionDate"] = current_date
if 'options' not in st.session_state:
    st.session_state['option'] = get_json("assets/options.json")
if not bool(st.session_state['convention']):
    st.error("Missing convention template")
    st.stop()
if not bool(st.session_state['option']):
    st.error("Missing option choices")
    st.stop()

st.info("Refresh the page if you want to start over!!")

pages = {
    "Home": [
        st.Page("sidebar/home.py", title="Readme",default=True),
    ],
    "NameBuilder": [
        st.Page("sidebar/convention_builder.py", title="🔨 Build Convention!"),
        st.Page("sidebar/name_generator.py", title="✒️ Name Generator!"),
        st.Page("sidebar/edit_convention.py", title="🪛 Edit Convention!"),
    ],
}

pg = st.navigation(pages)
pg.run()
