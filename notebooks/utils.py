from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    filename="transcript_api.log",
    filemode="a",  # append
)

logger = logging.getLogger(__name__)

def get_youtube_video_id(url: str) -> str | None:
    parsed = urlparse(url)

    # youtu.be/<id>
    if parsed.netloc in ("youtu.be", "www.youtu.be"):
        return parsed.path.lstrip("/")

    # youtube.com/*
    if "youtube.com" in parsed.netloc:
        # watch?v=<id>
        if parsed.path == "/watch":
            return parse_qs(parsed.query).get("v", [None])[0]

        # /embed/<id>, /shorts/<id>
        parts = parsed.path.split("/")
        if len(parts) >= 3 and parts[1] in {"embed", "shorts"}:
            return parts[2]

    return None

def retrieve_video_transcript(video_url:str) -> str:
    video_id = get_youtube_video_id(video_url)
    ytt_api = YouTubeTranscriptApi()
    full_text=""
    try : 
        fetched_transcript = ytt_api.fetch(video_id)
    except Exception as e:
        logger.error(
            "Failed to fetch transcript for video_url=%s: %s",
            video_url,
            e
        )
        return("")
    for snippet in fetched_transcript.snippets:
        full_text+= snippet.text + " "
    return(full_text)