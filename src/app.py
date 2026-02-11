import logging
import re

import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from utils import (
    fast_rag,
    generate_vector_store,
    retrieve_channel_items,
    retrieve_video_transcript,
)

logging.basicConfig(
    filename="logs/app.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

load_dotenv()


@st.cache_data(persist="disk", show_spinner=False)
def get_cached_channel_data(handle):
    return retrieve_channel_items(handle)


@st.cache_resource
def get_vectorstore(videos):
    return generate_vector_store(videos)


@st.cache_resource(show_spinner=False)
def load_llm():
    return ChatOpenAI(model="gpt-4o-mini", temperature=0)


if "channel_loaded" not in st.session_state:
    st.session_state.channel_loaded = False

if "answer_generated" not in st.session_state:
    st.session_state.answer_generated = False

st.set_page_config(page_title="YouTube Channel Explorer", page_icon="data/yt_logo.png")

st.header("YouTube channel explorer", text_alignment="center")

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.image("data/yt_logo.png", width=300)

channel_handle = st.text_input(
    "Which YouTube channel are you interested in?", value="@"
)

run = st.button("Get YT channel videos", type="primary", use_container_width=True)

if run:
    logging.info(f"Channel Handle : {channel_handle}")
    try:
        with st.spinner(f"Retrieving {channel_handle} channel data"):
            stats, videos = get_cached_channel_data(channel_handle)
            _ = get_vectorstore(videos)
            st.session_state.channel_loaded = True
            st.session_state.channel_handle = channel_handle

    except Exception as e:
        st.info("Please check the channel handle you provided")
        print(e)

if st.session_state.channel_loaded:
    stats, videos = get_cached_channel_data(st.session_state.channel_handle)
    st.divider()
    col_a, col_b = st.columns(2)
    col_a.metric("Total #Views", f"{int(stats['viewCount']):,}")
    col_b.metric("Total #Videos", len(videos))
    vectorstore = get_vectorstore(videos)  # cached in RAM with st.cache_resource
    llm = load_llm()

    # RAG Interface
    user_text = st.text_input(
        "Ask any question to get video recommendations",
        placeholder="e.g., What are the latest AI agentic advances?",
    )
    run2 = st.button("Recommend videos", type="primary", use_container_width=True)
    if run2:
        if user_text:
            logging.info(f"Asked video recommendation : {user_text}")
            with st.spinner(
                "Searching for relevant videos and Analyzing the results..."
            ):
                docs, answer = fast_rag(vectorstore, llm, user_text)
                st.session_state.answer = answer
                st.session_state.docs = docs
                st.session_state.answer_generated = True
        else:
            st.warning("Please enter a question first.")

if st.session_state.channel_loaded & st.session_state.answer_generated:
    st.markdown(st.session_state.answer)
    logging.info(f"Video recommendation generated: {st.session_state.answer}")

    # 1. Extract the specific URLs the LLM actually wrote in its answer
    recommended_urls = re.findall(
        r"https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+", st.session_state.answer
    )

    video_options = {
        d.page_content: d.metadata["url"]
        for d in st.session_state.docs
        if d.metadata["url"] in recommended_urls
    }

    st.divider()
    st.subheader("Video summary")

    if video_options:
        selected_title = st.selectbox("Choose a video", list(video_options.keys()))

        if st.button("Get Detailed Summary", use_container_width=True):
            target_url = video_options[selected_title]
            logging.info(
                f"Summary asked for the video : {selected_title}, url : {target_url}"
            )
            with st.spinner(f"Summarizing the video {selected_title}"):
                try:
                    transcript = retrieve_video_transcript(target_url)
                    logging.info(f"Video transcript: {transcript}")
                    # LLM call for summary
                    res = llm.invoke(f"Summarize this video transcript: {transcript}")
                    st.info(f"**Detailed Summary: {selected_title}**")
                    st.markdown(res.content)
                    logging.info(f"Video summary: {res.content}")
                except Exception as e:
                    st.error(f"Error: {e}")
    else:
        st.write("No specific videos were recommended for this query.")
