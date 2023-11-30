import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import datetime
from streamlit_folium import folium_static
import pandas as pd

# Set your API key
api_key = 'AIzaSyCaWWyNgY0_haGbbao9sB1148AKHaQsvC4'  # Replace with your actual API key

# Create a YouTube API client
youtube = build('youtube', 'v3', developerKey=api_key)

# Function to get trending videos with published dates
def get_trending_videos_with_dates(country_code):
    try:
        request = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            chart="mostPopular",
            regionCode=country_code,
            maxResults=10  # Adjust as needed
        )
        response = request.execute()

        data = []
        for video in response.get('items', []):
            title = video['snippet']['title']
            views = int(video['statistics']['viewCount'])
            
            # Check if 'likeCount' key is present in the video statistics
            if 'likeCount' in video['statistics']:
                likes = int(video['statistics']['likeCount'])
            else:
                likes = 0  # Set a default value if 'likeCount' is not present
            
            date_published = video['snippet']['publishedAt']
            video_id = video['id']
            data.append({'Title': title, 'Views': views, 'Likes': likes, 'Date Published': date_published, 'Video ID': video_id})

        return data

    except HttpError as e:
        print(f"An HTTP error occurred: {e}")
        return []

# Set page configuration
st.set_page_config(
    page_title="Mugare's YouTube Trending Videos Dashboard",
    page_icon="📺",  # Add your preferred icon here
    layout="wide"
)

# Streamlit App
st.title("Mugare's YouTube Trending Videos Dashboard")

# Dropdown for selecting country
selected_country = st.selectbox("Select a Country", ["US", "GB", "IN", "CA", "KE"])

# Retrieve data with published dates
video_data_with_dates = get_trending_videos_with_dates(selected_country)

# Convert date strings to datetime objects
for video in video_data_with_dates:
    video['Date Published'] = datetime.datetime.fromisoformat(video['Date Published'].replace('Z', '+00:00'))

# Bar chart for views
st.subheader(f'Bar Chart - Number of Views for Trending Videos in {selected_country}')
fig_bar_views, ax_bar_views = plt.subplots()
ax_bar_views.barh([video['Title'] for video in video_data_with_dates], [video['Views'] for video in video_data_with_dates], color='skyblue')
ax_bar_views.set_xlabel('Number of Views')
ax_bar_views.set_ylabel('Video Title')
ax_bar_views.invert_yaxis()
ax_bar_views.set_title(f'Trending Videos in {selected_country} - Views')
for i, video in enumerate(video_data_with_dates):
    ax_bar_views.text(video['Views'], i, str(video['Views']), color='black', va='center')
st.pyplot(fig_bar_views)

# Bar chart for likes
st.subheader(f'Bar Chart - Number of Likes for Trending Videos in {selected_country}')
fig_bar_likes, ax_bar_likes = plt.subplots()
ax_bar_likes.barh([video['Title'] for video in video_data_with_dates], [video['Likes'] for video in video_data_with_dates], color='lightcoral')
ax_bar_likes.set_xlabel('Number of Likes')
ax_bar_likes.set_ylabel('Video Title')
ax_bar_likes.invert_yaxis()
ax_bar_likes.set_title(f'Trending Videos in {selected_country} - Likes')
for i, video in enumerate(video_data_with_dates):
    ax_bar_likes.text(video['Likes'], i, str(video['Likes']), color='black', va='center')
st.pyplot(fig_bar_likes)

# Line chart for views and likes over time
st.subheader(f'Line Chart - Views and Likes Over Time for Trending Videos in {selected_country}')
fig_line_chart, ax_line_chart = plt.subplots()
for video in video_data_with_dates:
    ax_line_chart.plot(video['Date Published'], video['Views'], marker='o', label=f"{video['Title']} - Views")
    ax_line_chart.plot(video['Date Published'], video['Likes'], marker='o', label=f"{video['Title']} - Likes")

ax_line_chart.set_xlabel('Date Published')
ax_line_chart.set_ylabel('Count')
ax_line_chart.set_title(f'Views and Likes Over Time')
ax_line_chart.legend(loc='upper left', bbox_to_anchor=(1, 1))
plt.xticks(rotation=45)
st.pyplot(fig_line_chart)

# Summary table
st.subheader("Summary Table")
summary_data = {
    'Title': [video['Title'] for video in video_data_with_dates],
    'Views': [video['Views'] for video in video_data_with_dates],
    'Likes': [video['Likes'] for video in video_data_with_dates],
    'Date Published': [video['Date Published'].strftime("%Y-%m-%d %H:%M:%S") for video in video_data_with_dates]
}
summary_df = pd.DataFrame(summary_data)
st.table(summary_df)

# Video player
st.subheader("Interactive Video Player")
selected_video = st.selectbox("Select a Video to Watch", [video['Title'] for video in video_data_with_dates])

# Get the video ID for the selected video
video_id = next(video['Video ID'] for video in video_data_with_dates if video['Title'] == selected_video)

# Embed YouTube video
st.video(f"https://www.youtube.com/watch?v={video_id}")

# Social media sharing buttons
st.subheader("Share Your Favorite Video:")
selected_video_share = st.selectbox("Select a Video to Share", [video['Title'] for video in video_data_with_dates])

# Get the video ID for the selected video
video_id_share = next(video['Video ID'] for video in video_data_with_dates if video['Title'] == selected_video_share)

# Twitter sharing button
twitter_url = f"https://twitter.com/intent/tweet?url=https://www.youtube.com/watch?v={video_id_share}&text=Check%20out%20this%20awesome%20video:%20{selected_video_share}"
st.markdown(f'<a href="{twitter_url}" target="_blank"><img src="https://simplesharebuttons.com/images/somacro/twitter.png" alt="Twitter" width="40"></a>', unsafe_allow_html=True)

# Facebook sharing button
facebook_url = f"https://www.facebook.com/sharer/sharer.php?u=https://www.youtube.com/watch?v={video_id_share}&quote=Check%20out%20this%20awesome%20video:%20{selected_video_share}"
st.markdown(f'<a href="{facebook_url}" target="_blank"><img src="https://simplesharebuttons.com/images/somacro/facebook.png" alt="Facebook" width="40"></a>', unsafe_allow_html=True)
