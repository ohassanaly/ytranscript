# app.py
import streamlit as st

from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()
# ----------------------------
# Streamlit page config
# ----------------------------

st.set_page_config(page_title="C3AI YouTube Channel Recommender", page_icon="🎥", layout="wide")
st.title("🎥 C3AI YouTube Channel Recommendation")
st.image("data/logo.png", width=600)
st.caption("Ask a question and get the recommended C3AI videos")

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
        placeholder="Paste any extra context here",
        height=220,
    )

with col2:
    k = st.number_input("Number of videos recommended", min_value=1, max_value=5, value=3, step=1)

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
        context_blocks.append(f"[video {i}] {content}\nURL: {url}".strip())

    context = "\n\n---\n\n".join(context_blocks)

    print(context) #logging

    prompt = f"""Answer the question using the following provided videos.

Question: {combined_query}

Context:
{context}

Instructions:
- Base your answer ONLY on the provided Context.
- If the Context is insufficient, say what’s missing and ask a follow-up question.
- Provide a short actionable learning plan referencing the videos by number.
"""

    with st.spinner("Generating answer..."):
        answer = llm.invoke(prompt).content

    # ----------------------------
    # Display results
    # ----------------------------
    st.subheader("✅ Answer")
    st.write(answer)

    st.subheader("📌 Recommended videos")
    for i, d in enumerate(docs, 1):
        url = d.metadata.get("url", "")
        title = d.metadata.get("title") or f"Video {i}"
        snippet = (d.page_content or "").strip()

        with st.expander(f"{i}. {title}", expanded=True):
            if url:
                st.markdown(f"[Open video]({url})")
            if snippet:
                st.write(snippet)
