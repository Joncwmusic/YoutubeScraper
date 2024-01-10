#### import image and UI libraries
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from io import BytesIO
import re
#### external files
import config

#### scraper and parser libraries
import requests
import bs4
import selenium as sl
import json

#### api lib
from googleapiclient.discovery import build


### Goals
### 1. Have functionality to go to a youtube channel and get Title, thumbnail, retention time, rating, description, captions, and viewcount
### 2. Build a UI to get this information for a given youtube channel
### 3. Put it into a downloadable repository
### 4. Make it a downloadable exe for anyone to use on desktop

api_key = config.api_key
youtube = build('youtube', 'v3', developerKey = api_key)


# class to make thumbnail grid within tkinter for a nice display
class ThumbnailGridApp(object):
    def __init__(self, master, image_paths):
        self.master = master
        self.image_paths = image_paths
        self.create_thumbnail_grid()

    def create_thumbnail_grid(self):
        row = 0
        col = 0

        for path in self.image_paths:
            thumbnail = self.load_thumbnail(path)
            thumbnail_label = tk.Label(self.master, image=thumbnail)
            thumbnail_label.grid(row=row, column=col, padx=5, pady=5)

            col += 1
            if col == 4:  # You can adjust the number of columns as needed
                col = 0
                row += 1

    def load_thumbnail(self, path):
        original_image = Image.open(path)
        # Resize the image to create a thumbnail
        thumbnail_size = (50, 50)
        thumbnail_image = original_image.resize(thumbnail_size, Image.ANTIALIAS)
        thumbnail = ImageTk.PhotoImage(thumbnail_image)
        return thumbnail


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


def scrape_videos_with_bs(channel_url):
    '''
    :param channel_url: url for the Youtube channel to scrape
    :return: a tuple with two lists. One containing the video thumbnail Urls and one containing the video titles
    '''
    response = requests.get(channel_url)
    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    pattern = re.compile(r'ytInitialData')

    # title and thumbnail array init
    video_titles = []
    video_thumbnails = []

    # search for a script tag within html using BS4
    script_tag = soup.find("script", string = pattern)
    json_text_from_channel = script_tag.string[script_tag.string.index('ytInitialData = ') + 16:len(script_tag.string)-1]


    if json_text_from_channel:
        # Extract the text content of the script tag
        script_content = script_tag

        # Parse the JSON data
        json_data_from_channel = json.loads(json_text_from_channel)
        # Navigate through the JSON structure to get the thumbnails
        # iterate over the index on contents with list comprehension
        video_thumbnails = [json_data_from_channel['contents']['twoColumnBrowseResultsRenderer'][
                          'tabs'][1]['tabRenderer']['content']['richGridRenderer']['contents'][
                          i]['richItemRenderer']['content']['videoRenderer'][
                          'thumbnail']['thumbnails'][3]['url'] for i in range(0, len(json_data_from_channel['contents']['twoColumnBrowseResultsRenderer']['tabs'][1]['tabRenderer']['content']['richGridRenderer']['contents'])-1)]

        video_titles = [json_data_from_channel['contents']['twoColumnBrowseResultsRenderer'][
                          'tabs'][1]['tabRenderer']['content']['richGridRenderer']['contents'][i]['richItemRenderer']['content'][
                'videoRenderer']['title']['runs'][0]['text'] for i in range(0, len(json_data_from_channel['contents']['twoColumnBrowseResultsRenderer']['tabs'][1]['tabRenderer']['content']['richGridRenderer']['contents'])-1)]

    return video_titles, video_thumbnails

# Function to retrieve video titles using YouTube API
def get_videos_with_api(channel_id):
    '''
    :param channel_id: channel id taken from the api search
    :return: video titles from the api call
    '''
    playlist_response = youtube.channels().list(
        part='contentDetails',
        id=channel_id
    ).execute()

    uploads_playlist_id = playlist_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    playlist_items = youtube.playlistItems().list(
        part='snippet',
        playlistId=uploads_playlist_id,
        maxResults=30  # Adjust as needed. Max is 50.
    ).execute()

    video_titles = [item['snippet']['title'] for item in playlist_items['items']]
    return video_titles

def get_images_from_url(image_url):
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    # img.thumbnail((100, 100))  # Resize thumbnail if needed
    return img

# Function for the button click event
def on_button_click():
    channel_string = entry.get()
    # Scrape video titles using Beautiful Soup
    channel_id = get_channel_id(channel_string)

    channel_url = f'https://www.youtube.com/c/{channel_string}/videos'
    if channel_id:
        bs_video_titles = scrape_videos_with_bs(channel_url)[0]
        bs_thumbnail_urls = scrape_videos_with_bs(channel_url)[1]

        bs_result_text.delete(1.0, tk.END)  # Clear existing content
        bs_result_text.insert(tk.END, '\n'.join(bs_video_titles))

        # Retrieve video titles using YouTube API
        api_video_titles = get_videos_with_api(channel_id)
        api_result_text.delete(1.0, tk.END)  # Clear existing content
        api_result_text.insert(tk.END, '\n'.join(api_video_titles))

        thumbnail_url_text.delete(1.0, tk.END)
        thumbnail_url_text.insert(tk.END, '\n'.join(bs_thumbnail_urls))

        # thumbnail_images = [tk.PhotoImage(,image = get_images_from_url(item)) for item in bs_thumbnail_urls]

    else:
        bs_result_text.delete(1.0, tk.END)
        bs_result_text.insert(tk.END, 'Channel not found')

        api_result_text.delete(1.0, tk.END)
        api_result_text.insert(tk.END, 'Channel not found')

        thumbnail_url_text.delete(1.0, tk.END)
        thumbnail_url_text.insert(tk.END, 'Channel not found')


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

    # notebook object is what contains the tab groups
    notebook = ttk.Notebook(root)
    notebook.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

    # Create tabs
    # tab_titles = ['Beautiful Soup', 'YouTube API', 'Thumbnails', 'Thumbnail URLs']
    bs_tab = ttk.Frame(notebook)
    api_tab = ttk.Frame(notebook)
    thumbnails_tab = ttk.Frame(notebook)
    thumbnail_urls = ttk.Frame(notebook)

    notebook.add(bs_tab, text='Beautiful Soup')
    notebook.add(api_tab, text='YouTube API')
    notebook.add(thumbnails_tab, text='Thumbnails')
    notebook.add(thumbnail_urls, text = 'Thumbnail URLs')

    # Text widget for Beautiful Soup result
    bs_result_text = tk.Text(bs_tab, height=10, width=40)
    bs_result_text.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

    # Text widget for YouTube API result
    api_result_text = tk.Text(api_tab, height=10, width=40)
    api_result_text.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

    # Text Widget for Thumbnail URLs
    thumbnail_url_text = tk.Text(thumbnail_urls, height=10, width= 40)
    thumbnail_url_text.grid(row = 3, column = 0, columnspan =  3, padx = 10, pady = 10)

    # Images from thumbnails
    # thumbnail_images = tk.PhotoImage(image = thumbnail_urls)
    # thumbnail_images = []
    # Display it within a label.
    # label = ttk.Label(image=thumbnail_images)
    # Frame for displaying thumbnails
    thumbnails_frame = ttk.Frame(thumbnails_tab)
    thumbnails_frame.grid(row=0, column=0, padx=10, pady=10)

    # Start the Tkinter event loop
    root.mainloop()

