import pytube


def display_streams(streams):
    """Display available video streams"""
    print("Available video streams:")
    for i, stream in enumerate(streams):
        print(f"{i + 1}. {stream.resolution} - {stream.mime_type} - {stream.filesize_approx / (1024 * 1024):.2f} MB")


def sanitize_filename(filename):
    """Sanitize filename to remove invalid characters"""
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename


def download_video(video_url, file_name, quality):
    """Downloads the video"""
    try:
        youtube = pytube.YouTube(video_url)
        streams = youtube.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc()
        
        if quality > len(streams) or quality < 1:
            print("Invalid quality selection.")
            return
        
        selected_stream = streams[quality - 1]
        
        # Sanitize the video title
        sanitized_title = sanitize_filename(youtube.title)
        file_name = sanitized_title + '.mp4'
        
        selected_stream.download(filename=file_name)
        print(f'Video downloaded: {file_name}')
    except Exception as e:
        print(f'Error downloading video: {e}')


def main():
    """Main function"""
    video_url = input('Enter the YouTube video URL: ')
    
    try:
        youtube = pytube.YouTube(video_url)
        title = youtube.title
        file_name = title + '.mp4'
        
        # Fetch available streams and display them
        streams = youtube.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc()
        display_streams(streams)
        
        quality = int(input("Select the video quality (Enter the number):\n"))
        
        download_video(video_url, file_name, quality)
    except Exception as e:
        print(f'Error getting video information: {e}')


if __name__ == '__main__':
    main()
