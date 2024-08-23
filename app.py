import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import io

# Function to process the CSV and generate drop-off data
def process_data(file):
    # Read the CSV file
    data = pd.read_csv(file)
    
    # Extract the leave times
    data['Leave Time'] = data['Sessions'].apply(lambda x: x.split(' - ')[1].strip())
    data['Leave Time'] = pd.to_datetime(data['Leave Time'], format='%d/%m/%Y, %I:%M:%S %p', errors='coerce')
    
    # Filter out invalid dates
    data = data.dropna(subset=['Leave Time'])
    
    # Sort the leave times
    leave_times = data['Leave Time'].sort_values()
    
    # Determine the session start and end times
    session_start_time = leave_times.min()
    session_end_time = leave_times.max()
    
    # Create 5-minute intervals
    time_intervals = pd.date_range(start=session_start_time, end=session_end_time, freq='5T')
    drop_off_counts = []

    for i in range(len(time_intervals)-1):
        start_time = time_intervals[i]
        end_time = time_intervals[i+1]
        drop_off_count = leave_times[(leave_times >= start_time) & (leave_times < end_time)].count()
        drop_off_counts.append(drop_off_count)

    return time_intervals[:-1], drop_off_counts

# Streamlit app layout
st.title("Session Drop-off Visualization")

# Upload CSV file
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    # Process the uploaded file
    time_intervals, drop_off_counts = process_data(uploaded_file)
    
    # Plot the data
    st.subheader("Drop-off Visualization")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(time_intervals, drop_off_counts, label='Drop-offs', color='red', marker='o')
    ax.set_xlabel('Time')
    ax.set_ylabel('Number of Users Dropped Off')
    ax.set_title('User Drop-off Counts Every 5 Minutes')
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)
    
    # Provide download functionality for the plot
    st.subheader("Download the Visualization")
    img_buf = io.BytesIO()
    fig.savefig(img_buf, format='png')
    img_buf.seek(0)
    st.download_button(label="Download Image", data=img_buf, file_name="drop_off_visualization.png", mime="image/png")
    
    # Provide download functionality for the processed data
    download_data = pd.DataFrame({"Time Interval": time_intervals, "Drop-offs": drop_off_counts})
    csv_buf = io.StringIO()
    download_data.to_csv(csv_buf, index=False)
    csv_buf.seek(0)
    st.download_button(label="Download CSV Data", data=csv_buf, file_name="drop_off_data.csv", mime="text/csv")
