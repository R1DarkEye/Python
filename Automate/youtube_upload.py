import os
import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow

# Authenticate and construct the YouTube service
def get_authenticated_service():
    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secret_']
    )
    credentials = flow.run_local_server(port=8080)

    return build('youtube', 'v3', credentials=credentials)

def check_video_uploaded(video_name, log_file='uploaded_videos.txt'):
    """Check if the video has been uploaded by checking the log file."""
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            uploaded_videos = f.read().splitlines()
        if video_name in uploaded_videos:
            return True
    return False

def log_uploaded_video(video_name, log_file='uploaded_videos.txt'):
    """Log the uploaded video name to the log file."""
    with open(log_file, 'a') as f:
        f.write(video_name + '\n')

def upload_video(service, file, title, description, category_id, keywords):
    """Upload the video to YouTube."""
    request = service.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": keywords,
                "categoryId": category_id
            },
            "status": {
                "privacyStatus": "public"  # Can be 'public', 'private', 'unlisted'
            }
        },
        media_body=MediaFileUpload(file, chunksize=-1, resumable=True)
    )
    response = request.execute()
    print(f"Video uploaded with ID: {response['id']}")

def get_video_and_caption(video_folder, video_file):
    """Get the video file and its corresponding title and description."""
    # Get the corresponding text file (same name as the video, but .txt extension)
    text_file = video_file.replace('.mp4', '.txt')
    
    title = ""
    description = ""
    
    if os.path.exists(os.path.join(video_folder, text_file)):
        with open(os.path.join(video_folder, text_file), 'r', encoding='utf-8') as file:
            lines = file.readlines()
            
            if lines:
                # Assuming the first line is the title, and the rest are part of the description
                title = lines[0].strip()  # First line is the title
                description = "Follow EpicShark for more inspiring and motivational content. Stay tuned for daily uplifting videos that fuel your passion and keep you moving forward.#quotes #denzelwashington #denzelwashingtonquotes #quoteoftheday #dailymotivation #successtips #successquotes #dailyquotes #motivations #quotesaboutlife #motivationalquotes #quotesaboutlife #motivationdaily #insprationalquote #motivativationalspeaker #inspirational #lovequotes #lifelessons #dailymotivation #motive #positivethoughts #motivationonmonday #quotesoftheday #motivated #quotestoliveby #lifequotes"  # Default description if empty
                if not description:
                    description = "\n".join(lines[1:]).strip()  # Rest of the file is the description
    else:
        print(f"Text file for {video_file} not found.")
        title = ""
        description = "Follow it  for more inspiring and motivational content. Stay tuned for daily uplifting videos that fuel your passion and keep you moving forward."

    # Ensure the title is not empty
    if not title.strip():
        title = f"Untitled Video - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    return title, description  # Return title and description

if __name__ == "__main__":
    # Define the folder containing videos and captions
    video_folder = 'videosFolder'

    # Authenticate to YouTube
    youtube_service = get_authenticated_service()

    # Track uploaded videos
    uploaded_videos_log = 'uploaded_videos.txt'

    # Get the list of video files and sort them by modification time (oldest first)
    video_files = [f for f in os.listdir(video_folder) if f.endswith('.mp4')]
    video_files.sort(key=lambda f: os.path.getmtime(os.path.join(video_folder, f)))

    # Counter for uploaded videos
    uploaded_count = 0
    max_uploads = 2  # Limit to 2 uploads in one run

    for video_file in video_files:
        # Check if the video has already been uploaded
        if check_video_uploaded(video_file, uploaded_videos_log):
            print(f"Skipping {video_file}, already uploaded.")
            continue

        video_path = os.path.join(video_folder, video_file)
        
        # Get the title and description for the current video
        title, description = get_video_and_caption(video_folder, video_file)

        # Upload the video
        video_category_id = '21'  # "People & Blogs"
        video_keywords = ['fitness', 'workout', 'exercise', 'health', 'gym', 'yoga','motivatation','motivated']  # Empty keywords

        upload_video(youtube_service, video_path, title, description, video_category_id, video_keywords)
        
        # Log the uploaded video
        log_uploaded_video(video_file, uploaded_videos_log)

        # Increment the uploaded video count
        uploaded_count += 1
        
        # Stop if 2 videos have been uploaded
        if uploaded_count >= max_uploads:
            print(f"Uploaded {uploaded_count} videos. Stopping execution.")
            break
