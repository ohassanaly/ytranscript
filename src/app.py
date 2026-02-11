import streamlit as st
from utils import retrieve_channel_items, generate_vector_store, fast_rag
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

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

st.set_page_config(page_title="YouTube Video Summarizer", page_icon="data/yt_logo.png")

st.header("YouTube channel explorer", text_alignment="center")

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.image("data/yt_logo.png", width=300)

channel_handle = st.text_input("Which YouTube channel are you intersted in?", value="@")

run = st.button("Get YT channel videos", type="primary", use_container_width=True)

if run:
    try : 
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
    vectorstore = get_vectorstore(videos) #cached in RAM with st.cache_resource
    llm = load_llm()

    #RAG Interface
    user_text = st.text_input(
    "Ask any question to get video recommendations",
    placeholder="e.g., What are the latest AI agentic advances?",
    )
    run2 = st.button("Recommend videos", type="primary", use_container_width=True)
    if run2:
        if user_text:
            with st.spinner("Searching videos..."):
                answer = fast_rag(vectorstore, llm, user_text)
                st.markdown(answer)
        else: 
            st.warning("Please enter a question first.")



