This project aims at screening the content of a YouTube channel based on the transcritps of its videos. <br>

First, we use Google native [YouTube Data API](https://developers.google.com/youtube/v3/docs/channels/list) to retrieve all the videos titles and URLs from the channel. <br>
Nota : the channel can be identified using the channel ID, the channel handle, or the channel username.<br>

Second, we retrieve the transcript text of each video based on its URL.<br>

Idea : 
if there is a video transcript directly available in YouTube :<br>
    Retrieve the video transcript using [youtube_transcript_api](https://pypi.org/project/youtube-transcript-api/)<br>
    Nota : we face here some rate limiting problems.
else:<br>
    download the audio video locally using [yt-dlp](https://github.com/yt-dlp/yt-dlp) and extract the transcript using [openAI whisper](https://github.com/openai/whisper)<br>


Once we are able to retrieve all the video transcripts, we can build some intelligent processing such as classic NLP, RAG, or content synthesis.<br>

Ideas include : 
- a search engine to retrieve the relevant videos given some query
- a synthesis of the YouTube channel content ; to provide a great overview of it
- much more
