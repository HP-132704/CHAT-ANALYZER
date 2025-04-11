import re
import pandas as pd

def preprocess(data):
    # Regex pattern to match the date-time format (e.g., '28/07/20, 6:47 pm - ')
    pattern = r'\d{1,2}/\d{1,2}/\d{2,4}, \d{1,2}:\d{2}(?:\s?[ap]m)? - '

    # Splitting messages and dates
    messages = re.split(pattern, data)[1:]  # Extract messages after the first match
    dates = re.findall(pattern, data)  # Extract date-time strings

    # Create a DataFrame
    df = pd.DataFrame({'user_message': messages, 'message_date': dates})

    # Convert date column to datetime format
    try:
        df['message_date'] = pd.to_datetime(df['message_date'], format="%d/%m/%y, %I:%M %p - ", errors='coerce')
    except ValueError as e:
        print("Date conversion error:", e)
        return None

    # Rename the column for better understanding
    df.rename(columns={'message_date': 'date'}, inplace=True)

    # Separate users and messages
    users, messages = [], []
    for message in df['user_message']:
        # Split on first colon and space to separate user and message
        entry = re.split(r'([\w\W]+?):\s', message)
        if len(entry) > 1:
            users.append(entry[1])  # Username
            messages.append(entry[2])  # Message content
        else:
            users.append('group_notification')  # For system messages or notifications
            messages.append(entry[0])  # Entire message as content

    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)

    # Add additional date-time features
    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()

    # Convert hour to 12-hour format with AM/PM
    df['hour_12'] = df['date'].dt.strftime('%I:%M %p')  # 12-hour format with AM/PM

    # Add time periods for activity mapping (12-hour periods)
    periods = []
    for hour in df['date'].dt.hour:
        if hour == 23:
            periods.append(f"{hour}-00")
        elif hour == 0:
            periods.append(f"00-{hour + 1}")
        else:
            periods.append(f"{hour}-{hour + 1}")
    df['period'] = periods

    return df