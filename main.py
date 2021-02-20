#! /usr/bin/python3

import configparser
import sys
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth

from rofi import Rofi




def get_device_name(device):
    str_device = ""
    str_device += "✅" if device["is_active"] else "❌"
    str_device += "|" + ("🖥️" if device["type"] == "Computer" else "📱")
    str_device += " - " + device["name"]
    return str_device


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
        return "{} added to {}".format(music["name"], playlist_name)
    else:
        return "{} is already in {}".format(music["name"], playlist_name)


def rofi_add_current_music_to_playlist(r, sp):
    r.status("Loading your playlists...")
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
                'Add to', playlists_rofi, message="Playing <b>" + music["name"] + " - " + music["artist"] + "</b>")

        if(key == 0):
            selected_playlist = playlists[index]
            r.status("Adding...")
            result = add_current_music_to_playlist(sp, selected_playlist, music)
            r.error(result)

    except TypeError:
        return r.error("Nothing playing...")
    except Exception as error:
        r.error(error.args)


def rofi_select_device(r, sp):
    r.status("Loading your spotify devices...")
    try:
        devices_result = sp.devices()
        devices = []
        for i, device in enumerate(devices_result['devices']):
            print(device)
            devices.append({
                    "id": device["id"],
                    "name": device["name"],
                    "is_active": device["is_active"],
                    "type": device["type"]
                })


        devices_rofi = map(lambda device: get_device_name(device), devices)
        index, key = r.select("Select a device", devices_rofi)

        if (key == 0):
            selected_device = devices[index]
            r.status("Selecting device...")
            sp.transfer_playback(selected_device["id"])

    except Exception as error:
        r.error("Error when selecting device.")


def rofi_play_pause(r, sp):
    try:
        if (sp.current_playback()['is_playing']):
            sp.pause_playback()
        else:
            sp.start_playback()
    except Exception:
        r.error("Error while play/pause music")


def rofi_next_track(r, sp):
    try:
        sp.next_track()
    except Exception:
        r.error("Error next track")

def rofi_prev_track(r, sp):
    try:
        sp.previous_track()
    except Exception:
        r.error("Error previous track")


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

    sp_menu_options = ["1 - Play/Payse", "2 - Next", "3 - Previous", "4 - Select a Playback Device", "5 - Add Track to Playlist"]
    index, key = r.select("Spotify action", sp_menu_options, rofi_args=["-i"])
    if (key == 0): # Means that something was choosed
        if (index == 0):
            rofi_play_pause(r, sp)
        if (index == 1):
            rofi_next_track(r, sp)
        if (index == 2):
            rofi_prev_track(r, sp)
        if (index == 3):
            rofi_select_device(r, sp)
        if (index == 4):
            rofi_add_current_music_to_playlist(r, sp)


if __name__ == "__main__":
    main()
