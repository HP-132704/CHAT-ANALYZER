import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns
import base64

st.sidebar.title("MOBILE DATA ANALYZER")

# Function to get base64-encoded binary file
@st.cache_data
def get_base64_of_bin_file(bin_file):
    """
    Reads a binary file, encodes it in base64, and caches the result.

    Parameters:
        bin_file (str): Path to the binary file.

    Returns:
        str: Base64 encoded string of the binary file.
    """
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# File uploader section
uploaded_file = st.sidebar.file_uploader(" IMPORT YOUR FILE ")

if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")

    # Preprocess the uploaded file
    df = preprocessor.preprocess(data)

    if df is not None:
        if 'user' in df.columns:
            # Generate user list
            user_list = df['user'].dropna().unique().tolist()
            if 'group_notification' in user_list:
                user_list.remove('group_notification')
            user_list.sort()
            user_list.insert(0, "Overall")

            # User selection for analysis
            selected_user = st.sidebar.selectbox("Show analysis wrt", user_list)

            if st.sidebar.button("START THE APPLICATION"):
                # Fetch and display statistics
                num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)
                st.title("TOP STATISTICS")
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.header("TOTAL MESSAGE")
                    st.title(num_messages)
                with col2:
                    st.header("TOTAL WORDS")
                    st.title(words)
                with col3:
                    st.header("MEDIA SHARED")
                    st.title(num_media_messages)
                with col4:
                    st.header("LINKS SHARED")
                    st.title(num_links)

                # Monthly timeline
                st.title("MONTHLY TIMELINE")
                timeline = helper.monthly_timeline(selected_user, df)
                fig, ax = plt.subplots()
                ax.plot(timeline['time'], timeline['message'], color='green')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)

                # Daily timeline
                st.title("DAILY TIMELINE")
                daily_timeline = helper.daily_timeline(selected_user, df)
                fig, ax = plt.subplots()
                ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='black')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)

                # Activity maps
                st.title('ACTIVITY MAP')
                col1, col2 = st.columns(2)
                with col1:
                    st.header("MOST BUSY DAY")
                    busy_day = helper.week_activity_map(selected_user, df)
                    fig, ax = plt.subplots()
                    ax.bar(busy_day.index, busy_day.values, color='purple')
                    plt.xticks(rotation='vertical')
                    st.pyplot(fig)
                with col2:
                    st.header("MOST BUSY MONTH")
                    busy_month = helper.month_activity_map(selected_user, df)
                    fig, ax = plt.subplots()
                    ax.bar(busy_month.index, busy_month.values, color='black')
                    plt.xticks(rotation='vertical')
                    st.pyplot(fig)

                # Weekly activity heatmap
                st.title("WEEKLY ACTIVITY MAP")
                user_heatmap = helper.activity_heatmap(selected_user, df)
                fig, ax = plt.subplots()
                sns.heatmap(user_heatmap, ax=ax)
                st.pyplot(fig)

                # Busiest users
                if selected_user == 'Overall':
                    st.title('MOST BUSY USER')
                    x, new_df = helper.most_busy_users(df)
                    fig, ax = plt.subplots()
                    col1, col2 = st.columns(2)
                    with col1:
                        ax.bar(x.index, x.values, color='red')
                        plt.xticks(rotation='vertical')
                        st.pyplot(fig)
                    with col2:
                        st.dataframe(new_df)

                # WordCloud
                st.title("WORDINGS CLOUD")
                df_wc = helper.create_wordcloud(selected_user, df)
                fig, ax = plt.subplots()
                ax.imshow(df_wc)
                st.pyplot(fig)

                # Most common words
                most_common_df = helper.most_common_words(selected_user, df)
                fig, ax = plt.subplots()
                ax.barh(most_common_df[0], most_common_df[1])
                plt.xticks(rotation='vertical')
                st.title('MOST COMMON WORDS')
                st.pyplot(fig)

                # Emoji analysis
                emoji_df = helper.emoji_helper(selected_user, df)
                st.title("EMOJI AND SENTIMENT ANALYSIS")
                col1, col2 = st.columns(2)
                with col1:
                    st.dataframe(emoji_df)
                with col2:
                    fig, ax = plt.subplots()
                    ax.pie(emoji_df[1].head(), labels=emoji_df[0].head(), autopct="%0.2f")
                    st.pyplot(fig)
        else:
            st.error("The required column 'user' is missing from the dataset. Please check the input file.")
    else:
        st.error("Error processing the uploaded file. Please ensure it is in the correct format.")
