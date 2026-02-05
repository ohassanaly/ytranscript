# app.py
import streamlit as st

from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()
# ----------------------------
# Streamlit page config
# ----------------------------

st.set_page_config(page_title="C3AI YT Recommendations", page_icon="data/yt_logo.png", layout="wide")

st.header("C3AI YouTube Recommendations", text_alignment="center")

col1, col2 = st.columns(2)
with col1:
    st.image("data/logo.png")

with col2:
    st.image("data/yt_logo.png")

st.subheader("Ask a question and get the recommended videos from C3AI YouTube channel",
             text_alignment="center")

# ----------------------------
# Caching: load embeddings + FAISS once
# ----------------------------
@st.cache_resource(show_spinner=False)
def load_vectorstore():
    embeddings = OpenAIEmbeddings()  # uses OPENAI_API_KEY from env or Streamlit secrets
    vs = FAISS.load_local(
        "data/c3ai_youtube_index",
        embeddings,
        allow_dangerous_deserialization=True,
    )
    return vs

@st.cache_resource(show_spinner=False)
def load_llm():
    return ChatOpenAI(model="gpt-4o-mini", temperature=0)

vectorstore = load_vectorstore()
llm = load_llm()

# ----------------------------
# UI controls
# ----------------------------
col1, col2 = st.columns([3, 1])
with col1:
    user_text = st.text_input(
        "What do you want to learn about C3AI?",
        placeholder="e.g., What are the latest agentic advances from C3AI?",
    )

    extra_content = st.text_area(
        "Extra content (optional)",
        placeholder="(Optional) Paste any extra context here",
        height=220,
    )

with col2:
    k = st.number_input("Number of videos recommended", min_value=1, max_value=10, value=3, step=1)

run = st.button("Recommend videos", type="primary", use_container_width=True)

# ----------------------------
# Run retrieval + generation
# ----------------------------
if run:
    if not user_text.strip():
        st.warning("Please type a question first.")
        st.stop()

    if extra_content.strip():
        combined_query = f"""User question:
        {user_text}
        Here is extra context relating with the question:
        {extra_content}
        """
    else:
        combined_query = user_text

    with st.spinner("Searching videos..."):
        docs = vectorstore.similarity_search(combined_query, k=int(k))

    if not docs:
        st.info("No videos found for that query.")
        print("no video found for that query")
        st.stop()          
            
    # Build context safely (avoid quote issues)
    context_blocks = []
    for i, d in enumerate(docs, 1):
        url = d.metadata.get("url", "")
        content = (d.page_content or "").strip()
        context_blocks.append(f"[video {i}] {content}: {url}".strip())

    context = "\n\n---\n\n".join(context_blocks)

    print(context) #logging

    prompt = f"""Answer the following question using the provided videos from C3AI company YouTube channel.
    Instructions:
- Base your answer ONLY on the provided C3AI YouTube channel videos.
- Say if some videos are not relevant with user question. Proivde URLs and video number for each relevant video

Question: {combined_query}

C3AI YouTube channel videos:
{context}


"""

    with st.spinner("Generating answer..."):
        answer = llm.invoke(prompt).content
        print(prompt)

    # ----------------------------
    # Display results
    # ----------------------------
    st.subheader("✅ Answer")
    st.write(answer)

    st.subheader("📌 Top-result videos")
    for i, d in enumerate(docs, 1):
        url = d.metadata.get("url", "")
        title = d.page_content
        snippet = (d.page_content or "").strip()

        with st.expander(f"Video {i} : {title}", expanded=False):
            if url:
                st.markdown(f"[Open video]({url})")
            if snippet:
                st.write(snippet)
