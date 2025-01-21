# News Scraping App 🚀

Welcome to **NISA** (“News Insight Scraping App”) — a sleek, powerful, and AI-driven tool for searching, analysing, and visualising the latest news! ✨ Built for enthusiasts, researchers, and anyone who wants to make sense of the news with ease and efficiency.

## Why NISA?

Have you ever found yourself:
- Drowning in a sea of news articles? …or
- Wishing for a smarter way to extract insights from them? 🤔

**NISA** is here to save the day! From lightning-fast searches to powerful analytics, this app lets you:

- **Search smarter** with Google Custom Search JSON API
- **Summarise news** with cutting-edge NLP techniques (HuggingFace Transformers)
- **Analyse sentiment** (Textblob) 😊/😒
- **Discover topics** through interactive visualisations (Gensim + pyLDAvis) 🎨

## Key Features 🔍

1. **Streamlined UI** – Built with [Streamlit](https://streamlit.io/) for a modern and intuitive user experience.
2. **Google-Powered Search** – Integrates the Google Custom Search JSON API to fetch accurate and relevant news articles.
3. **Supercharged with AI** – Employs **FastEmbed**, an open-source high-performance embedding model, for semantic understanding.
4. **State-of-the-Art Storage** – Utilises **Qdrant** for efficient and scalable vector storage.
5. **Enhanced RAG Techniques** – Implements Retrieval Augmented Generation (RAG) with advanced techniques like:
   - Hybrid Search
   - Vector Semantic Search
   - PDF Table Extraction 🔢
6. **Cloud-Optimised** – Deployed using Azure Web App Service to handle high traffic and concurrent users effortlessly.

## Behind the Scenes ⚙️

### 1. **Tech Stack**
- **Frontend**: Streamlit
- **Backend**: FastEmbed (open-source embedding model), Cohere (LLM), Qdrant (vector database)
- **Search API**: Google Custom Search JSON API
- **NLP Magic**: HuggingFace Transformers, TextBlob, Gensim
- **Cloud**: Azure Web App Service

### 2. **RAG Mastery**
- Compared different RAG techniques to find the best-performing model.
- Strategically chose the optimal LLM after testing various options (Cohere, OpenAI, and open-source models).
- See the technical diagram of the advanced RAG system below (migrated from LlamaIndex to Cohere with its reranker) 
![image](https://github.com/user-attachments/assets/50a8dd20-7cd2-4861-b18e-c45952aa85ff)

### 3. **Advanced Visualisation**
- Integrated interactive graphs to explore:
  - Sentiment trends ⬆️⬇️
  - Topic distributions 🔬
  - Keyword extractions ✨

### 4. **Cloud Scaling**
- Worked with Azure experts to optimise deployment for production-level performance and security.
- Evaluated multiple vector database options (Azure AI Search, Qdrant, Singlestore) for scalability and data protection.

## How It Works 💡

1. **Search for News**
   - Input a topic or keywords and let the Google-powered search do its magic. ⚡
2. **Semantic Analysis**
   - Use FastEmbed to cluster and retrieve the most contextually relevant articles.
3. **Dive Deeper**
   - Summarise, analyse sentiments, or uncover hidden topics.
4. **Visualise It**
   - Enjoy interactive dashboards powered by Streamlit!

## How to Run Locally 🌄

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/nisa.git
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your Google Custom Search JSON API key and Qdrant connection in `.env`.
4. Run the app:
   ```bash
   streamlit run app.py
   ```
5. 🎉 That’s it! Open the app in your browser and start exploring!

## Sneak Peek 📸

Here’s a little preview of what the app looks like (screenshots below):

---

Built with ❤️ by Daniel Wong 👷‍♂️. Feel free to fork, contribute, or just enjoy the app! Feedback is always welcome. ✉️



Check it out at: https://newsscraping.streamlit.app/ 

## Screenshots:

![image](https://github.com/user-attachments/assets/092a9be5-5b97-400e-86de-af284d209b47)
![image](https://github.com/user-attachments/assets/b525ac72-402a-4df7-b4ce-c2962bf2005e)
![image](https://github.com/user-attachments/assets/5a18adc9-b56c-421b-8d8c-3c3ffc2d5adb)
![image](https://github.com/user-attachments/assets/cbac5ebd-6faf-488b-b65c-5ed5adcefd13)



