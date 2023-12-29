import tkinter as tk
from tkinter import ttk
import config
import requests
import bs4
import selenium as sl
from googleapiclient.discovery import build
import os
import google_auth_oauthlib.flow
import googleapiclient.errors
### import googleapiclient.discovery


### Goals
### 1. Have functionality to go to a youtube channel and get Title, thumbnail, retention time, rating, description, captions, and viewcount
### 2. Build a UI to get this information for a given youtube channel
### 3. Put it into a downloadable repository
### 4. Make it a downloadable exe for anyone to use on desktop


# scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
# os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
# api_service_name = "youtube"
# api_version = "v3"
# client_secrets_file = "YOUR_CLIENT_SECRET_FILE.json"
# flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
#     client_secrets_file, scopes)
# credentials = flow.run_console()
# youtube = googleapiclient.discovery.build(
#     api_service_name, api_version, credentials=credentials)
#
# request = youtube.channels().list(
#     part="snippet,contentDetails,statistics",
#     id="UC_x5XG1OV2P6uZZ5FSM9Ttw"
# )
# response = request.execute()

api_key = config.api_key
youtube = build('youtube', 'v3', developerKey = api_key)

#Function to convert channel name to channel id

def get_channel_id(channel_name):
    search_response = youtube.search().list(
        part='id',
        q=channel_name,
        type='channel'
    ).execute()

    if 'items' in search_response:
        channel_id = search_response['items'][0]['id']['channelId']
        return channel_id
    else:
        return None


# Function to scrape video titles using Beautiful Soup
def scrape_videos_with_bs(channel_url):
    response = requests.get(channel_url)
    soup = bs4.BeautifulSoup(response.text, 'html.parser')

    video_titles = [title.text for title in soup.select('.yt-simple-endpoint.style-scope.yt-formatted-string')]
    return video_titles


# Function to retrieve video titles using YouTube API
def get_videos_with_api(channel_id):
    playlist_response = youtube.channels().list(
        part='contentDetails',
        id=channel_id
    ).execute()

    uploads_playlist_id = playlist_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    playlist_items = youtube.playlistItems().list(
        part='snippet',
        playlistId=uploads_playlist_id,
        maxResults=10  # Adjust as needed
    ).execute()

    video_titles = [item['snippet']['title'] for item in playlist_items['items']]
    return video_titles


# Function to handle the button click event
def on_button_click():
    channel_string = entry.get()
    # Scrape video titles using Beautiful Soup
    channel_id = get_channel_id(channel_string)

    channel_url = f'https://www.youtube.com/c/{channel_string}/videos'
    if channel_id:
        bs_video_titles = scrape_videos_with_bs(channel_url)
        #bs_result_label.config(text=f'Video Titles (Beautiful Soup): {", ".join(bs_video_titles)}')
        bs_result_text.delete(1.0, tk.END)  # Clear existing content
        bs_result_text.insert(tk.END, '\n'.join(bs_video_titles))

        # Retrieve video titles using YouTube API
        api_video_titles = get_videos_with_api(channel_id)
        #api_result_label.config(text=f'Video Titles (YouTube API): {", ".join(api_video_titles)}')
        api_result_text.delete(1.0, tk.END)  # Clear existing content
        api_result_text.insert(tk.END, '\n'.join(api_video_titles))
    else:
        bs_result_text.delete(1.0, tk.END)
        bs_result_text.insert(tk.END, 'Channel not found')

        api_result_text.delete(1.0, tk.END)
        api_result_text.insert(tk.END, 'Channel not found')


if __name__ == '__main__':
    root = tk.Tk()
    root.title('YouTube Scraper')

    # Create and place GUI components
    label = ttk.Label(root, text='Enter YouTube Channel:')
    label.grid(row=0, column=0, padx=10, pady=10)

    entry = ttk.Entry(root, width=20)
    entry.grid(row=0, column=1, padx=10, pady=10)

    button = ttk.Button(root, text='Get Video Titles', command=on_button_click)
    button.grid(row=0, column=2, padx=10, pady=10)

    # bs_result_label = ttk.Label(root, text='Video Titles (Beautiful Soup):')
    # bs_result_label.grid(row=1, column=0, columnspan=3, padx=10, pady=10)
    #
    # api_result_label = ttk.Label(root, text='Video Titles (YouTube API):')
    # api_result_label.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

    # Text widget for Beautiful Soup result
    bs_result_text = tk.Text(root, height=10, width=40)
    bs_result_text.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

    # Text widget for YouTube API result
    api_result_text = tk.Text(root, height=10, width=40)
    api_result_text.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

    # Start the Tkinter event loop
    root.mainloop()
