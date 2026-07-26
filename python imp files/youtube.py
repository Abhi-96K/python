from yt_dlp import YoutubeDL

def download_youtube_video(url, output_path='.'):
    try:
        ydl_opts = {
            'outtmpl': f'{output_path}/%(title)s.%(ext)s',  # Save file as video title
            'format': 'best',  # Download the best quality available
        }

        with YoutubeDL(ydl_opts) as ydl:
            print(f"Downloading: {url}...")
            ydl.download([url])
            print("Download completed!")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    video_url = input("Enter the YouTube video URL: ")
    output_path = input("Enter the output path (or press Enter for current directory): ")

    download_youtube_video(video_url, output_path if output_path else '.')