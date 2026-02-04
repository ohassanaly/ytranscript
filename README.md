This project aims at building a recommendation system for C3AI's YouTube channel. <br>
Based on a user query and some optional extra context, a RAG system first performs the retrieval. The videos result are then fed to an LLM who analyzes the results, and provide an answer with the possibility to later click on videos URLs.<br>

The webapp is based on [Streamlit](https://streamlit.io/).<br>

The RAG uses [FAISS](https://pypi.org/project/faiss-cpu/) for vector databse indexing, [openai](https://platform.openai.com/docs/overview) for embedding and augmented generation and [langchain](https://www.langchain.com/) for plumbing.<br>

The YT channel video content was retrieved using Google native [YouTube Data API](https://developers.google.com/youtube/v3/docs/channels/list)

To run the app, active the venv, go into app_demo folder and run 
`uv run streamlit run app.py`