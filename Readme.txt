Playlist YouTube Downloader
----------------------------
Reads a playlist text file, searches YouTube for each track,
and downloads it as an MP3 using yt-dlp.

Usage:
    python download_playlist.py

Requirements:
    pip install yt-dlp

Output:
    ./downloads/  — one MP3 per track
    ./failed.txt  — any tracks that couldn't be found/downloaded
"""