# We need a dedicated module to guessing the album, because Apple can't fucking give it to us. The best
# way to do this would be through an API, but that's not factored in yet; this is pretty brute-force right now.
import os
import pickle
import sys
from typing import List

import requests

with open('.env', 'r') as f:
    line = f.readline()
    API_KEY = line.split('=')[1].strip()


CACHE_FILE_NAME = '.lastfm_cache'
CACHE_HIT = 0
CACHE_MISS = 1


def parse_unknown_album(album: str) -> List:
    cache = {}
    if os.path.exists(CACHE_FILE_NAME):
        with open(CACHE_FILE_NAME, 'rb') as f:
            cache = pickle.load(f)

    # It's likely TS. This minimizes API requests.
    if '(Taylor\'s Version)' in album or \
        'Taylor’s Version' in album or \
        'long pond studio' in album.lower() or \
        '1989' in album or \
        'reputation' in album or \
        'Midnights' in album or \
        album == 'The More Lover Chapter - EP':
        return [('Taylor Swift',), CACHE_HIT]
    
    if album in cache:
        return [(cache[album]['results']['albummatches']['album'][0]['artist'],), CACHE_HIT]

    response = requests.get(f'http://ws.audioscrobbler.com/2.0/?method=album.search&album={album}&api_key={API_KEY}&format=json')
    data = response.json()
    cache[album] = data

    # Write back to cache
    with open(CACHE_FILE_NAME, 'wb') as f:
        pickle.dump(cache, f)

    try:
        return [(data['results']['albummatches']['album'][0]['artist'],), CACHE_MISS]
    except KeyError as e:
        # We've failed. Sigh.
        print(e.with_traceback(), file=sys.stderr)
        return [(), CACHE_MISS]
