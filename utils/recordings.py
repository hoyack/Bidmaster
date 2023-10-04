import argparse
from pydub import AudioSegment
import requests
import io


def download_mp3(url):
    """Download an MP3 file from a given URL and return an AudioSegment."""
    response = requests.get(url)
    response.raise_for_status()
    return AudioSegment.from_mp3(io.BytesIO(response.content))

def main():
    parser = argparse.ArgumentParser(description='Chain MP3 files together.')
    parser.add_argument('--input', required=True, help='Path to the text file containing MP3 URLs.')
    parser.add_argument('--output', required=True, help='Path to save the combined MP3 file.')
    parser.add_argument('--delay', type=int, default=3, help='Delay in seconds to add between files.')
    args = parser.parse_args()

    # Read URLs from the input file
    with open(args.input, 'r') as f:
        urls = [line.strip() for line in f]

    # Download and concatenate audio
    combined_audio = AudioSegment.empty()
    for url in urls:
        print(f"Downloading {url}...")
        audio = download_mp3(url)
        combined_audio += audio + AudioSegment.silent(duration=args.delay * 1000)  # delay is multiplied by 1000 to convert to milliseconds

    # Remove the last added delay
    if len(urls) > 0:
        combined_audio = combined_audio[:-args.delay * 1000]

    # Save the combined audio
    combined_audio.export(args.output, format="mp3")
    print(f"Saved combined audio to {args.output}")

if __name__ == "__main__":
    main()
