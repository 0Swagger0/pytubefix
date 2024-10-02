from pytubefix import YouTube
import ssl
from pydub import AudioSegment
from flask import Flask, Response, send_file
import os

app = Flask(__name__)

# Disable SSL verification
ssl._create_default_https_context = ssl._create_unverified_context

# Directory where audio files will be stored
AUDIO_DIR = 'audio_files/'

# Ensure the audio directory exists
if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)

def download_and_convert_audio(youtube_id):
    """
    Download the audio from YouTube and convert it to MP3.
    Returns the file path of the MP3.
    """
    video_url = f'https://www.youtube.com/watch?v={youtube_id}'
    yt = YouTube(video_url)

    # Filter to get the first audio stream
    audio_stream = yt.streams.filter(only_audio=True).first()

    # Download the audio in its original format (webm/mp4)
    downloaded_file_path = audio_stream.download(output_path=AUDIO_DIR, filename=f'{youtube_id}.webm')

    # Convert to MP3
    mp3_file_path = os.path.join(AUDIO_DIR, f'{youtube_id}.mp3')

    # Convert only if the mp3 file doesn't already exist
    if not os.path.exists(mp3_file_path):
        audio = AudioSegment.from_file(downloaded_file_path)
        audio.export(mp3_file_path, format="mp3")

        # Optionally, remove the original downloaded file after conversion
        os.remove(downloaded_file_path)

    return mp3_file_path

@app.route('/stream/<youtube_id>')
def stream_audio(youtube_id):
    """
    Stream the MP3 audio for a given YouTube ID.
    If the MP3 doesn't exist, it will download, convert, and then stream.
    """
    # Path to the MP3 file
    mp3_file_path = os.path.join(AUDIO_DIR, f'{youtube_id}.mp3')

    # If the file doesn't exist, download and convert it
    if not os.path.exists(mp3_file_path):
        mp3_file_path = download_and_convert_audio(youtube_id)

    # Stream the MP3 file
    return send_file(mp3_file_path, mimetype='audio/mp3')

if __name__ == '__main__':
    app.run(debug=True,port=8000)

