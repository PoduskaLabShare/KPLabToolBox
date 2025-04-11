import streamlit as st
import pyvisa
from pyvisa import constants
import pandas as pd
import plotly.graph_objects as go
import json
from time import sleep
from datetime import datetime

time_label = datetime.now().strftime("%Y-%m-%d %H-%M")

with open("electrode_list.json") as f:
    electrodes = json.load(f)


def config_streamlit():
    """Configure Streamlit page settings and initialize session state variables."""
    if st.secrets:
        menu_items = {
            'Get Help': 'mailto:' + st.secrets['email']['administrator'],
            'Report a bug': 'mailto:' + st.secrets['email']['administrator'],
            'About': "# pH Meter App\nAn *extremely* cool tool for Orion Star A215!"
        }
    else:
        menu_items = None

    st.set_page_config(
        page_title="pH-OrionStarA215",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items=menu_items
    )
    if "connected" not in st.session_state:
        st.session_state["connected"] = False
    if "instrument" not in st.session_state:
        st.session_state["instrument"] = None
    if "data_log" not in st.session_state:
        st.session_state["data_log"] = pd.DataFrame(
            columns=["Date & Time", "pH Value", "mV Value", "Temperature Value"])


# Orion Star A215 settings
orion_settings = {
    "baud_rate": 9600,
    "data_bits": 8,
    "line_break": '\r',
    "line_termination": '>',
    "parity": None,
    "stop_bits": 1,
    "flow_control": None
}


@st.cache_data(ttl="6h", show_spinner="Scanning resources...")
def list_resources():
    """List available VISA resources with error handling."""
    try:
        rm = pyvisa.ResourceManager()
        resources = rm.list_resources()
        return resources if resources else ["No resources found"]
    except Exception as e:
        st.error(f"Error scanning resources: {e}")
        return []


def connect_to_instrument(resource, settings):
    """Establish connection to the instrument with specified settings."""
    try:
        rm = pyvisa.ResourceManager()
        inst = rm.open_resource(resource)
        inst.timeout = 5000
        inst.baud_rate = settings['baud_rate']
        inst.data_bits = settings['data_bits']
        inst.parity = constants.Parity.none if settings['parity'] is None else settings['parity']
        inst.stop_bits = constants.StopBits.one if settings['stop_bits'] == 1 else settings['stop_bits']
        inst.write_termination = settings['line_break']
        inst.read_termination = settings['line_termination']

        inst.write("SYSTEM")
        response = inst.read()
        st.write(f"Connected! Response: {response.strip('> ')}")
        return inst
    except pyvisa.errors.VisaIOError as e:
        st.error(f"Communication error with {resource}: {e} (Check if port is busy or device is on)")
    except Exception as e:
        st.error(f"Failed to connect to {resource}: {e}")
    return None


def get_measurement(inst):
    """Retrieve a single measurement from the instrument."""
    try:
        if not inst:
            raise ValueError("No instrument connected")
        inst.write("GETMEAS")
        response = inst.read()
        lines = response.strip('> ').split('\r')
        measurement_line = lines[3] if len(lines) > 3 else lines[0]
        return [item.strip() for item in measurement_line.split(",")]
    except Exception as e:
        st.error(f"Measurement failed: {e}")
        return None


def get_measurement2(inst, time_step=5):
    """Start timed measurements on channel 1 with specified interval."""
    step = str(int(time_step))
    try:
        if not inst:
            raise ValueError("No instrument connected")
        inst.write(f"GETMEASTIMED CH_1 {step}")
        response = inst.read()
        lines = response.strip('> ').split('\r')
        measurement_line = lines[3] if len(lines) > 3 else lines[0]
        return [item.strip() for item in measurement_line.split(",")]
    except Exception as e:
        st.error(f"Measurement failed: {e}")
        return None


def stop(inst):
    """Stop the current measurement process."""
    try:
        if not inst:
            raise ValueError("No instrument connected")
        inst.write("STOP")
        response = inst.read()
        lines = response.strip('> ').split('\r')
        measurement_line = lines[3] if len(lines) > 3 else lines[0]
        return [item.strip() for item in measurement_line.split(",")]
    except Exception as e:
        st.error(f"Measurement failed: {e}")
        return None


def get_log(inst, lower_limit, upper_limit):
    """Retrieve measurement logs between specified indices."""
    lower = str(int(lower_limit))
    upper = str(int(upper_limit))
    try:
        if not inst:
            raise ValueError("No instrument connected")
        inst.write(f"GETLOG {lower} {upper}")
        response = inst.read()
        lines = response.strip('> ').split('\r\n')
        data_lines = [line for line in lines if line and not line.startswith(('End of Data', 'GETLOG'))]

        if not data_lines:
            st.warning("No log data returned.")
            return pd.DataFrame()

        columns = [
            "Model", "Serial Number", "Firmware", "User ID", "Date & Time", "Sample ID",
            "Channel", "Mode", "pH Value", "pH Unit", "mV Value", "mV Unit",
            "Temperature Value", "Temperature Unit", "Slope Value", "Slope Unit",
            "Method", "Log #"
        ]

        measurements = [line.strip().split(',') for line in data_lines if line.strip()]

        # Check if measurements match expected column count
        if measurements and len(measurements[0]) != len(columns):
            st.warning("Log data format unexpected, displaying raw data")
            return pd.DataFrame(measurements)

        df = pd.DataFrame(measurements, columns=columns)
        return df

    except Exception as e:
        st.error(f"Log retrieval failed: {e}")
        return None


def convert_for_download(df):
    return df.to_csv().encode("utf-8")


# Initialize app
config_streamlit()
st.title("Poduska's pH-Meter")
st.caption("Orion Star A215")
st.caption(time_label)

# Connection Section
with st.container(border=True):
    st.header("Connect to pH Meter")
    if not st.session_state["connected"]:
        st.warning("Disconnected")
        st.markdown("""
        #### How to Select Your pH Meter
        1. Open **Device Manager** (Windows) and find your pH meter under 'Ports (COM & LPT)'.
        2. Note the COM port (e.g., COM8).
        3. Select the matching resource below (e.g., **COM8 = ASRL8::INSTR**).
        ##### :red[Important note]
        * The instrument has a time delay to respond so use the "Date & Time" column instead the elapsed 
        time column when plotting your data.
        """)

        pc_resources = list_resources()
        st.write("Detected resources:", pc_resources)

        col1, col2 = st.columns([3, 1])
        with col1:
            selected_resource = st.selectbox("Select your pH meter", options=pc_resources,
                                             index=pc_resources.index(
                                                 "ASRL8::INSTR") if "ASRL8::INSTR" in pc_resources else 0)
        with col2:
            if st.button("Refresh Resources", icon="🔃"):
                list_resources.clear()
                st.rerun()

        if st.button("Connect", type="primary"):
            inst = connect_to_instrument(selected_resource, orion_settings)
            if inst:
                st.session_state["instrument"] = inst
                st.session_state["selected_resource"] = selected_resource
                st.session_state["connected"] = True
                st.rerun()
    else:
        st.success(f"Connected to {st.session_state['selected_resource']}!")
        st.info("ℹ️ Don't forget to disconnect the instrument")
        if st.button("Disconnect"):
            st.session_state["instrument"].close()
            st.session_state["instrument"] = None
            st.session_state["connected"] = False
            st.rerun()

# Measurement Section
if not st.session_state["connected"] or not st.session_state["instrument"]:
    st.stop()

current_electrode = st.selectbox("Select the electrode you're working with:", options=electrodes["electrodes"])

online_meas, timed_meas = st.tabs(["Online Measurement", "Timed Measurement"])
with online_meas:
    st.write('''
    #### README
    This mode of measurement display real time data coming from the pH-meter every a set time step. 
    However, this measurement set up creates a delay in response (about 0.5s) regardless of the time step. Beware that the time
    elapsed is not a fixed time step. Still the `Date & Time` column is coming from the meter and is totally accurate. 
    ''')
    parm_column, display_col = st.columns((1, 2), gap='medium')
    with parm_column:
        st.header("pH Measuring Parameters")
        col1, col2 = st.columns(2)
        with col1:
            duration = st.number_input("Duration (min)", min_value=1, max_value=580, step=1)
        with col2:
            time_step = st.number_input("Time step (s)", min_value=5, max_value=17400, step=5)
        steps = int((duration * 60) / time_step)

    with display_col:
        # Initialize figure with proper layout
        fig = go.Figure(
            layout={
                "title": {"text": "pH vs Time"},
                "xaxis_title": "Time",
                "yaxis_title": "pH",
            }
        )
        # Add an empty scatter trace to update later
        fig.add_trace(go.Scatter(x=[], y=[], mode="lines+markers", name="pH"))
        plot_placeholder = st.plotly_chart(fig, use_container_width=True)
        status_placeholder = st.empty()

        if st.button("Record pH", type="primary"):
            st.session_state["data_log"] = pd.DataFrame(
                columns=["Date & Time", "Elapsed Time", "pH Value", "mV Value", "Temperature Value"])
            start_time = None
            with st.spinner("Recording pH..."):
                for cycle in range(steps):
                    record = get_measurement(st.session_state["instrument"])
                    if record:
                        timestamp = pd.to_datetime(record[4], format="%d/%m/%y %H:%M:%S")
                        if start_time is None:
                            start_time = timestamp
                        elapsed_time = (timestamp - start_time).total_seconds()

                        data = {
                            "Date & Time": timestamp,
                            "Elapsed Time": elapsed_time,
                            "pH Value": float(record[8]),
                            "mV Value": float(record[10]),
                            "Temperature Value": float(record[12])
                        }
                        st.session_state["data_log"] = pd.concat(
                            [st.session_state["data_log"], pd.DataFrame([data])], ignore_index=True
                        )

                        # Update the existing trace with the full dataset
                        fig.data[0].x = st.session_state["data_log"]["Date & Time"]
                        fig.data[0].y = st.session_state["data_log"]["pH Value"]
                        plot_placeholder.plotly_chart(fig, use_container_width=True)
                        status_placeholder.write(f"Progress: {cycle + 1}/{steps} measurements")
                        sleep(time_step)
                status_placeholder.write("Recording complete!")
            parm_column.write(st.session_state["data_log"])

        csv = convert_for_download(st.session_state["data_log"])
        parm_column.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"{current_electrode} {time_label}.csv",
            mime='text/csv'
        )
with timed_meas:
    st.write("""
    #### README
    This measurement will allow you to record a timed experiment with with fixed time steps,
    but results are not available until you decide to stop the timed measurement.
    """)
    fixed_time_step = st.number_input("Choose every how many seconds are you recording",
                                      min_value=3, step=1, max_value=3600,
                                      help="Minimum every 3 seconds / Maximum every 3600 seconds")

    if st.button("Time Measurement", key='time_button'):
        time_measurement_response = get_measurement2(st.session_state["instrument"], time_step=fixed_time_step)
        if len(time_measurement_response) >= 1:
            st.write(f'''
            Your experiment started at:  
            `{time_measurement_response[4]}`
            ''')
        else:
            st.warning("Starting time was not retrieved.")
    st.write('''
    Click the stop button to finish recording.  
    🚨 :red[If you don't click stop the meter will continue to log datapoints endlessly.]
    ''')
    if st.button("Stop"):
        stop(st.session_state["instrument"])
    st.write("""
    Click the **log view** button on the pH meter and find the initial and final **SNo** (record number) of
    your measurement 
    """)
    sno = st.columns(2)
    lower_sno = sno[0].number_input("Insert index of the initial measurement", min_value=1, max_value=2000)
    upper_sno = sno[1].number_input("Insert index of the final measurement", min_value=lower_sno + 1, max_value=2000)

    if st.button("Get Log"):
        log = get_log(st.session_state["instrument"], lower_sno, upper_sno)
        st.write(log)
        csv2 = convert_for_download(log)
        st.download_button(
            key='dowload_timed_meas',
            label="Download CSV",
            data=csv2,
            file_name=f"{current_electrode} {time_label}.csv",
            mime='text/csv'
        )