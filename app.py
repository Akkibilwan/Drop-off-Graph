import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

# Function to process the CSV and generate drop-off data
def process_data(file):
    # Read the CSV file
    data = pd.read_csv(file)
    
    # Extract the leave times and corresponding user names
    leave_times = []
    invalid_entries = []

    for session in data['Sessions']:
        try:
            leave_time_str = session.split(' - ')[1].strip()
            leave_time = pd.to_datetime(leave_time_str, format='%d/%m/%Y, %I:%M:%S %p', errors='coerce')
            
            if pd.isnull(leave_time):
                invalid_entries.append(session)
            else:
                leave_times.append(leave_time)
        except Exception as e:
            invalid_entries.append(session)
            continue

    # Combine leave times into a DataFrame
    df = pd.DataFrame({'Leave Time': leave_times})
    
    # Sort the DataFrame by leave times
    df = df.sort_values(by='Leave Time')
    
    if df.empty:
        st.error("No valid leave times found.")
        return None, None

    # Determine the session start and end times
    session_start_time = df['Leave Time'].min()
    session_end_time = df['Leave Time'].max()
    
    # Create 5-minute intervals
    time_intervals = pd.date_range(start=session_start_time, end=session_end_time, freq='5T')
    drop_off_counts = []

    for i in range(len(time_intervals)-1):
        start_time = time_intervals[i]
        end_time = time_intervals[i+1]
        interval_data = df[(df['Leave
