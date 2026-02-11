import streamlit as st
from utils import retrieve_channel_items
import os

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
            stats, videos = retrieve_channel_items(channel_handle)

            st.text(f"Total #views on the {channel_handle} channel : {stats["viewCount"]}")
            st.text(f"Total #videos on the {channel_handle} channel : {len(videos)}")
            st.table(videos)

    except Exception as e:
        st.info("Please check the channel handle you provided")
        print(e)