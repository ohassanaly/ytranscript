from googleapiclient.discovery import build
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
import os

def retrieve_channel_items(channel_handle:str):
    
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

def generate_vector_store(data):

    title_list = [item["title"] for item in data]
    url_list = [item["url"] for item in data]
    metadatas = [{"url": url} for url in url_list]

    embeddings = OpenAIEmbeddings()

    vectorstore = FAISS.from_texts(title_list, embeddings, metadatas=metadatas)

    return(vectorstore)

def fast_rag(vectorstore, llm, user_query, n_videos=10):
    docs = vectorstore.similarity_search(user_query, k=n_videos)
    context_blocks = []
    for i, d in enumerate(docs, 1):
        url = d.metadata.get("url", "")
        content = (d.page_content or "").strip()
        context_blocks.append(f"[video {i}] {content}: {url}".strip())

    context = "\n\n---\n\n".join(context_blocks)

    print(context) #logging in terminal

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
    return(answer)