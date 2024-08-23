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
        interval_data = df[(df['Leave Time'] >= start_time) & (df['Leave Time'] < end_time)]
        drop_off_count = interval_data.shape[0]
        drop_off_counts.append(drop_off_count)

    return time_intervals[:-1], drop_off_counts

# Streamlit app layout
st.title("Session Drop-off Visualization")

# Upload CSV file
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    # Process the uploaded file
    time_intervals, drop_off_counts = process_data(uploaded_file)
    
    if time_intervals is not None:
        # Plot the data
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(time_intervals, drop_off_counts, label='Drop-offs', color='red', marker='o')
        ax.set_xlabel('Time')
        ax.set_ylabel('Number of Users Dropped Off')
        ax.set_title('User Drop-off Counts Every 5 Minutes')
        ax.legend()
        ax.grid(True)
        st.pyplot(fig)
        
        # Provide download functionality for the plot
        img_buf = io.BytesIO()
        fig.savefig(img_buf, format='png')
        img_buf.seek(0)
        st.download_button(label="Download Image", data=img_buf, file_name="drop_off_visualization.png", mime="image/png")
