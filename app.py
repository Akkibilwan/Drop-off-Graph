import streamlit as st
import pandas as pd
import io

def process_data(data):
    # Clean and parse session times
    data['Cleaned Session End'] = data['Sessions'].str.split(' - ').str[1].str.split('\n').str[0]
    data['Session Start'] = pd.to_datetime(data['Sessions'].str.split(' - ').str[0], format='%d/%m/%Y, %I:%M:%S %p')
    data['Session End'] = pd.to_datetime(data['Cleaned Session End'].str.strip(), format='%d/%m/%Y, %I:%M:%S %p')

    # Create a range of times at 5-minute intervals between the earliest and latest times in the data
    start_time = data['Session Start'].min().floor('5T')
    end_time = data['Session End'].max().ceil('5T')
    time_range = pd.date_range(start=start_time, end=end_time, freq='5T')

    # Initialize a DataFrame to hold drop-off counts
    drop_off_counts = pd.DataFrame(0, index=time_range, columns=['Drop-offs'])

    # Calculate the drop-offs for each 5-minute interval
    for i in range(len(time_range) - 1):
        current_interval = (data['Session End'] >= time_range[i]) & (data['Session End'] < time_range[i + 1])
        drop_off_counts.loc[time_range[i], 'Drop-offs'] = current_interval.sum()

    drop_off_counts['Time'] = drop_off_counts.index.strftime('%H:%M')
    drop_off_counts.reset_index(drop=True, inplace=True)

    return drop_off_counts

def main():
    st.title("User Drop-off Analysis")
    st.write("Upload a CSV file containing session data to generate a drop-off count report.")

    # File uploader
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:
        # Read the CSV file
        data = pd.read_csv(uploaded_file)

        # Process the data to get drop-off counts
        drop_off_counts = process_data(data)

        # Display the drop-off counts
        st.write("Drop-off Counts Every 5 Minutes")
        st.dataframe(drop_off_counts)

        # Convert DataFrame to CSV
        csv = drop_off_counts.to_csv(index=False)
        b64 = st.download_button(label="Download Drop-off CSV", data=csv, file_name='drop_off_counts.csv', mime='text/csv')

if __name__ == "__main__":
    main()
