#### import image and UI libraries
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from io import BytesIO

#### external files
import config

#### scraper libraries
import requests
import bs4
import selenium as sl

#### api lib
from googleapiclient.discovery import build


### Goals
### 1. Have functionality to go to a youtube channel and get Title, thumbnail, retention time, rating, description, captions, and viewcount
### 2. Build a UI to get this information for a given youtube channel
### 3. Put it into a downloadable repository
### 4. Make it a downloadable exe for anyone to use on desktop

api_key = config.api_key
youtube = build('youtube', 'v3', developerKey = api_key)


# Function to convert channel name to channel id
def get_channel_id(channel_name):
    search_response = youtube.search().list(
        part='id',
        q=channel_name,
        type='channel'
    ).execute()

    # For each item in the search response for the channel name it's picking only the first record.
    # So it's possible for a channel to be set aside for another channel if they're spelled similarly
    # Example Mr. Feast might be a typo for Mr. Beast
    if 'items' in search_response:
        channel_id = search_response['items'][0]['id']['channelId']
        return channel_id
    else:
        return None


# # Function to scrape video titles using Beautiful Soup
# def scrape_videos_with_bs(channel_url):
#     response = requests.get(channel_url)
#     soup = bs4.BeautifulSoup(response.text, 'html.parser')
#     print(response)
#     print(soup)
#     print(soup.select('.yt-simple-endpoint.style-scope.yt-formatted-string'))
#     video_titles = [title.text for title in soup.select('.yt-simple-endpoint.style-scope.yt-formatted-string')]
#     print(video_titles)
#     return video_titles


def scrape_videos_with_bs(channel_url):
    response = requests.get(channel_url)
    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    print(soup)
    print(soup.select('.style-scope ytd-grid-video-renderer'))
    video_titles = []
    video_thumbnails = []

    for item in soup.select('.style-scope ytd-grid-video-renderer'):
        title = item.find('a', {'id': 'video-title'}).text.strip()
        thumbnail_anchor = item.find('a', {'id': 'thumbnail'})
        thumbnail_url = thumbnail_anchor.find('img').get('src')
        video_titles.append(title)
        video_thumbnails.append(get_thumbnail(thumbnail_url))
        print(video_titles)
        print(video_thumbnails)

    return video_titles, video_thumbnails

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


# Function to retrieve thumbnails from videos
def get_thumbnail(url):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    img.thumbnail((100, 100))  # Resize thumbnail if needed
    thumbnail = ImageTk.PhotoImage(img)
    return thumbnail


def get_thumbnail_url(video_title):
    thumbnail_url = f'http://img.youtube.com/vi/{video_title}/maxresdefault.jpg'
    return thumbnail_url


# Function to actually display each thumbnail in the tkinter application
def display_thumbnails(thumbnails):
    for i, thumbnail in enumerate(thumbnails):
        thumbnail_label = ttk.Label(thumbnails_frame, image=thumbnail)
        thumbnail_label.grid(row=i // 3, column=i % 3, padx=10, pady=10)


# Function for the button click event
def on_button_click():
    channel_string = entry.get()
    # Scrape video titles using Beautiful Soup
    channel_id = get_channel_id(channel_string)

    channel_url = f'https://www.youtube.com/c/{channel_string}/videos'
    if channel_id:
        bs_video_titles = scrape_videos_with_bs(channel_url)[0]
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

    notebook = ttk.Notebook(root)
    notebook.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

    # Create tabs
    tab_titles = ['Beautiful Soup', 'YouTube API', 'Thumbnails']
    bs_tab = ttk.Frame(notebook)
    api_tab = ttk.Frame(notebook)
    thumbnails_tab = ttk.Frame(notebook)

    notebook.add(bs_tab, text='Beautiful Soup')
    notebook.add(api_tab, text='YouTube API')
    notebook.add(thumbnails_tab, text='Thumbnails')

    # Text widget for Beautiful Soup result
    bs_result_text = tk.Text(bs_tab, height=10, width=40)
    bs_result_text.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

    # Text widget for YouTube API result
    api_result_text = tk.Text(api_tab, height=10, width=40)
    api_result_text.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

    # Frame for displaying thumbnails
    thumbnails_frame = ttk.Frame(thumbnails_tab)
    thumbnails_frame.grid(row=0, column=0, padx=10, pady=10)

    # Start the Tkinter event loop
    root.mainloop()
