# Apple Music Data Analyzer

This repository contains code to analyze the data from Apple Music data requests.

Note: The `v1/` directory contains code for an older version of the Apple Music data, but is archived in case it proves useful later on. The files in the root directory are current.

**Updated 2024:** It seems like `v1/` is more accurate (or at least, closer to what Apple Music Replay provides). I don't know why the discrepancy exists, but if you're trying to get a specific metric (like your Taylor%) to some goal, you should probably keep use `v1/` to keep track.

## Requirements

* Python (this repo is tested on 3.11)
* Your Apple Music data in the same directory as this README.md file
    * Go to Apple's [Data and Privacy website](https://privacy.apple.com/) to get it.
    * Click on 'Request a copy of your data', and select 'Apple Media Services information'.
    * Unzip the contents. Navigate to `Apple_Media_Services` > Apple Music Activity and copy 'Apple Music - Play History Daily Tracks.csv' to this directory. For v1, copy 'Apple Music Play Activity.csv' and 'Apple Music - Container Details.csv'.
* A Last.fm API key. You can get one [here](https://www.last.fm/api/account/create).
    * I too wish this wasn't necessary. But the data from Apple Music is awful. We use this API to fetch the artists for the albums in your library.
    * Create a file called `.env` and add the following line to it: `API_KEY = <your API key>`

## Usage

Run `python3 parse.py` to get a summary of your Apple Music data.

## Features extracted

The following metrics are computed:

* Total number of songs played
* Total play time (in minutes)
* Top 5 artists by play time
* Top 5 albums by play time
* Top 10 songs by play time
