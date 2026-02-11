from googleapiclient.discovery import build
from dotenv import load_dotenv
import os

def retrieve_channel_items(channel_handle:str):
    
    load_dotenv()
    youtube = build("youtube", "v3", developerKey=os.getenv("YOUTUBE_API_KEY"))
    
    #Step 1: Get the channel’s Uploads playlist ID
    request = youtube.channels().list(
        part="contentDetails,statistics",
        forHandle=channel_handle,
        )
    response = request.execute()
    uploads_playlist_id = response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    
    #bonus get the channel statistics
    statistics = response['items'][0]['statistics']
    
    #Step 2: List videos from the uploads playlist
    videos = []
    
    request = youtube.playlistItems().list(
        part="contentDetails,snippet",
        playlistId=uploads_playlist_id,
        maxResults=50
    )
    
    while request:
        response = request.execute()
    
        for item in response["items"]:
            title = item["snippet"]["title"]
            video_id = item["snippet"]["resourceId"]["videoId"]
            url = f"https://www.youtube.com/watch?v={video_id}"
    
            videos.append({"title": title, "url": url})
    
        request = youtube.playlistItems().list_next(request, response)
    
    return(statistics, videos)