# Apple Music Data Analyzer

This repository contains code to analyze the data from Apple Music data requests.

## Requirements

* Python (this repo is tested on 3.11)
* Your Apple Music data in the same directory as this README.md file
    * Go to Apple's [Data and Privacy website](https://privacy.apple.com/) to get it.
    * Click on 'Request a copy of your data', and select 'Apple Media Services information'.
    * Unzip the contents. Navigate to `Apple_Media_Services` > Apple Music Activity and copy 'Apple Music Play Activity.csv' and 'Apple Music - Container Details.csv' to this directory.
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