#! /usr/bin/python3
import configparser
import spotipy
from spotipy.oauth2 import SpotifyOAuth

def load_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config


def main():
    config = load_config()
    CLIENT_ID = config['AUTH']['CLIENT_ID']
    CLIENT_SECRET = config['AUTH']['CLIENT_SECRET']
    REDIRECT_URI = config['AUTH']['REDIRECT_URI']
    SCOPE = config['AUTH']['SCOPE']

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                                           client_secret=CLIENT_SECRET,
                                                           redirect_uri=REDIRECT_URI,
                                                           scope=SCOPE))
    playlists = sp.current_user_playlists()
    playlist_id = None
    playlist_name = None

    current_playing = sp.current_user_playing_track()
    music_id = current_playing['item']['id']
    music_name = current_playing['item']['name']

    should_add_to_playlist = True

    for idx, item in enumerate(playlists['items']):
        if item['name'] == "Punkson":
            playlist_id = item['id']
            playlist_name = item['name']

            # TODO: Precisa lembrar da paginação
            # results = 0
            # limit_counter = 0
            # while results is not None:
                # playlist_musics = sp.playlist_tracks(playlist_id, limit=limit_counter+100, offset=limit_counter)
                # if len(playlist_musics) > 0:
                    # for idx, item in enumerate(playlist_musics['items']):
                        # print(item['track']['name'])
                        # if music_id == item['track']['id']:
                            # should_add_to_playlist = False
                            # print("Já está na playlist")
                        # else:
                            # results = None
            break

    if should_add_to_playlist:
        sp.playlist_add_items(playlist_id, [music_id])

    print("{} adicionada a {}".format(music_name, playlist_name))


if __name__ == "__main__":
    main()
