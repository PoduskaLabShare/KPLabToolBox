import streamlit as st
import json
import pandas as pd
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

def load_json(file):
    """Load JSON from an uploaded file."""
    try:
        return json.load(file)
    except json.JSONDecodeError:
        st.error("Invalid JSON format in the uploaded file!")
        return None

def validate_convention(convention, template):
    """Validate that the uploaded convention complies with template.json structure."""
    required_keys = set(template.keys())
    if not all(key in convention for key in required_keys):
        st.error(f"Invalid convention format. Missing required keys: {required_keys - set(convention.keys())}")
        return False

    # Validate MetadataKeys structure
    for key, meta in convention["MetadataKeys"].items():
        if meta["Type"] not in ["DateType", "Categorical", "Numerical"]:
            st.error(f"Invalid metadata type for {key}: {meta['Type']}")
            return False
        if meta["Type"] == "DateType" and "Format" not in meta:
            st.error(f"Missing 'Format' for DateType metadata {key}")
            return False
        if meta["Type"] == "Categorical" and "Categories" not in meta:
            st.error(f"Missing 'Categories' for Categorical metadata {key}")
            return False
        if meta["Type"] == "Numerical" and not all(k in meta for k in ["Lower", "Upper", "Digits"]):
            st.error(f"Missing required fields (Lower, Upper, Digits) for Numerical metadata {key}")
            return False

    # Validate Separators length
    if len(convention["Separators"]) != len(convention["MetadataOrder"]) - 1:
        st.error("Number of separators must be one less than the number of metadata keys.")
        return False

    return True

def validate_metadata_df(df, metadata_name):
    """Validate the DataFrame for duplicate or invalid keys."""
    if df.empty or df[["Key", "Description"]].isna().all().all():
        st.warning(f"No data entered for {metadata_name}.")
        return False
    df = df[df["Key"].notna() & (df["Key"] != "")]
    if df.empty:
        st.warning(f"No valid data entered for {metadata_name}.")
        return False
    if df["Key"].duplicated().any():
        st.error(f"Duplicate keys found in {metadata_name}. Each key must be unique.")
        return False
    invalid_keys = df["Key"].isna() | (df["Key"] == "") | (~df["Key"].str.match("^[A-Z0-9]{1,3}$"))
    if invalid_keys.any():
        st.error(f"Invalid keys in {metadata_name}. Use 1–3 capital letters (A-Z) or numbers (0-9).")
        return False
    return df.to_dict()


# Streamlit app
st.header("Edit Existing Naming Convention")

# File uploader
uploaded_file = st.file_uploader("Upload your naming convention JSON file", type=["json"])
if not uploaded_file:
    st.info("Please upload a JSON file to continue.")
    st.stop()

# Load the convention
convention = load_json(uploaded_file)
if convention is None:
    st.stop()
st.write(convention)
# Load template for validation
if 'convention' in st.session_state:
    template = st.session_state['convention']
else:
    st.session_state['convention'] = get_json(file_path="assets/template.json")
    template = st.session_state['convention']

if not validate_convention(convention, template):
    st.error("Fix the errors or start a new convention")
    st.stop()

# Initialize session state for edited convention
if "edited_convention" not in st.session_state:
    st.session_state["edited_convention"] = convention

# Edit Convention Name
st.subheader("Convention Name")
col1, col2 = st.columns([3, 1])
with col1:
    convention_name = st.text_input(
        "Convention Name",
        value=st.session_state["edited_convention"]["ConventionName"],
        max_chars=20,
        key="edit_convention_name"
    )
    st.session_state["edited_convention"][
        "ConventionName"] = convention_name or f"{datetime.today().strftime('%Y%m%d')}_naming_convention"
with col2:
    st.write("Name Preview:")
    st.code(st.session_state["edited_convention"]["ConventionName"])

# Edit MetadataKeys
st.subheader("Edit Metadata")
for key in st.session_state["edited_convention"]["MetadataOrder"]:
    metadata = st.session_state["edited_convention"]["MetadataKeys"].get(key)
    if not metadata:
        st.error(f"Metadata key {key} not found in MetadataKeys.")
        continue

    st.write(f"#### {key}")
    metadata_type = metadata["Type"]

    if metadata_type == "DateType":
        format_options = st.session_state['option']['date_formats']
        current_format = metadata.get("Format", format_options[0])
        new_format = st.selectbox(
            f"Date Format for {key}",
            options=format_options,
            index=format_options.index(current_format) if current_format in format_options else 0,
            key=f"edit_date_format_{key}"
        )
        st.session_state["edited_convention"]["MetadataKeys"][key]["Format"] = new_format

    elif metadata_type == "Categorical":
        categories = metadata.get("Categories", {"Key": {}, "Description": {}})
        df = pd.DataFrame({
            "Key": list(categories["Key"].values()),
            "Description": list(categories["Description"].values())
        })
        modified_df = st.data_editor(
            df,
            num_rows="dynamic",
            column_config={
                "Key": st.column_config.TextColumn(
                    max_chars=3,
                    validate="^[A-Z0-9]{1,3}$",
                    help="1–3 capital letters (A-Z) or numbers (0-9).",
                    required=True
                ),
                "Description": st.column_config.TextColumn(
                    max_chars=50,
                    help="Describe your key",
                    required=True
                )
            },
            key=f"edit_categorical_{key}"
        )
        if st.button(f"Save changes to {key}", key=f"save_categorical_{key}"):
            validated_df = validate_metadata_df(modified_df, key)
            if validated_df is not False:
                st.session_state["edited_convention"]["MetadataKeys"][key]["Categories"] = validated_df
                st.success(f"Updated {key} successfully!")

    elif metadata_type == "Numerical":
        col_num1, col_num2 = st.columns(2)
        with col_num1:
            lower = st.number_input(
                f"Lower Limit for {key}",
                min_value=0,
                max_value=9999,
                value=int(metadata.get("Lower", 0)),
                step=1,
                key=f"edit_lower_{key}"
            )
        with col_num2:
            upper = st.number_input(
                f"Upper Limit for {key}",
                min_value=0,
                max_value=9999,
                value=int(metadata.get("Upper", 9999)),
                step=1,
                key=f"edit_upper_{key}"
            )

        st.session_state["edited_convention"]["MetadataKeys"][key]["Lower"] = lower
        st.session_state["edited_convention"]["MetadataKeys"][key]["Upper"] = upper

# Edit Metadata Order
st.subheader("Metadata Order")
new_order = st.multiselect(
    "Select metadata order",
    options=st.session_state["edited_convention"]["MetadataKeys"].keys(),
    default=st.session_state["edited_convention"]["MetadataOrder"],
    key="edit_metadata_order"
)
if not new_order:
    new_order = st.session_state["edited_convention"]["MetadataOrder"]

if len(new_order) < 2:
    st.warning("Select at least two metadata keys.")
else:
    st.session_state["edited_convention"]["MetadataOrder"] = new_order

# Edit Separators
st.subheader("Separators")
separator_options = ["None (Joined)", "Underscore <_>", "Dash <->"]
separator_list = []
for idx, met in enumerate(new_order[:-1]):
    separator_list.append(f"{met} + {new_order[idx + 1]}")
separators_df = pd.DataFrame({
    "Order": separator_list,
    "Separator": st.session_state["edited_convention"]["Separators"] + [None] * (
                len(separator_list) - len(st.session_state["edited_convention"]["Separators"]))
})
if new_order:
    modified_separators = st.data_editor(
        separators_df,
        num_rows="static",
        hide_index=True,
        disabled=["Order"],
        column_config={
            "Separator": st.column_config.SelectboxColumn(
                options=separator_options,
                required=True
            )
        },
        key="edit_separators"
    )
    st.session_state["edited_convention"]["Separators"] = modified_separators["Separator"].to_list()

# Export Updated Convention
st.subheader("Export Updated Convention")
convention_json = json.dumps(st.session_state["edited_convention"], indent=2)
st.download_button(
    label="Download Updated JSON",
    data=convention_json,
    file_name=f"{st.session_state['edited_convention']['ConventionName']}_edited.json",
    mime="application/json"
)