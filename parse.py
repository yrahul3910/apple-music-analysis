import argparse
import datetime
import warnings

import pandas as pd

from get_album import CACHE_HIT, get_album_cached

CSV_FILE_NAME = 'Apple Music - Play History Daily Tracks.csv'
PLAY_DURATION_COLUMN = 'Play Duration Milliseconds'
SONG_COLUMN = 'Track Description'
DATE_COLUMN = 'Date Played'

ALL_COLUMNS = [v for k, v in list(locals().items()) if k.endswith('_COLUMN')]

# Hyper-parameters
INSUFFICIENT_DURATION_MILLIS = 10000
DATE_FORMAT = '%Y%m%d'
START_DATE = datetime.datetime(
    2023, 1, 1, 0, 0, 0)

# Cache stats
cache_hits = 0
cache_misses = 0


def get_title(track: str) -> str:
    '''
    Returns the title of a track, without the artist
    '''
    if '-' not in track:
        return track

    return ' - '.join(track.split(' - ')[1:]).strip()


def get_artist(track: str) -> str:
    '''
    Returns the artist for a given track
    '''
    return track.split(' - ')[0].strip()


def get_album(track: str) -> str:
    global cache_hits, cache_misses

    album, cache_status = get_album_cached(track)
        
    if cache_status == CACHE_HIT:
        cache_hits += 1
    else:
        cache_misses += 1

    return album


if __name__ == '__main__':
    warnings.filterwarnings('ignore')

    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    df = pd.read_csv(CSV_FILE_NAME)

    # Filter columns of interest
    df = df[ALL_COLUMNS]

    # Remove columns where there is no data in any of the columns
    df = df.dropna(how='any')

    # Remove rows where the date is before the start date
    df[DATE_COLUMN] = pd.to_datetime(df[DATE_COLUMN], format=DATE_FORMAT)
    df = df[df[DATE_COLUMN] > START_DATE]

    # Remove rows where the play duration is less than 10 seconds
    df = df[df[PLAY_DURATION_COLUMN] > INSUFFICIENT_DURATION_MILLIS]

    # Add in the artist column
    ARTIST_COLUMN = 'Artist'
    df[ARTIST_COLUMN] = df[SONG_COLUMN].apply(get_artist)

    # Add in the album column
    ALBUM_COLUMN = 'Album'
    df[ALBUM_COLUMN] = df[SONG_COLUMN].apply(get_album)

    # Remove artist from the track name
    df[SONG_COLUMN] = df[SONG_COLUMN].apply(get_title)

    print('Songs played: ', len(df))
    print('Last date: ', df[DATE_COLUMN].max().strftime('%Y-%m-%d'))

    # Get total play time
    total_play_time = df[PLAY_DURATION_COLUMN].sum()
    print('Total play time (min): ', round(
        total_play_time / (1000 * 60), 1))
    print()

    # Find the top 5 artists by play time
    artist_play_time = df.groupby(ARTIST_COLUMN)[PLAY_DURATION_COLUMN].sum()
    artist_play_time = artist_play_time.sort_values(ascending=False)
    top_artists_df = pd.DataFrame({
        'Artist': artist_play_time.index,
        'Play Time (min)': (artist_play_time.values / (1000 * 60)).round(1),
        'Percentage': (artist_play_time.values / total_play_time * 100).round(1)
    }).head(5)
    print('Top 5 artists by play time:')
    print(top_artists_df)
    print()

    # Get Taylor Swift play time
    y = artist_play_time['Taylor Swift'] / 60000
    z = total_play_time / 60000
    k = 0.9
    # Minutes needed to hit 90% of Taylor Swift play time: (kz - y) / (1 - k)
    print('Minutes needed to hit 90% of Taylor Swift play time: ', round((k * z - y) / (1 - k), 1))
    print()

    # Find the top 5 albums by play time
    album_play_time = df.groupby([ARTIST_COLUMN, ALBUM_COLUMN])[
        PLAY_DURATION_COLUMN].sum()
    album_play_time = album_play_time.sort_values(ascending=False)
    top_albums_df = pd.DataFrame({
        'Artist': album_play_time.index.get_level_values(ARTIST_COLUMN),
        'Album': album_play_time.index.get_level_values(ALBUM_COLUMN),
        'Play Time (h)': (album_play_time.values / (1000 * 60 * 60)).round(1)
    }).head(5)
    print('Top 5 albums by play time:')
    print(top_albums_df)
    print()

    # Find the top 10 songs by play time, and show album name
    song_play_time = df.groupby([ARTIST_COLUMN, ALBUM_COLUMN, SONG_COLUMN])[
        PLAY_DURATION_COLUMN].sum()
    song_play_time = song_play_time.sort_values(ascending=False)
    top_songs_df = pd.DataFrame({
        'Artist': song_play_time.index.get_level_values(ARTIST_COLUMN),
        'Album': song_play_time.index.get_level_values(ALBUM_COLUMN),
        'Song': song_play_time.index.get_level_values(SONG_COLUMN),
        'Play Time (min)': (song_play_time.values / (1000 * 60)).round(1)
    }).head(10)
    print('Top 10 songs by play time:')
    print(top_songs_df)

    if args.debug:
        print()
        print('Cache hit%:', round(cache_hits / (cache_hits + cache_misses) * 100, 1))
