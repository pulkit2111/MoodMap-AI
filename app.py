import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns
from TwitterPostAnalysis import twitterUserFetch
import gmail_fetch
import pandas as pd
import spam_predictor
import os

plt.rcParams['font.family']='Segoe UI Emoji'

analysis_type = st.sidebar.selectbox(
    "Choose the Analysis Type", ["WhatsApp Chat Analysis", "Twitter User Description" , "Gmail Mails Analysis"]
)

def logout():
    """Logs the user out by removing the token.json file."""
    if os.path.exists('token.json'):
        os.remove('token.json')
        st.success("Logged out successfully!")
        st.session_state.logged_in = False  # Update session state

if analysis_type=="WhatsApp Chat Analysis":
    st.sidebar.title("WhatsApp Chat Analyzer")
    
    uploaded_files = st.sidebar.file_uploader(
        "Choose a txt file", accept_multiple_files=True
    )
    for uploaded_file in uploaded_files:
        bytes_data = uploaded_file.getvalue()
        data=bytes_data.decode("utf-8")
        # st.text(data)
        df=preprocessor.preprocess(data)

        # st.dataframe(df)

        # fetch unique users
        user_list = df['user'].unique().tolist()
        user_list.remove('group_notification')
        user_list.sort()
        user_list.insert(0,"Overall")

        selected_user = st.sidebar.selectbox("Show analysis wrt",user_list)

        if selected_user != 'Overall':
            st.dataframe(df[df['user'] == selected_user])
        else:
            st.dataframe(df)

        if st.sidebar.button("Show Analysis"):

            # Stats Area
            num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user,df)
            st.title("Top Statistics")
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.header("Total Messages")
                st.title(num_messages)
            with col2:
                st.header("Total Words")
                st.title(words)
            with col3:
                st.header("Media Shared")
                st.title(num_media_messages)
            with col4:
                st.header("Links Shared")
                st.title(num_links)

            #sentiment analyze
            positive, negative, neutral, styled_df=helper.wordsentiment(selected_user, df)
            st.dataframe(styled_df)
            st.title(f'Positive messages: {positive}')  # Use f-string to combine text and value
            st.title(f'Negative messages: {negative}')
            st.title(f'Neutral messages: {neutral}')

            # most common words
            most_common_df = helper.most_common_words(selected_user,df)

            fig,ax = plt.subplots()

            ax.barh(most_common_df[0],most_common_df[1])
            plt.xticks(rotation='vertical')

            st.title('Most commmon words')
            st.pyplot(fig)

            # finding the busiest users in the group(Group level)
            if selected_user == 'Overall':
                st.title('Most Busy Users')
                x,new_df = helper.most_busy_users(df)
                fig, ax = plt.subplots()

                col1, col2 = st.columns(2)

                with col1:
                    ax.bar(x.index, x.values,color='red')
                    plt.xticks(rotation='vertical')
                    st.pyplot(fig)
                with col2:
                    st.dataframe(new_df)

            # WordCloud
            st.title("Wordcloud")
            df_wc = helper.create_wordcloud(selected_user,df)
            fig,ax = plt.subplots()
            ax.imshow(df_wc)
            st.pyplot(fig)


            # monthly timeline
            st.title("Monthly Timeline")
            timeline = helper.monthly_timeline(selected_user,df)
            fig,ax = plt.subplots()
            ax.plot(timeline['time'], timeline['message'],color='green')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

            # daily timeline
            st.title("Daily Timeline")
            daily_timeline = helper.daily_timeline(selected_user, df)
            fig, ax = plt.subplots()
            ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='black')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

            # activity map
            st.title('Activity Map')
            col1,col2 = st.columns(2)

            with col1:
                st.header("Most busy day")
                busy_day = helper.week_activity_map(selected_user,df)
                fig,ax = plt.subplots()
                ax.bar(busy_day.index,busy_day.values,color='purple')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)

            with col2:
                st.header("Most busy month")
                busy_month = helper.month_activity_map(selected_user, df)
                fig, ax = plt.subplots()
                ax.bar(busy_month.index, busy_month.values,color='orange')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)

            st.title("Weekly Activity Map")
            user_heatmap = helper.activity_heatmap(selected_user,df)
            fig,ax = plt.subplots()
            ax = sns.heatmap(user_heatmap)
            st.pyplot(fig)

            # emoji analysis
            emoji_df = helper.emoji_helper(selected_user,df)
            st.title("Emoji Analysis")

            col1,col2 = st.columns(2)

            with col1:
                st.dataframe(emoji_df)
            with col2:
                fig,ax = plt.subplots()
                ax.pie(emoji_df['counts'].head(),labels=emoji_df['emoji'].head(),autopct="%0.2f")
                st.pyplot(fig)

elif analysis_type=="Twitter User Description":
    st.sidebar.title("Twitter User Description")
    twitter_url = st.text_input("Enter a post or profile URL to fetch user info:")

    if twitter_url:
        tweet_id=twitterUserFetch.extract_username(twitter_url)
        st.write("Tweet Id: ")
        st.write(tweet_id)

        if tweet_id:
            tweet_content = twitterUserFetch.get_user_info(tweet_id)
            st.write("User info: ")
            st.write(tweet_content)

elif analysis_type=="Gmail Mails Analysis":
    # Initialize session state to keep track of login status
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = os.path.exists('token.json')

    # Streamlit app
    st.title('Gmail Analysis')

    # Check login status and update UI accordingly
    if st.session_state.logged_in:
        st.sidebar.write("You are logged in.")

        # Show the logout button if the user is logged in
        if st.sidebar.button("Logout"):
            logout()
            st.rerun()  # This will refresh the app after logout

    else:
        st.sidebar.write("You are not logged in.")

        # Show the login button if the user is not logged in
        if st.sidebar.button("Login"):
            gmail_fetch.gmail_authenticate()  # Authenticate the user
            st.session_state.logged_in = True  # Update session state after login
            st.rerun()  # Refresh the app after login

    # Allow the user to fetch emails if they are logged in
    if st.session_state.logged_in:
        # Input for the number of emails and sender name
        emails = st.number_input("Enter the number of emails you want to see:", value=5, min_value=1)
        sender = st.text_input("Enter the sender's email:")

        # Fetch the emails
        # Assuming gmail_fetch.fetch_emails is a function that returns a DataFrame
        df = pd.DataFrame(gmail_fetch.fetch_emails(emails, sender))  # Uncomment this line to fetch emails
        df.index = range(1, len(df) + 1)

        # Display the emails in a dataframe if not empty
        if not df.empty:
            st.dataframe(df)
        else:
            st.write("No emails to display.")

