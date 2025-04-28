import pandas as pd
import streamlit as st
import json


def has_none_values(obj):
    if isinstance(obj, dict):
        return any(value is None or has_none_values(value) for value in obj.values())
    elif isinstance(obj, list):
        return any(value is None or has_none_values(value) for value in obj)
    return obj is None


def generate_sample_filename(convention):
    """Generate a sample filename based on the current convention."""
    parts = []
    for key in convention["MetadataOrder"]:
        if key == "Separators":
            continue
        elif convention["MetadataKeys"][key]["Type"] == "DateType":
            parts.append(convention["MetadataKeys"][key]["Format"])  # Placeholder for empty datetype data
        elif convention["MetadataKeys"][key]["Type"] == "Categorical":
            parts.append("XXX")  # Placeholder for empty categorical data
        elif convention["MetadataKeys"][key]["Type"] == "Numerical":
            dig = convention["MetadataKeys"][key]["Digits"]
            parts.append("#" * dig)  # Placeholder for numeric metadata
    example = ""
    for part_no in range(len(parts)):
        # Add the current string
        example += parts[part_no]
        # Add the separator if it exists and we're not at the last string
        if part_no < (len(parts) - 1):
            if convention["Separators"][part_no] == 'Underscore <_>':
                example += '_'
            elif convention["Separators"][part_no] == "Dash <->":
                example += "-"
            else:
                continue
    return example


def validate_metadata_df(df, metadata_name):
    """Validate the DataFrame for duplicate or invalid keys."""
    if df.empty or df[["Key", "Description"]].isna().all().all():
        st.warning(f"No data entered for {metadata_name}.")
        return False
    # Remove placeholder rows with empty Key
    df = df[df["Key"].notna() & (df["Key"] != "")]
    if df.empty:
        st.warning(f"No valid data entered for {metadata_name}.")
        return False
    # Check for duplicate keys
    if df["Key"].duplicated().any():
        st.error(f"Duplicate keys found in {metadata_name}. Each key must be unique.")
        return False
    # Check for invalid keys
    invalid_keys = df["Key"].isna() | (df["Key"] == "") | (~df["Key"].str.match("^[A-Z0-9]{1,3}$"))
    if invalid_keys.any():
        st.error(f"Invalid keys in {metadata_name}. Use 1–3 capital letters (A-Z) or numbers (0-9).")
        return False
    dictionary = df.to_dict()
    return dictionary


## Page begins here ##
current_date = st.session_state.current_date

st.header("Build your naming convention")
display_col = st.columns((4, 2),border=True)

with display_col[1]:
    if st.button("Visualize Convention File"):
        st.write(st.session_state['convention'])

with display_col[0]:
    with st.container(border=True):
        st.write("### 1. Create a name for your convention")
        fname = st.columns(2)
        with fname[0]:
            st.write("")
            fileset_name = st.text_input("**Give your convention a name**", max_chars=20,
                                         placeholder=f"{current_date}_naming_convention",
                                         help='''Use something that relates your files. Example: "MSc. Files"''',
                                         key='fileset_name'
                                         )
            if fileset_name:
                st.session_state['convention']["ConventionName"] = fileset_name
            else:
                st.session_state['convention']["ConventionName"] = f"{current_date}_naming_convention"

        with fname[1]:
            st.write(f'''
            Preview your convention name:
            ```
            {st.session_state['convention']["ConventionName"]}
            ```
            ''')

    with st.container(border=True):
        st.write("### 2. Choose the metadata for your convention")
        st.write("**What data types will your naming have?**:")
        datatypes = st.columns(3)
        date_in = datatypes[0].checkbox("Date")
        categorical_in = datatypes[1].checkbox("Categorical")
        numerical_in = datatypes[2].checkbox("Numerical")

        if not date_in and not categorical_in and not numerical_in:
            st.info('''
            Choose at least one data type!  
            Ensure don't leave empty fields.
            ''')
            st.stop()

        type_editors = st.columns(2)
        metadatas = {}
        if date_in:
            date_metadata = pd.DataFrame({"Date Description": st.session_state['option']['date_examples'],
                                          "Format": len(st.session_state['option']['date_examples']) * [None]})
            date_meta_mod = type_editors[0].data_editor(date_metadata, num_rows="dynamic",
                                                        column_config={
                                                            "Date Description": st.column_config.TextColumn(
                                                                max_chars=10, required=True),
                                                            "Format": st.column_config.SelectboxColumn(
                                                                options=st.session_state["option"]["date_formats"],
                                                                required=True)
                                                        }, use_container_width=True)
            type_editors[0].write("One metadata key is recommended.")
            for met in date_meta_mod["Date Description"]:
                metadatas[met] = {}
                metadatas[met]["Type"] = "DateType"
                metadatas[met]["Format"] = date_meta_mod["Format"][date_meta_mod["Date Description"] == met].values[0]

        if categorical_in:
            categorical_metadata = pd.DataFrame({"Categorical": st.session_state['option']['categorical_examples']})
            cat_meta_mod = type_editors[1].data_editor(categorical_metadata, num_rows="dynamic",
                                                       column_config={
                                                           "Categorical": st.column_config.TextColumn(max_chars=15,
                                                                                                      required=True),
                                                       }, use_container_width=True)
            type_editors[1].write("Subcategories will be added later.")
            for met1 in cat_meta_mod["Categorical"]:
                metadatas[met1] = {}
                metadatas[met1]["Type"] = "Categorical"

        if numerical_in:
            numerical_metadata = pd.DataFrame({"Description": st.session_state['option']['numerical_examples'],
                                               "Lower Limit": len(st.session_state['option']['numerical_examples']) * [
                                                   None],
                                               "Upper Limit": len(st.session_state['option']['numerical_examples']) * [
                                                   None]})

            num_meta_mod = st.data_editor(numerical_metadata, num_rows="dynamic",
                                          column_config={
                                              "Description": st.column_config.TextColumn(max_chars=10, required=True),
                                              "Lower Limit": st.column_config.NumberColumn(min_value=0, step=1,
                                                                                           max_value=9999,
                                                                                           required=True,
                                                                                           help='''
                                                                                            Add a key in the categorical data for negatives
                                                                                                 '''),
                                              "Upper Limit": st.column_config.NumberColumn(min_value=0, step=1,
                                                                                           max_value=9999,
                                                                                           required=True,
                                                                                           help='''
                                                                                                 If your value is higher than 9999 consider a different unit
                                                                                                 '''
                                                                                           ),
                                          })
            st.write("A numerator is recommended")

            for met2 in num_meta_mod["Description"]:
                metadatas[met2] = {}
                metadatas[met2]["Type"] = "Numerical"
                metadatas[met2]["Lower"] = num_meta_mod["Lower Limit"][num_meta_mod["Description"] == met2].values[0]
                metadatas[met2]["Upper"] = num_meta_mod["Upper Limit"][num_meta_mod["Description"] == met2].values[0]
                digit = int(len(str(num_meta_mod["Upper Limit"][num_meta_mod["Description"] == met2].values[0])))
                metadatas[met2]["Digits"] = digit

        if has_none_values(metadatas):
            st.error('''
            Tables have empty values  
            Eliminate those rows or fill them out!
            ''')
            st.stop()

        st.write("#### 2.1 Choose the metadata order")

        selected_metadata = st.multiselect("**Select what data to encode in the name in the order you'd like**",
                                           options=metadatas.keys(), help="If you exclude one, it will be disregarded")

        if len(selected_metadata) == 1:
            st.warning("Select more than one metadata")
            st.stop()
        elif not selected_metadata:
            st.info("Select more than one metadata to continue")
            st.stop()

        st.write("#### 2.2 How you'd like to join your metadata keys?")
        separator = st.multiselect(label='Choose the separator(s)',
                                   options=["None (Joined)", "Underscore <_>", "Dash <->"], max_selections=2,
                                   help="Select up to two separators")

        separator_list = []
        for idx, met in enumerate(selected_metadata):
            separator_list.append(f"{selected_metadata[idx]} + {selected_metadata[idx + 1]}")
            if idx == len(selected_metadata) - 2:
                break
        separators_df = pd.DataFrame({"Order": separator_list, "Separator": [None] * (len(selected_metadata) - 1)})

        if len(separator) == 2:
            st.write("**Edit the Separator column for two consecutive metadatas**")
            separators_modified = st.data_editor(separators_df, num_rows='static', hide_index=True, disabled=["Order"],
                                                 column_config={
                                                     "Separator": st.column_config.SelectboxColumn(
                                                         help="Choose the separator",
                                                         width="medium",
                                                         options=separator,
                                                         required=True,
                                                     )})
        elif len(separator) == 1:
            separators_modified = separators_df.copy()
            separators_modified["Separator"] = separator * (len(selected_metadata) - 1)
            st.write(separators_modified)

        if st.button("Create"):
            if not selected_metadata:
                st.warning("Forgot to select the metadata order")
            elif not separator:
                st.warning("Haven't select a separator yet!")
            else:
                st.session_state["convention"]["MetadataOrder"] = selected_metadata
                for meta in selected_metadata:
                    st.session_state["convention"]["MetadataKeys"][meta] = metadatas[meta]
                st.session_state["convention"]["Separators"] = separators_modified["Separator"].to_list()
                st.success('''
                The first instance of your Naming Convention has been built  
                **Continue** 👇
                ''')

    with st.container(border=True):
        st.write('''**Example name preview**:''')
        if bool(st.session_state["convention"]["Separators"]):
            st.write(f'''  
            ```
            {generate_sample_filename(st.session_state["convention"])}
            ```
            ''')
        else:
            st.warning("Hit create to see the example preview!")

    if categorical_in and bool(st.session_state["convention"]["MetadataKeys"]):
        with st.container(border=True):
            st.write('''### 3. Populate Categorical Data''')
            categorical_list = []
            for key in st.session_state["convention"]["MetadataKeys"]:
                if st.session_state["convention"]["MetadataKeys"][key]["Type"] == "Categorical":
                    categorical_list.append(key)

            selected_categorical = st.selectbox("Select a categorical metadata to edit", options=categorical_list)
            st.write(f"You are editing: **{selected_categorical}**")
            if selected_categorical:
                st.session_state["convention"]["MetadataKeys"][selected_categorical]["Categories"] = {"Key": [],
                                                                                                      "Description": []}
                sel_to_edit = pd.DataFrame(
                    st.session_state["convention"]["MetadataKeys"][selected_categorical]["Categories"], dtype=str)
            modified_categorical = st.data_editor(
                sel_to_edit,
                num_rows="dynamic",
                column_config={
                    "Key": st.column_config.TextColumn(
                        label="Key",
                        max_chars=3,
                        validate="^[A-Z0-9]{1,3}$",
                        help="Enter 1–3 characters (capital letters A-Z or numbers 0-9 only).",
                        required=True
                    ),
                    "Description": st.column_config.TextColumn(
                        label="Description",
                        max_chars=50,
                        help="Describe your key",
                        required=True
                    )
                },
                key=f"data_editor_{selected_categorical}"
            )

            if st.button(f"Save changes to {selected_categorical}"):
                validated_df = validate_metadata_df(modified_categorical, selected_categorical)
                if validated_df is not False:
                    st.session_state["convention"]["MetadataKeys"][selected_categorical]["Categories"] = validated_df
                    st.success(f"Updated {selected_categorical} successfully!")

    with st.container(border=True):
        st.write('''### 4. Export Naming Convention''')
        convention_json = json.dumps(st.session_state["convention"], indent=2)
        st.download_button(
            label="Download JSON",
            data=convention_json,
            file_name=f"{st.session_state["convention"]["ConventionName"]}.json",
            mime="application/json"
        )
