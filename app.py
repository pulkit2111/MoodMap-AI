import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns
from TwitterPostAnalysis import twitterUserFetch

plt.rcParams['font.family']='Segoe UI Emoji'

analysis_type = st.sidebar.selectbox(
    "Choose the Analysis Type", ["WhatsApp Chat Analysis", "Twitter User Description"]
)

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
            positive, negative, neutral, negative_messages, positive_messages, neutral_messages=helper.wordsentiment(selected_user, df)
            st.title(f'Positive messages: {positive}')  # Use f-string to combine text and value
            st.title(f'Negative messages: {negative}')
            st.title(f'Neutral messages: {neutral}')

            st.write("Negative messages: ", negative_messages)
            st.write("Positive messages: ", positive_messages)
            st.write("Neutral messages: ", neutral_messages)

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
