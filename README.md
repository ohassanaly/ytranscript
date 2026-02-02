This project aims at providing a solution to retrieve transcripts for youtube videos. This text transcript will later be used for intelligent processing such as classic NLP, RAG, or synthesis.

Idea : 
if video transcript available :
    retrieve the video transcript using [youtube_transcript_api](https://pypi.org/project/youtube-transcript-api/)
else:
    download the audio video locally using [yt-dlp](https://github.com/yt-dlp/yt-dlp) and extract the transcript using [openAI whisper](https://github.com/openai/whisper)