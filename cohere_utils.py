import cohere
from dotenv import dotenv_values
import uuid
import hnswlib
from typing import List, Dict
from sentence_transformers import SentenceTransformer
# from gpt4all import Embed4All

config = dotenv_values(".env")
cohere_api = config['COHERE_API_KEY']
co = cohere.Client(cohere_api)

class Vectorstore:
    def __init__(self, raw_documents: List[Dict]):
        self.raw_documents = raw_documents
        self.chunk_words = 150
        self.docs = []
        self.docs_embs = []
        self.retrieve_top_k = 10
        self.rerank_top_k = 5
        self.load_and_chunk()
        self.embed()
        self.index()

    def load_and_chunk(self) -> None:
        """
        Loads the text from the sources and chunks the HTML content.
        """
        print("Loading documents...")
        # Check if the documents are from web scraping or local PDF file(s)
        if 'file' not in self.raw_documents[0]:
            for raw_document in self.raw_documents:
                # Split the content into words
                words = raw_document['scrapped_text'].split()
                # Group the words into chunks of 150
                chunks = [' '.join(words[i : min(i + self.chunk_words, len(words))]) for i in range(0, len(words), self.chunk_words)]
                for chunk in chunks:
                    self.docs.append(
                        {
                            "title": raw_document["title"],
                            "text": str(chunk),
                            "url": raw_document["URL"],
                        }
                    )
        # consider the case for local PDF file(s), returned by load_local()
        else:
            for raw_document in self.raw_documents:
                # Split the content into words
                words = raw_document['text'].split()
                # Group the words into chunks of 150
                chunks = [' '.join(words[i : min(i + self.chunk_words, len(words))]) for i in range(0, len(words), self.chunk_words)]
                for chunk in chunks:
                    self.docs.append(
                        {
                            "file": raw_document["file"],
                            "text": str(chunk),
                            "page": raw_document["page"],
                        }
                    )

    def embed(self) -> None:
        """
        Embeds the document chunks using the Cohere API.
        """
        print("Embedding document chunks...")

        self.docs_len = len(self.docs)
        print(f"Total document chunks: {self.docs_len}")
        # batch_size = 90
        # for i in range(0, self.docs_len, batch_size):
        #     batch = self.docs[i : min(i + batch_size, self.docs_len)]
        #     texts = [item["text"] for item in batch]
        #     docs_embs_batch = co.embed(
        #         texts=texts, model="embed-multilingual-v3.0", input_type="search_document"
        #     ).embeddings
        #     self.docs_embs.extend(docs_embs_batch)
        #     print(f"Embedding {len(docs_embs_batch)} document chunks.")

        # embedder = Embed4All()
        # self.tokens_processed = 0
        # for doc in self.docs:
        #     output = embedder.embed([doc['text']], long_text_mode="mean", return_dict=True)
        #     self.docs_embs.extend(output["embeddings"])
        #     self.tokens_processed += output["n_prompt_tokens"]
        #     print(f"Embedding {output['n_prompt_tokens']} characters.")        
        # print(f"Total tokens (characters) processed: {self.tokens_processed}")

        # Use SentenceTransformer for embedding
        # Known issue: can't read one-page PDF files due to the retriever from hnswlib
        self.embedder = SentenceTransformer('sentence-transformers/all-MiniLM-L12-v2')
        for doc in self.docs:
            doc_emb = self.embedder.encode(doc['text'])
            # doc_emb_list = doc_emb.tolist()  # Convert array to list
            self.docs_embs.append(doc_emb)

    def index(self) -> None:
        """
        Indexes the documents for efficient retrieval.
        """
        # print("Indexing documents...")

        # Determine the dimensionality of the embeddings, which is 384 for the GPT4All model
        dim = len(self.docs_embs[0])        

        self.idx = hnswlib.Index(space="ip", dim=dim)       # dynamic dimensionality
        self.idx.init_index(max_elements=self.docs_len, ef_construction=512, M=64)    # tricky parameters... 
        self.idx.add_items(self.docs_embs, list(range(len(self.docs_embs))))

        # It's also recommended to adjust the ef parameter for query time
        self.idx.set_ef(max(self.retrieve_top_k, 400))  # Setting ef to at least the number of top_k results you want or higher for better accuracy
        print(f"Indexing complete with {self.idx.get_current_count()} documents.")

    def retrieve(self, query: str) -> List[Dict[str, str]]:
        """
        Retrieves document chunks based on the given query.

        Parameters:
        query (str): The query to retrieve document chunks for.

        Returns:
        List[Dict[str, str]]: A list of dictionaries representing the retrieved document chunks, with 'title', 'text', and 'url' keys.
        """
        # Dense retrieval
        query_emb = co.embed(
            texts=[query], model="embed-english-v3.0", input_type="search_query"
        ).embeddings
        # query_emb = self.embedder.encode(query)

        doc_ids = self.idx.knn_query(query_emb, k=self.retrieve_top_k)[0][0]
        print(doc_ids)

        # Reranking
        docs_to_rerank = [self.docs[doc_id]["text"] for doc_id in doc_ids]

        rerank_results = co.rerank(
            query=query,
            documents=docs_to_rerank,
            top_n=self.rerank_top_k,
            model="rerank-english-v2.0",
        )
       
        # These two lines were revised to extract the indices of the rerank_results
        results = [item for item in rerank_results if item[0] == 'results'][0][1]

        # Extract the indices
        doc_ids_reranked = [doc_ids[result.index] for result in results]

        docs_retrieved = []

        # Check if the documents are from web scraping or local PDF file(s)
        if 'file' not in self.raw_documents[0]:
            for doc_id in doc_ids_reranked:
                docs_retrieved.append(
                    {
                        "title": self.docs[doc_id]["title"],
                        "text": self.docs[doc_id]["text"],
                        "url": self.docs[doc_id]["url"],
                    }
                )
        # consider the case for local PDF file(s)
        else:
            for doc_id in doc_ids_reranked:
                docs_retrieved.append(
                    {
                        "file": self.docs[doc_id]["file"],
                        "text": self.docs[doc_id]["text"],
                        "page": self.docs[doc_id]["page"],
                    }
                )
        print(f"Docs retrieved: {docs_retrieved}")
        return docs_retrieved

def annotate_citations(text: str, citations: list[dict], datasource: str):
    """
    A helper function to pretty print citations.
    """
    annotated_ls = list()
    last_end = 0    # Initialize the end of the last citation as 0
    id_offset = 4 if datasource == "Static News" or datasource == "Local File" else 11

    # Process citations in the order they were provided
    for citation in citations:
        start, end = citation.start, citation.end 
        cited_docs = [doc_id[id_offset:] for doc_id in citation.document_ids]
        
        # Shorten citations if they're too long for convenience
        if len(cited_docs) > 3:
            placeholder = "[" + ", ".join(cited_docs[:3]) + "...]"
        else:
            placeholder = "[" + ", ".join(cited_docs) + "]"
        
        # Modify the text to include the citation
        highlight = f'{text[start:end]}', f'{placeholder}', '#eeeeee'
        
        # Append the annotated text to the list
        annotated_ls.append(text[last_end:start])
        # Append the highlighted text
        annotated_ls.append(highlight)
        # Update the end of the last citation
        last_end = end
        
    # Append any remaining text after the last citation
    annotated_ls.append(text[last_end:])

    return annotated_ls