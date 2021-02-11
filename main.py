#! /usr/bin/python3

import configparser
import sys
import spotipy
from spotipy.oauth2 import SpotifyOAuth


def load_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config


def add_current_music_to_playlist(sp, playlist):
    try:
        current_playing = sp.current_user_playing_track()

        music_id = current_playing['item']['id']
        music_name = current_playing['item']['name']
    except TypeError:
        print("Nenhuma música tocando no momento")
        return False

    should_add_to_playlist = True

    playlist_id = playlist['id']
    playlist_name = playlist['name']

    limit_counter = 0
    while True:
        playlist_musics = sp.playlist_tracks(playlist_id, limit=100, offset=limit_counter)
        limit_counter = limit_counter + 100
        if len(playlist_musics['items']) > 0:
            for idx, item in enumerate(playlist_musics['items']):
                if music_id == item['track']['id']:
                    should_add_to_playlist = False
                    break
        else:
            break

    if should_add_to_playlist:
        sp.playlist_add_items(playlist_id, [music_id])
        print("{} adicionada a {}".format(music_name, playlist_name))
        return True
    else:
        print("{} já está na playlist {}".format(music_name, playlist_name))
        return False


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

    if len(sys.argv) < 2:
        playlists = sp.current_user_playlists()
        playlists_dict = {}
        user_name = sp.current_user()['display_name']
        print("Suas playlists:")
        idx = 0
        for i, item in enumerate(playlists['items']):
            if item['owner']['display_name'] == user_name or item['collaborative'] == True:
                idx = idx+1
                print("{} - {}".format(idx, item["name"]))
                playlists_dict[idx] = {"name": item["name"], "id": item["id"]}

        try:
            selected_playlist_input = int(input("Digite o número da playlist: "))
            if selected_playlist_input == 0:
                print("Parando programa")
                sys.exit()
            selected_playlist = playlists_dict[selected_playlist_input]

            add_current_music_to_playlist(sp, selected_playlist)

        except ValueError:
            print("Necessário ser um número para prosseguir")
    else:
        playlists = sp.current_user_playlists()
        playlists_dict = {}
        playlist_input = sys.argv[1]

        selected_playlist = None

        for idx, item in enumerate(playlists['items']):
            if playlist_input ==  item['name']:
                selected_playlist = {"name": item["name"], "id": item["id"]}


        try:
            add_current_music_to_playlist(sp, selected_playlist)

        except ValueError:
            print("Necessário ser um número para prosseguir")




if __name__ == "__main__":
    main()
