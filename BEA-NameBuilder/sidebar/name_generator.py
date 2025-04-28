import streamlit as st
import json
import pandas as pd
from datetime import datetime
import qrcode
from io import BytesIO

def load_json(file):
    """Load JSON from an uploaded file."""
    try:
        return json.load(file)
    except json.JSONDecodeError:
        st.error("Invalid JSON format in the uploaded file!")
        return None


def format_numerical(value, digits):
    """Format numerical value to the specified number of digits."""
    if digits == 0:
        return str(int(value))
    return f"{int(value):0{digits}d}"


def generate_filename(convention, user_inputs):
    """Generate a filename based on user inputs and convention separators."""
    parts = []
    for key in convention["MetadataOrder"]:
        value = user_inputs.get(key)
        if convention["MetadataKeys"][key]["Type"] == "DateType":
            date_format = convention["MetadataKeys"][key]["Format"]
            if date_format == "YYYYMMDD":
                parts.append(value.strftime("%Y%m%d"))
            elif date_format == "MMDDYYYY":
                parts.append(value.strftime("%m%d%Y"))
            elif date_format == "DDMMYYYY":
                parts.append(value.strftime("%d%m%Y"))
            elif date_format == "MMYY":
                parts.append(value.strftime("%m%y"))
            elif date_format == "YYMM":
                parts.append(value.strftime("%y%m"))
        elif convention["MetadataKeys"][key]["Type"] == "Categorical":
            parts.append(value)
        elif convention["MetadataKeys"][key]["Type"] == "Numerical":
            digits = convention["MetadataKeys"][key]["Digits"]
            parts.append(format_numerical(value, digits))

    # Combine parts with separators
    filename = ""
    for i, part in enumerate(parts):
        filename += part
        if i < len(parts) - 1:
            separator = convention["Separators"][i]
            if separator == "Underscore <_>":
                filename += "_"
            elif separator == "Dash <->":
                filename += "-"
            # No separator for "None (Joined)"

    return filename


def generate_qr_code(text):
    """Generate a QR code from the given text and return it as a BytesIO object."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Save image to BytesIO
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr
# Streamlit app
st.header("Generate a File Name from Naming Convention")

# File uploader
uploaded_file = st.file_uploader("Upload your naming convention JSON file", type=["json"])
if not uploaded_file:
    st.info("Please upload a JSON file to continue.")
    st.stop()

# Load the convention
convention = load_json(uploaded_file)
if convention is None:
    st.stop()

# Validate convention structure
required_keys = ["ConventionName", "MetadataOrder", "MetadataKeys", "Separators"]
if not all(key in convention for key in required_keys):
    st.error("Invalid convention format. Missing required keys.")
    st.stop()

# Initialize session state for user inputs
if "user_inputs" not in st.session_state:
    st.session_state["user_inputs"] = {}

# Create input widgets based on MetadataOrder
st.subheader("Enter Metadata Values")
for key in convention["MetadataOrder"]:
    metadata = convention["MetadataKeys"].get(key)
    if not metadata:
        st.error(f"Metadata key {key} not found in MetadataKeys.")
        st.stop()

    metadata_type = metadata["Type"]

    if metadata_type == "DateType":
        label = f"Select date for {key}"
        date_value = st.date_input(
            label,
            min_value=datetime(1970, 11, 24),
            max_value=datetime(2099, 12, 31),
            value=datetime.today(),
            key=f"input_{key}"
        )
        st.session_state["user_inputs"][key] = date_value

    elif metadata_type == "Categorical":
        categories = metadata.get("Categories", {})
        if not categories or not categories.get("Key") or not categories.get("Description"):
            st.warning(f"No categories defined for {key}. Please add categories in the convention.")
            st.session_state["user_inputs"][key] = ""
            continue

        # Convert categories to a list of keys and descriptions
        keys = list(categories["Key"].values())
        descriptions = list(categories["Description"].values())
        options = [f"{k} - {d}" for k, d in zip(keys, descriptions)]
        selected = st.selectbox(
            f"Select {key}",
            options=options,
            key=f"input_{key}"
        )
        # Store only the key (e.g., "BEA")
        selected_key = selected.split(" - ")[0] if selected else ""
        st.session_state["user_inputs"][key] = selected_key

    elif metadata_type == "Numerical":
        lower = metadata.get("Lower", 0)
        upper = metadata.get("Upper", 9999)
        digits = metadata.get("Digits", 0)
        label = f"Enter number for {key} (between {lower} and {upper})"
        # Set format to display leading zeros based on digits
        input_format = "%d" if digits == 0 else f"%0{digits}d"
        value = st.number_input(
            label,
            min_value=float(lower),
            max_value=float(upper),
            value=float(lower),
            step=1.0,
            format=input_format,
            key=f"input_{key}"
        )
        st.session_state["user_inputs"][key] = value

# Generate and display the filename
if all(key in st.session_state["user_inputs"] for key in convention["MetadataOrder"]):
    filename = generate_filename(convention, st.session_state["user_inputs"])
    st.subheader("Generated File Name")
    st.code(filename, language="text")
    st.write("Copy the filename above to use it.")
    # Generate and display QR code
    st.subheader("QR Code for Filename")
    qr_image = generate_qr_code(filename)
    st.image(qr_image, caption="Scan this QR code to get the filename", use_container_width=False)

    # Download button for QR code
    st.download_button(
        label="Download QR Code",
        data=qr_image,
        file_name=f"{filename}_qr.png",
        mime="image/png"
    )
else:
    st.info("Please fill out all fields to generate the filename.")