import os
import sys
import re

from dotenv import load_dotenv, find_dotenv
from pathlib import Path
from pytube import Playlist, YouTube
from moviepy.editor import *

# import environment vars
CURRENT_DIR = os.path.dirname(sys.argv[0])
find_dotenv(CURRENT_DIR)
load_dotenv()

# obtain save path from local env file
LOCAL_SAVE_PATH = Path(os.getenv("SAVE_PATH"))
AUDO_FILE_FORMAT = os.getenv("AUDO_FILE_FORMAT")
YOUTUBE_PLAYLIST_URL = os.getenv("YOUTUBE_PLAYLIST_URL")
YOUTUBE_VIDEO_URL = os.getenv("YOUTUBE_VIDEO_URL")

YOUTUBE_STREAM_AUDIO = "140"


def convert_to_audio(input_save_path, input_fileExt, del_video_file=True):
    """Converts videos in a given directory to a audio file (user files format)
    Deletes original video file by default"""

    if "." not in input_fileExt:
        input_fileExt = f".{input_fileExt}"  # reformat to check for extension ending in .

    # get existing files from dir with same file extension
    check_files = [x for x in os.listdir(input_save_path) if x.endswith(input_fileExt)]
    print(f"\n\tFound {len(check_files)} files matching the extension - {input_fileExt}")

    # get all audio .mp4 files
    video_files = [x for x in os.listdir(input_save_path) if x.endswith(".mp4")]
    video_files = [os.path.join(input_save_path, x) for x in video_files]

    # convert video files to audio using moviepy
    if video_files:
        for i, vid in enumerate(video_files):
            # TODO format file name as unicode prior to conversion

            print(f"\n{i+1}. Converting mp4 file - {vid}")
            # convert each file to an .mp3, then delete the .mp4 file
            mp4_name = os.path.basename(vid).split(".mp4")[0]
            mp3_path = os.path.join(input_save_path, f"{mp4_name}{input_fileExt}")
            mp4_to_mp3(vid, mp3_path)

            if del_video_file:
                os.remove(vid)
    else:
        print("\n\nFound no video files in directory...")
        print("\t\tRerun script to download YouTube videos")

    print("\n\nConverted all video files to audio")


def mp4_to_mp3(mp4, mp3):
    """MoviePy conversion function - convert a single file
    Credits:
    https://stackoverflow.com/questions/55081352/how-to-convert-mp4-to-mp3-using-python
    https://www.tutorialexample.com/a-complete-guide-to-python-convert-mp4-to-mp3-with-moviepy-python-tutorial/
    """

    # video = VideoFileClip(os.path.join("path","to","movie.mp4"))
    # video.audio.write_audiofile(os.path.join("path","to","movie_sound.mp3"))

    # mp4_without_frames = AudioFileClip(mp4)
    # mp4_without_frames.write_audiofile(mp3, codec="use_codec")
    # mp4_without_frames.close()

    videoclip = VideoFileClip(mp4)
    audioclip = videoclip.audio
    audioclip.write_audiofile(mp3)
    audioclip.close()
    videoclip.close()


def get_Youtube_Playlist(input_yt_url, input_save_path):
    """
    Downloads a playlist from a given URL to a local save path
    Define a final file extension for the resulting file(s).
    """

    print(f"\nSaving to local directory:\n\t\t{input_save_path}")

    # get a list of existing file names in dir
    files_existing = list(Path(input_save_path).glob("**/*"))
    file_names_existing = [os.path.basename(x).split(".")[0] for x in files_existing if x.is_file()]
    print(f"Existing files:\n\n{file_names_existing}")

    # create a pytube playlist object
    p = Playlist(input_yt_url)

    # this fixes the empty playlist.videos list
    p._video_regex = re.compile(r"\"url\":\"(/watch\?v=[\w-]*)")

    # print(f"Downloading: {p.title}")

    # loop through all containing videos and download
    for i, video in enumerate(p.videos):
        name = video.title

        # check if name of video already exists in the directory
        if name not in file_names_existing:
            print(f"\n\t{i + 1}. Downloading video - \t {name}")
            # found_streams = video.streams.filter(file_extension="mp4")
            # print(f"Found video streams:\n{found_streams}")
            st = video.streams.get_highest_resolution()
            # st.download(r'path')  `
            # audioStream = video.streams.get_by_itag(YOUTUBE_STREAM_AUDIO)
            st.download(output_path=input_save_path)

    print(f"\nDownloaded all videos from YouTube Playlist:\n\t{input_yt_url}")


def main():
    """ACQUIRE YT AUDIO
    1. Downloads a Youtube Playlist or Video using Pytube
    2. Saves to a local dir with a specified audio file format
        - Converts .wav to audio file using MoviePy
    """

    # TODO - rewrite using try/except
    print(f"Current working directory:\n\t {CURRENT_DIR}")

    if YOUTUBE_PLAYLIST_URL:
        # get_Youtube_Playlist(YOUTUBE_PLAYLIST_URL, LOCAL_SAVE_PATH)
        convert_to_audio(LOCAL_SAVE_PATH, AUDO_FILE_FORMAT)

    elif YOUTUBE_VIDEO_URL:
        print("Download YT video separately")
    else:
        print("\n\nERROR -- No URL provides for YouTube playlist or single video")
        print("\t\tComplete the `.env` file with the required variables. See `example.env` for instructions")


if __name__ == "__main__":
    main()
else:
    print("Executed when imported")
