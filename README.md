This project aims at exploring the content of a YouTube channel, using AI augmented capabilities.<br>

This project is divided into 3 steps : 

* Retrieving all the videos of a given YouTube channel.

* Performing intelligent search among those videos to focus on a specific content.

* Asking for a summary of the relevant videos retrieved.

# Retrieving all the videos of a given YouTube channel <br>
We use Google native [YouTube Data API](https://developers.google.com/youtube/v3/docs/channels/list) to retrieve all the videos titles and URLs from a given youTube channel. <br>
Nota : the channel is dentified using the the channel @handle<br>

#  Performing intelligent search among those videos to focus on a specific content <br>
Once all the video titles of the channel retrieved, we build a vector database of these video titles. This is done using [FAISS](https://pypi.org/project/faiss-cpu/), [OpenAI](https://platform.openai.com/docs/overview) as the embedding model, and [Langchain](https://www.langchain.com/) for plumbing.<br>

Based on a user query, a similarity search is performed. Top 10 relevant videos are retrieved, and then, another LLM analyzes the result and generates an answer. <br>

# Asking for a summary of the relevant videos retrieved <br>
It is possible to go further ; We can ask for a summary of the relevant retrieved videos validated by the LLM. To do so, we first retrieve the video transcript based on its URL using [youtube_transcript_api](https://pypi.org/project/youtube-transcript-api/).<br>

Then, we ask an LLM to summarize the transcript. <br>

__________________________

The main issue encountered at this point is YouTube blocking requests from my IP when doing too much requests. This is documented in the "Working around IP bans" section of [youtube_transcript_api](https://pypi.org/project/youtube-transcript-api/). The suggested solution  involves buying a proxy on [Webshare](https://www.webshare.io). <br>
 
On the technical level, cache management and logging were implemented. <br>