

import subprocess
import sys
import os
import re
import time

# ─── CONFIG ───────────────────────────────────────────────────────────────────
PLAYLIST_FILE = "My_Playlist__25__2_.txt"   # path to your playlist .txt
OUTPUT_DIR    = "downloads"                  # folder where MP3s are saved
FAILED_LOG    = "failed.txt"                 # tracks that failed
SLEEP_BETWEEN = 1.5                          # seconds between downloads (be polite)
AUDIO_FORMAT  = "mp3"                        # output audio format
AUDIO_QUALITY = "192"                        # kbps
#

def clean_title(line: str) -> str:
    """Strip leading track numbers and whitespace from a playlist line."""
    # Remove leading "123\t" or "123 " numbering
    line = re.sub(r"^\s*\d+[\t\s]+", "", line)
    return line.strip()


def load_tracks(filepath: str) -> list[str]:
    """Load and deduplicate tracks from the playlist file."""
    if not os.path.exists(filepath):
        print(f"[ERROR] Playlist file not found: {filepath}")
        sys.exit(1)

    with open(filepath, encoding="utf-8") as f:
        lines = f.readlines()

    tracks = []
    seen   = set()
    for line in lines:
        title = clean_title(line)
        if not title:
            continue
        key = title.lower()
        if key not in seen:
            seen.add(key)
            tracks.append(title)

    return tracks


def download_track(query: str, output_dir: str) -> bool:
   
    # ytsearch1: searches YouTube and picks the top result
    search_url = f"ytsearch1:{query}"

    cmd = [
        "yt-dlp",
        "--no-playlist",
        "--extract-audio",
        "--audio-format", AUDIO_FORMAT,
        "--audio-quality", AUDIO_QUALITY,
        # Save as:  Artist - Title.mp3
        "-o", os.path.join(output_dir, "%(uploader)s - %(title)s.%(ext)s"),
        # Embed metadata and thumbnail
        "--embed-metadata",
        "--embed-thumbnail",
        # Quiet but show errors
        "--quiet",
        "--no-warnings",
        search_url,
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            return True
        else:
            # Print yt-dlp's error so user knows why it failed
            err = result.stderr.strip()
            if err:
                print(f"   yt-dlp error: {err[:200]}")
            return False
    except subprocess.TimeoutExpired:
        print("   [TIMEOUT] Skipping — took too long.")
        return False
    except Exception as e:
        print(f"   [EXCEPTION] {e}")
        return False


def main():
    tracks = load_tracks(PLAYLIST_FILE)
    total  = len(tracks)
    print(f"Loaded {total} unique tracks from '{PLAYLIST_FILE}'")
    print(f"Saving MP3s to  ./{OUTPUT_DIR}/\n")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    failed  = []
    success = 0

    for i, track in enumerate(tracks, 1):
        print(f"[{i:>3}/{total}] {track}")
        ok = download_track(track, OUTPUT_DIR)
        if ok:
            success += 1
            print(f"         ✓ downloaded")
        else:
            failed.append(track)
            print(f"         ✗ FAILED")
        time.sleep(SLEEP_BETWEEN)

    # ── Summary ──────────────────────────────────────────────────────────────
    print(f"\n{'─'*50}")
    print(f"Done!  {success}/{total} tracks downloaded successfully.")

    if failed:
        print(f"       {len(failed)} tracks failed — saved to '{FAILED_LOG}'")
        with open(FAILED_LOG, "w", encoding="utf-8") as f:
            f.write("\n".join(failed) + "\n")
        print(f"\nFailed tracks:")
        for t in failed:
            print(f"  • {t}")
    else:
        print("All tracks downloaded successfully!")


if __name__ == "__main__":
    main()