# We need a dedicated module to guessing the album, because Apple can't fucking give it to us. The best
# way to do this would be through an API, but that's not factored in yet; this is pretty brute-force right now.
import os
import pickle
import sys
import json
import requests
from typing import List, Union

from thefuzz import fuzz

with open('.env', 'r') as f:
    line = f.readline()
    API_KEY = line.split('=')[1].strip()


CACHE_FILE_NAME = '.lastfm_cache'
CACHE_HIT = 0
CACHE_MISS = 1


def find_matching_album(track, albums) -> Union[str, None]:
    best_similarity = 0
    best_match = None

    for album in albums.keys():
        similarity = fuzz.token_set_ratio(track, album)
        if similarity > best_similarity:
            best_similarity = similarity
            best_match = album

    if best_similarity >= 80:
        return albums[best_match]
    else:
        return None



def parse_taylor_track(track: str) -> Union[str, None]:
    with open('albums.json', 'r') as f:
        albums = json.load(f)
    
    if track in albums:
        return albums[track]
    
    # If `track` matches any of `albums` keys by 80% or more, return that album
    most_matched_album = find_matching_album(track, albums)
    if most_matched_album is not None:
        return most_matched_album
    
    return None


def normalize_ts_albums(track: str, album: str) -> str:
    if 'Taylor Swift' not in track:
        return album
    
    if 'Midnights' in album:
        return 'Midnights (3am Edition)'
    
    if 'Red' in album:
        return 'Red (Taylor\'s Version)'
    
    if 'Speak Now' in album:
        return 'Speak Now (Taylor\'s Version)'
    
    return album


def get_album_cached(track: str) -> List[str]:
    # Handle Taylor Swift tracks
    if 'Taylor Swift' in track:
        parsed = parse_taylor_track(track.split(' - ')[1].strip())
        if parsed is not None:
            return [parsed, CACHE_HIT]

    cache = {}
    if os.path.exists(CACHE_FILE_NAME):
        with open(CACHE_FILE_NAME, 'rb') as f:
            cache = pickle.load(f)
    
    if track in cache:
        if 'error' in cache[track]:
            return ['Unknown', CACHE_HIT]
        if 'album' in cache[track]['track']:
            return [normalize_ts_albums(track, cache[track]['track']['album']['title']), CACHE_HIT]

    splits = track.split(' - ')
    artist = splits[0].strip()

    if '&' in artist:
        artist = artist.split('&')[0].strip()

    title = ' - '.join(splits[1:]).strip()
    if '(Taylor\'s Version)' in title:
        title = title.split('(Taylor\'s Version)')[0].strip()

    if '&' in title:
        title = title.replace('&', 'and')

    response = requests.get(f'http://ws.audioscrobbler.com/2.0/?method=track.getInfo&track={title}&artist={artist}&api_key={API_KEY}&format=json')
    data = response.json()
    cache[track] = data

    # Write back to cache
    with open(CACHE_FILE_NAME, 'wb') as f:
        pickle.dump(cache, f)

    try:
        if 'error' in data:
            print(track, data)
            return ['Unknown', CACHE_MISS]
        if 'album' in data['track']:
            return [normalize_ts_albums(track, data['track']['album']['title']), CACHE_MISS]
        else:
            return ['Single', CACHE_MISS]
    except KeyError as e:
        print(track, data)
        # We've failed. Sigh.
        print('Error: ', e, file=sys.stderr)
        return ['Unknown', CACHE_MISS]
