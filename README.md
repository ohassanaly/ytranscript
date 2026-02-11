This project aims at building tools for intelligent processing of YouTube videos. <br>

# Recommendation system for C3AI's YouTube channel. <br>

folder channel_recommendation <br>
Based on a user query and some optional extra context, the webapp first performs the retrieval of the top videos matching the input query. In addition to the user query, the most relevant retrieved videos are then fed to an LLM, who analyzes the results, and provide an answer with the possibility to later click on videos URLs.<br>

The webapp is based on [Streamlit](https://streamlit.io/).<br>

The RAG uses [FAISS](https://pypi.org/project/faiss-cpu/) for vector databse indexing, [openai](https://platform.openai.com/docs/overview) for embedding and augmented generation and [langchain](https://www.langchain.com/) for plumbing.<br>

The YT channel video content was retrieved using Google native [YouTube Data API](https://developers.google.com/youtube/v3/docs/channels/list)

To run the app, active the venv, go into channel_recommendation folder and run 
`uv run streamlit run app.py`<br>

# YouTube video summarizer

folder video_summary<br>
Given any YouTube video URL (with a transcript available), this webapp first retrieves the text transcript using [youtube_transcript_api](https://pypi.org/project/youtube-transcript-api/)<br>

Then, we ask an LLM to summarize the result. <br>

Later improvements include :
- Cache management for aleady processed YouTube videos
- Proper Logging management
- managing IP adress restrictions for instance using [Webshare](https://www.webshare.io)