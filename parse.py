import datetime
import warnings

import pandas as pd

from get_album import parse_unknown_taylor_albums

CSV_FILE_NAME = 'Apple Music Play Activity.csv'
CONTAINER_FILE_NAME = 'Apple Music - Container Details.csv'
ALBUM_COLUMN = 'Album Name'
PLAY_DURATION_COLUMN = 'Play Duration Milliseconds'
SONG_COLUMN = 'Song Name'
DATE_COLUMN = 'Event End Timestamp'

ALL_COLUMNS = [v for k, v in list(locals().items()) if k.endswith('_COLUMN')]

# Hyper-parameters
INSUFFICIENT_DURATION_MILLIS = 10000
DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%f%z'
START_DATE = datetime.datetime(
    2023, 1, 1, 0, 0, 0).astimezone(datetime.timezone.utc)


def get_artist(album: str) -> str:
    """
    Returns the artist for a given album, based on a partial match in CONTAINER_FILE_NAME
    """
    df = pd.read_csv(CONTAINER_FILE_NAME)
    df = df.dropna(how='any', subset=['Container Description'])
    df = df[df['Container Description'].str.contains(album, regex=False)]

    if len(df) == 0:
        artist = parse_unknown_taylor_albums(album)
        if len(artist) == 0:
            print(album)
        return pprint_artists(artist)

    return pprint_artists(tuple(df['Artists'].values[0].split(', ')))


def pprint_artists(artists: tuple) -> str:
    """
    Pretty prints a tuple of artists
    """
    if len(artists) == 0:
        return 'Unknown'
    
    if len(artists) > 3:
        return ', '.join(artists[:3]) + ', ...'

    return ', '.join(artists)


if __name__ == '__main__':
    warnings.filterwarnings('ignore')
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
    df[ARTIST_COLUMN] = df[ALBUM_COLUMN].apply(get_artist)

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