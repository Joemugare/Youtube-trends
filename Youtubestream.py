import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import datetime
import folium
from streamlit_folium import folium_static  

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

# Streamlit App
st.title("Mugare's YouTube Trending Videos Dashboard")

# Dropdown for selecting country
selected_country = st.selectbox("Select a Country", ["US", "GB", "IN", "CA", "KE"])

# Retrieve data with published dates
video_data_with_dates = get_trending_videos_with_dates(selected_country)

# Convert date strings to datetime objects
for video in video_data_with_dates:
    video['Date Published'] = datetime.datetime.fromisoformat(video['Date Published'].replace('Z', '+00:00'))

# Bar chart
st.subheader(f'Bar Chart - Number of Views for Trending Videos in {selected_country}')
fig_bar, ax_bar = plt.subplots()
ax_bar.barh([video['Title'] for video in video_data_with_dates], [video['Views'] for video in video_data_with_dates], color='skyblue')
ax_bar.set_xlabel('Number of Views')
ax_bar.set_ylabel('Video Title')
ax_bar.invert_yaxis()
ax_bar.set_title(f'Trending Videos in {selected_country}')
for i, video in enumerate(video_data_with_dates):
    ax_bar.text(video['Views'], i, str(video['Views']), color='black', va='center')
st.pyplot(fig_bar)

# Pie chart
st.subheader(f'Pie Chart - Distribution of Likes for Trending Videos in {selected_country}')
fig_pie, ax_pie = plt.subplots()
ax_pie.pie([video['Likes'] for video in video_data_with_dates], labels=[video['Title'] for video in video_data_with_dates], autopct='%1.1f%%', startangle=90)
ax_pie.axis('equal')
ax_pie.set_title(f'Trending Videos in {selected_country}')
st.pyplot(fig_pie)

# Time series plot
st.subheader(f'Time Series Plot - Views Over Time for Trending Videos in {selected_country}')
fig_time_series, ax_time_series = plt.subplots()
for video in video_data_with_dates:
    ax_time_series.plot(video['Date Published'], video['Views'], marker='o', label=video['Title'])

ax_time_series.set_xlabel('Date Published')
ax_time_series.set_ylabel('Number of Views')
ax_time_series.set_title(f'Time Series - Views Over Time')
ax_time_series.legend(loc='upper left', bbox_to_anchor=(1, 1))
plt.xticks(rotation=45)
st.pyplot(fig_time_series)

# Video player
st.subheader("Interactive Video Player")
selected_video = st.selectbox("Select a Video to Watch", [video['Title'] for video in video_data_with_dates])

# Get the video ID for the selected video
video_id = next(video['Video ID'] for video in video_data_with_dates if video['Title'] == selected_video)

# Embed YouTube video
st.video(f"https://www.youtube.com/watch?v={video_id}")

# Display the geographical distribution on a map
st.subheader(f'Geographical Distribution of Trending Videos in {selected_country}')
m = folium.Map(location=[0, 0], zoom_start=2)

for video in video_data_with_dates:
    title = video['Title']
    views = video['Views']
    likes = video['Likes']
    date_published = video['Date Published'].strftime("%Y-%m-%d %H:%M:%S")
    video_url = f"https://www.youtube.com/watch?v={video['Video ID']}"

    # Add a marker for each video
    folium.Marker(
        location=[0, 0],  # Replace with actual latitude and longitude data if available
        popup=f"<strong>Title:</strong> {title}<br><strong>Views:</strong> {views}<br><strong>Likes:</strong> {likes}<br><strong>Date Published:</strong> {date_published}<br><a href='{video_url}' target='_blank'>Watch Video</a>",
        tooltip=title
    ).add_to(m)

# Display the map
folium_static(m)

# Social media sharing buttons
st.subheader("Share Your Favorite Video:")
selected_video = st.selectbox("Select a Video to Share", [video['Title'] for video in video_data_with_dates])

# Get the video ID for the selected video
video_id = next(video['Video ID'] for video in video_data_with_dates if video['Title'] == selected_video)

# Twitter sharing button
twitter_url = f"https://twitter.com/intent/tweet?url=https://www.youtube.com/watch?v={video_id}&text=Check%20out%20this%20awesome%20video:%20{selected_video}"
st.markdown(f'<a href="{twitter_url}" target="_blank"><img src="https://simplesharebuttons.com/images/somacro/twitter.png" alt="Twitter" width="40"></a>', unsafe_allow_html=True)

# Facebook sharing button
facebook_url = f"https://www.facebook.com/sharer/sharer.php?u=https://www.youtube.com/watch?v={video_id}&quote=Check%20out%20this%20awesome%20video:%20{selected_video}"
st.markdown(f'<a href="{facebook_url}" target="_blank"><img src="https://simplesharebuttons.com/images/somacro/facebook.png" alt="Facebook" width="40"></a>', unsafe_allow_html=True)
