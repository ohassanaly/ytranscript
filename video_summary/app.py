import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from utils import retrieve_video_transcript, count_tokens

load_dotenv()

st.set_page_config(page_title="YouTube Video Summarizer", page_icon="data/yt_logo.png")

st.header("YouTube Video summarizer", text_alignment="center")

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.image("data/yt_logo.png", width=300)

st.caption("Save time ; Paste any YouTube video URL and get the summary of this video")

video_url = st.text_input(
    "Paste a YouTube URL",
    placeholder="https://www.youtube.com/watch?v=xxxxxxxx",
)

col1, col2 = st.columns([1, 3])
with col1:
    run = st.button("Summarize", type="primary")

if run:
    if not video_url.strip():
        st.error("Please paste a YouTube URL first.")
        st.stop()

    try:
        with st.spinner("Fetching transcript..."):
            transcript = retrieve_video_transcript(video_url)

        if not transcript or not transcript.strip():
            st.warning("The video transcript could not be extracted. Check if the video has a transcript / if your IP is valid")
            st.stop()

        with st.expander("Show transcript"):
            st.code(transcript, language="text")

        with st.spinner("Summarizing..."):
            prompt = f"""Provide a concise, well-structured summary of the given video transcript.

Transcript:
{transcript}
"""
            #check we do not exceed the context window
            if count_tokens(prompt) >= 1e6:
                st.info("The text transcript length exceeds the model context window")
            print(count_tokens(prompt))

            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0) #1M max token context window
            answer = llm.invoke(prompt).content

        st.subheader("Summary")
        st.write(answer)

    except Exception as e:
        st.error(f"Please re-launch the application ; Something went wrong: {e}")