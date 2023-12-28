import tkinter as tk
import config
from googleapiclient.discovery import build

### Goals
### 1. Have functionality to go to a youtube channel and get Title, thumbnail, retention time, rating, description, captions, and viewcount
### 2. Build a UI to get this information for a given youtube channel
### 3. Put it into a downloadable repository
### 4. Make it a downloadable exe for anyone to use on desktop


if __name__ == '__main__':
    api_key = config.api_key
    MainWindow = tk.Tk()
    print("Hello World!")
