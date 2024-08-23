import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import io

# Function to process the CSV and generate drop-off data
def process_data(file):
    # Read the CSV file
    data = pd.read_csv(file)
    
    # Extract the leave times from the 'Sessions' column
    leave_times = []
    invalid_entries = []

    for session in data['Sessions']:
        try:
            leave_time_str = session.split(' - ')[1].strip()  # Extract end time
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
        # Format time intervals to only show time (not date)
        time_labels = [interval.strftime('%H:%M') for interval in time_intervals]
        
        # Create the Plotly figure
        fig = go.Figure(data=go.Scatter(x=time_labels, y=drop_off_counts, mode='lines+markers', marker=dict(color='red')))
        
        # Update layout for the figure
        fig.update_layout(
            title="User Drop-off Counts Every 5 Minutes",
            xaxis_title="Time",
            yaxis_title="Number of Users Dropped Off",
            xaxis=dict(tickmode='array', tickvals=time_labels),
            showlegend=False
        )
        
        # Display the Plotly chart
        st.plotly_chart(fig)
        
        # Provide download functionality for the plot
        img_buf = io.BytesIO()
        fig.write_image(img_buf, format='png')
        img_buf.seek(0)
        st.download_button(label="Download Image", data=img_buf, file_name="drop_off_visualization.png", mime="image/png")

