import os
import spotipy
import requests
import config
from datetime import datetime
from bs4 import BeautifulSoup
from spotipy.oauth2 import SpotifyOAuth
from collections import Counter

os.environ['SPOTIPY_CLIENT_ID'] = config.SPOTIFY_CLIENT_ID
os.environ['SPOTIPY_CLIENT_SECRET'] = config.SPOTIFY_CLIENT_SECRET
os.environ['SPOTIPY_REDIRECT_URI'] = config.SPOTIFY_REDIRECT_URI

songs = []
main_url = 'https://www.rmfmaxxx.pl/muzyka/playlista/'

for i in reversed(range(0, 24)):
    url = main_url + str(i)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    songs_list = soup.find('div', {'class': 'list-songs'})

    for div_tag in songs_list.find_all('div', {'class': 'pi'}):
        # Extracting title
        title = div_tag.find('a', {'class': 'is-title'}).text

        # Extracting artists
        artists = []
        artists_div = div_tag.find('div', {'class': 'is-artist'})
        for artist_a in artists_div.find_all('a'):
            artists.append(artist_a.text)

        if artists:
            songs.append(title + ' ' + artists[0])

print('Scraped {} songs from {}'.format(len(songs), main_url))

scope = 'playlist-modify-public'
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

spotify_song_ids = []
most_popular_songs = [key for key, value in Counter(songs).most_common()]

for song in most_popular_songs:
    results = sp.search(q=song, limit=1)
    if results['tracks']['total'] > 0:
        spotify_song_id = results['tracks']['items'][0]['id']
        spotify_song_ids.append(spotify_song_id)

n_of_songs = config.NUMBER_OF_SONGS
most_popular_song_ids = spotify_song_ids[:n_of_songs]

user_id = sp.me()['id']

playlist_name = 'RMF Maxxx Top {} {}'.format(len(most_popular_song_ids), datetime.today().strftime('%d-%m-%Y'))
playlist_description = 'Created using https://github.com/kartonixon/rmfmaxxx-to-spotify'
playlist_public = True

sp.user_playlist_create(user_id, playlist_name, playlist_public, False, playlist_description)
print('Playlist created!')

playlists = sp.current_user_playlists()
target_playlist_id = playlists['items'][0]['id']

sp.playlist_add_items(target_playlist_id, most_popular_song_ids)

print('Success! {} songs added to '.format(len(most_popular_song_ids)) + playlist_name)
