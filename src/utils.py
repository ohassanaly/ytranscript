import logging
import os
import re

from googleapiclient.discovery import build
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from youtube_transcript_api import YouTubeTranscriptApi

logging.basicConfig(
    filename="logs/errors.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def retrieve_channel_items(channel_handle: str):
    """Given a YT channel handlen retrieves its stats and videos"""
    youtube = build("youtube", "v3", developerKey=os.getenv("YOUTUBE_API_KEY"))

    # Step 1: Get the channel’s Uploads playlist ID
    request = youtube.channels().list(
        part="contentDetails,statistics",
        forHandle=channel_handle,
    )
    response = request.execute()
    uploads_playlist_id = response["items"][0]["contentDetails"]["relatedPlaylists"][
        "uploads"
    ]

    # bonus get the channel statistics
    statistics = response["items"][0]["statistics"]

    # Step 2: List videos from the uploads playlist
    videos = []

    request = youtube.playlistItems().list(
        part="contentDetails,snippet", playlistId=uploads_playlist_id, maxResults=50
    )

    while request:
        response = request.execute()

        for item in response["items"]:
            title = item["snippet"]["title"]
            video_id = item["snippet"]["resourceId"]["videoId"]
            url = f"https://www.youtube.com/watch?v={video_id}"

            videos.append({"title": title, "url": url})

        request = youtube.playlistItems().list_next(request, response)

    return (statistics, videos)


def generate_vector_store(data):
    """Generates a FAISS vector store given based on a list of videos titles"""
    title_list = [item["title"] for item in data]
    url_list = [item["url"] for item in data]
    metadatas = [{"url": url} for url in url_list]

    embeddings = OpenAIEmbeddings()

    vectorstore = FAISS.from_texts(title_list, embeddings, metadatas=metadatas)

    return vectorstore


def fast_rag(vectorstore, llm, user_query, n_videos=10):
    """Performs similairity search with the vector store and analyzes the result providing an answer"""
    docs = vectorstore.similarity_search(user_query, k=n_videos)
    context_blocks = []
    for i, d in enumerate(docs, 1):
        url = d.metadata.get("url", "")
        content = (d.page_content or "").strip()
        context_blocks.append(f"[video {i}] {content}: {url}".strip())

    context = "\n\n---\n\n".join(context_blocks)

    prompt = f"""Answer the following question using the provided videos from the YouTube channel
    Instructions:
    - Base your answer ONLY on the provided YouTube channel videos.
    - If some videos are not relevant with user question, don't talk about its. 
    - Provide URL for each relevant video

    Question: {user_query}

    YouTube channel videos:
    {context}
    """
    answer = llm.invoke(prompt).content
    return (docs, answer)


def retrieve_video_transcript(url_or_id: str):
    """Extracts video ID and fetches the transcript as a single string."""
    # Extract video ID from URL if necessary
    video_id = url_or_id
    if "youtube.com" in url_or_id or "youtu.be" in url_or_id:
        match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url_or_id)
        if match:
            video_id = match.group(1)

    try:
        full_transcript = ""
        ytt_api = YouTubeTranscriptApi()
        transcript_list = ytt_api.list(video_id)
        try:
            transcript = transcript_list.find_transcript(["en"])
        except Exception:
            logging.info(
                "No english transcript available ; looking for other languages "
            )
            transcript = next(iter(transcript_list))  # .translate("en")
            # the translate feature seems to trigger the YT IP block ; so we rather keep the video in its native language and rely on the LLM model to translate the source transcript
        fetched_transcript = transcript.fetch()
        for snippet in fetched_transcript.snippets:
            full_transcript += snippet.text + " "
        return full_transcript
    except Exception as e:
        logging.exception(f"Error fetching transcript for video ID: {video_id} ; {e}")
        raise Exception(
            f"Captions are disabled or unavailable for this video ({video_id})."
        ) from e
