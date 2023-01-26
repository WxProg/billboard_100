from bs4 import BeautifulSoup
import requests
import spotipy
import os
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

# ---------------------- BILLBOARD 100 WEB SCRAPPING --------------------------- #

date = input('Which year do you want to travel to? Enter the date in this format YYYY-MM-DD:\n')
year = date.split('-')[0]

WEBSITE_URL = f"https://www.billboard.com/charts/hot-100/{date}/"

response = requests.get(WEBSITE_URL)
website_html = response.text

soup = BeautifulSoup(website_html, 'html.parser')

song_tags = soup.find_all('h3', class_='a-no-trucate')
song_names = [song.get_text().strip("\n\t") for song in song_tags]

# ------------------------------- SPOTIPY SET UP -------------------------------------- #

# SPOTIFY AUTHENTICATION
load_dotenv(".env")
SP_CLIENT_ID = os.getenv("SP_CLIENT_ID")
SP_CLIENT_SECRET = os.getenv("SP_CLIENT_SECRET")

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SP_CLIENT_ID,
                                               client_secret=SP_CLIENT_SECRET,
                                               redirect_uri="http://example.com",
                                               show_dialog=True,
                                               cache_path="token.txt",
                                               scope="playlist-modify-private"))
user_id = sp.current_user()["id"]

# LOCATING SONG ON SPOTIFY
songs_uris = []

for song in song_names:
    results = sp.search(q=f"track:{song}", type="track")
    try:
        each_URIs = results['tracks']['items'][0]['uri']
        songs_uris.append(each_URIs)
    except IndexError:
        print(f"{song}, is not in listed on Spotify. It was skipped.")

# CREATING A PRIVATE PLAYLIST
billBoard_playlist = sp.user_playlist_create(user=user_id,
                                             name=f"Year:{year}\nBillboard 100 ",
                                             public=False,
                                             description=f"A playlist of Billboard's Hot 100 for the year {year}")

# ADDING TO THE PLAYLIST
sp.playlist_add_items(playlist_id=billBoard_playlist['id'], items=songs_uris)
