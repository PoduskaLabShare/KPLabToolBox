import pandas as pd
import numpy as np
import pyvisa
import streamlit as st
from datetime import datetime
import time
import plotly.express as px

# Orion Star A215 config per manual
instrument_name = 'ASRL7::INSTR'
baud_rate = 9600
bits = 8
parity = None
stop_bits = 1
flow_control = None
line_break = '\r'  # CR as per rule 1
line_termination = '>'  # Wait for prompt as per rule 3


# Function to set the time on the meter
def set_meter_time(inst):
    current_time = datetime.now()
    year = str(current_time.year)[-2:]  # Last two digits (2025 -> 25)
    month = str(current_time.month).zfill(2)  # Zero-pad (3 -> 03)
    day = str(current_time.day).zfill(2)  # Zero-pad (27 -> 27)
    hour = str(current_time.hour).zfill(2)  # 24-hour format
    minute = str(current_time.minute).zfill(2)
    second = str(current_time.second).zfill(2)

    setrtc_command = f"SETRTC {year} {month} {day} {hour} {minute} {second}"
    st.write(f"Sending: {setrtc_command}")
    inst.write(setrtc_command)
    response = inst.read()
    st.write("Response after SETRTC:", response.strip('> '))


def set_settings(name, rate, bits_no, parity, bits_stop, control_flow, break_line, line_end):
    try:
        rm = pyvisa.ResourceManager()
        instrument = rm.open_resource(name)
        # Set serial settings per the manual
        instrument.baud_rate = rate
        instrument.data_bits = bits_no
        if parity is None:
            instrument.parity = pyvisa.constants.Parity.none
        else:
            instrument.parity = parity  # Allow flexibility for other parity settings
        if bits_stop == 1:
            instrument.stop_bits = pyvisa.constants.StopBits.one
        else:
            instrument.stop_bits = bits_stop  # Allow flexibility
        if control_flow is None:
            instrument.flow_control = pyvisa.constants.ControlFlow.none
        else:
            instrument.flow_control = control_flow  # Allow flexibility

        instrument.write_termination = break_line
        instrument.read_termination = line_end
        set_meter_time(inst=instrument)
        return instrument
    except Exception as e:
        st.error(f"Error setting up instrument: {e}")
        return None


def check_system(inst):
    try:
        # Send the SYSTEM command and read response
        inst.write('SYSTEM')
        response = inst.read()
        st.success("Response: " + response.strip('> '))
        st.write("Done!!")
    except Exception as e:
        st.error(f"Error checking system: {e}")


def get_measurement(inst):
    try:
        # Send the GETMEAS command to get measurement and read response
        inst.write('GETMEAS')
        response = inst.read()
        lines = response.strip('> ').split('\r')
        measurement_line = lines[3] if len(lines) > 1 else lines[0]
        measurement = [item.strip() for item in measurement_line.split(",")]
        return measurement
    except Exception as e:
        st.error(f"Error getting measurement: {e}")


#### App begins here ####
st.title("ACBC pH-meter")

# Initialize session state for instrument
if "instrument" not in st.session_state:
    st.session_state["instrument"] = None

csetting1,csetting2 =st.columns(2)
with csetting1:
    # Button to set settings
    if st.button("Set settings"):
        # Close any existing instrument connection
        if st.session_state["instrument"] is not None:
            try:
                st.session_state["instrument"].close()
            except:
                pass  # Ignore errors during closure
        # Open a new connection
        instrument = set_settings(
            name=instrument_name,
            rate=baud_rate,
            bits_no=bits,
            parity=parity,
            bits_stop=stop_bits,
            control_flow=flow_control,
            break_line=line_break,
            line_end=line_termination
        )
        st.session_state["instrument"] = instrument
        if instrument:
            st.success("Instrument settings applied successfully!")
        else:
            st.error("Failed to set up instrument.")

    # Button to check system
    if st.button("Check system"):
        if st.session_state["instrument"] is not None:
            try:
                check_system(st.session_state["instrument"])
            except Exception as e:
                st.error(f"Error: {e}")
                st.session_state["instrument"] = None  # Reset on error
        else:
            st.error("System settings required. Please click 'Set settings' first.")

with csetting2:
    duration = st.number_input("Duration of the measurement (min)", min_value=1,max_value=580,
                               step=1)
    time_step = st.number_input("Recording time step (seg)", min_value=5, max_value=17400,step=10)

    steps = (duration*60)/time_step

with st.container():
    st.header("Get the pH")
    columns = ["Meter Model", "Serial Number", "Software Revision", "User ID", "Date & Time", "Sample ID", "Channel",
               "Mode", "pH Value", "pH Unit", "mV Value", "mV Unit", "Temperature Value", "Temperature Unit",
               "Slope Value", "Slope Unit", "Method #", "Log #"]
    if "data_log" not in st.session_state:
        st.session_state["data_log"] = pd.DataFrame(columns=columns)

    # Create a placeholder for the plot and display an empty scatter plot
    plot_placeholder = st.empty()
    # Initial empty scatter plot
    fig = px.scatter(
        title="pH vs Time",
        labels={"x": "Time (s)", "y": "pH"}
    )
    plot_placeholder.plotly_chart(fig, use_container_width=True)

    if st.button("Record pH"):
        if not st.session_state["data_log"].empty:
            st.session_state["data_log"] = pd.DataFrame(columns=columns)
        if st.session_state["instrument"]:
            cycle = 0
            start_time = None  # To store the first timestamp
            while cycle < steps:
                try:
                    record = get_measurement(st.session_state["instrument"])
                    if record is not None:
                        st.session_state["data_log"] = pd.concat(
                            [st.session_state["data_log"], pd.DataFrame([record], columns=columns)], ignore_index=True)

                        # Convert 'Date & Time' to datetime
                        current_time = pd.to_datetime(record[4], format="%d/%m/%y %H:%M:%S")

                        # Set the first timestamp as the reference (0 seconds)
                        if start_time is None:
                            start_time = current_time

                        # Calculate elapsed time in seconds
                        elapsed_time = (current_time - start_time).total_seconds()
                        st.session_state["data_log"].loc[cycle, "Time (s)"] = elapsed_time

                        # Ensure pH Value is numeric
                        st.session_state["data_log"]["pH Value"] = st.session_state["data_log"]["pH Value"].astype(
                            float)

                        # Update plot in real-time with scatter plot
                        fig = px.scatter(
                            st.session_state["data_log"],
                            x="Time (s)",
                            y="pH Value",
                            title="pH vs Time",
                            labels={"Elapsed Time (s)": "Time (s)", "pH Value": "pH"}
                        )
                        plot_placeholder.plotly_chart(fig, use_container_width=True)

                        time.sleep(time_step)
                        cycle += 1
                except Exception as e:
                    st.error(f"Error: {e}")
                    st.session_state["instrument"] = None  # Reset on error
                    break
            # Display the final data table with elapsed time
            st.write(st.session_state["data_log"][["Time (s)", "pH Value","mV Value","Temperature Value","Date & Time"]])
        else:
            st.error("System settings required. Please click 'Set settings' first.")

# Clean up when the app closes (optional, Streamlit handles this on restart)
if st.button("Close connection"):
    if st.session_state["instrument"] is not None:
        try:
            st.session_state["instrument"].close()
            st.session_state["instrument"] = None
            st.success("Connection closed.")
        except Exception as e:
            st.error(f"Error closing connection: {e}")

