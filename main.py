#! /usr/bin/python3

import configparser
import sys
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth

from rofi import Rofi


def get_script_path():
    script_path = os.path.dirname(os.path.realpath(__file__))
    return script_path


def load_config():
    config = configparser.ConfigParser()
    config.read(os.path.join(get_script_path(), 'config.ini'))
    return config


def add_current_music_to_playlist(sp, playlist, music):
    should_add_to_playlist = True

    playlist_id = playlist['id']
    playlist_name = playlist['name']

    limit_counter = 0
    while True:
        playlist_musics = sp.playlist_tracks(
            playlist_id, limit=100, offset=limit_counter)
        limit_counter = limit_counter + 100
        if len(playlist_musics['items']) > 0:
            for idx, item in enumerate(playlist_musics['items']):
                if music["id"] == item['track']['id']:
                    should_add_to_playlist = False
                    break
        else:
            break

    if should_add_to_playlist:
        sp.playlist_add_items(playlist_id, [music["id"]])
        return "{} adicionada a {}".format(music["name"], playlist_name)
    else:
        return "{} já está na playlist {}".format(music["name"], playlist_name)


def main():
    config = load_config()
    r = Rofi()
    CLIENT_ID = config['AUTH']['CLIENT_ID']
    CLIENT_SECRET = config['AUTH']['CLIENT_SECRET']
    REDIRECT_URI = config['AUTH']['REDIRECT_URI']
    SCOPE = config['AUTH']['SCOPE']

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                                   client_secret=CLIENT_SECRET,
                                                   redirect_uri=REDIRECT_URI,
                                                   scope=SCOPE,
                                                   cache_path=os.path.join(get_script_path(), ".cache")))
    if len(sys.argv) < 2:
        r.status("Carregando playlists...")
        playlists_result = sp.current_user_playlists()
        playlists = []
        user_name = sp.current_user()['display_name']
        for i, item in enumerate(playlists_result['items']):
            if item['owner']['display_name'] == user_name or item['collaborative'] == True:
                playlists.append({"name": item["name"], "id": item["id"]})

        try:
            current_playing = sp.current_user_playing_track()

            music = {
                    "id": current_playing['item']['id'],
                    "name": current_playing['item']['name'],
                    "artist": current_playing['item']['artists'][0]['name']
                    }

            playlists_rofi = map(lambda playlist: playlist['name'], playlists)
            index, key = r.select(
                    'Adicionar música a', playlists_rofi, message="Tocando <b>" + music["name"] + " - " + music["artist"] + "</b>")

            if(key == 0):
                selected_playlist = playlists[index]
                r.status("Adicionando música...")
                result = add_current_music_to_playlist(sp, selected_playlist, music)
                r.error(result)

        except TypeError:
            return r.error("Nenhuma música tocando no momento")
        except Exception as error:
            r.error(error.args)
    else:
        playlists = sp.current_user_playlists()
        playlists_dict = {}
        playlist_input = sys.argv[1]

        selected_playlist = None

        for idx, item in enumerate(playlists['items']):
            if playlist_input == item['name']:
                selected_playlist = {"name": item["name"], "id": item["id"]}

        try:
            add_current_music_to_playlist(sp, selected_playlist)

        except ValueError:
            print("Necessário ser um número para prosseguir")


if __name__ == "__main__":
    main()
