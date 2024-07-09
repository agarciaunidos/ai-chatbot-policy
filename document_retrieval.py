
import streamlit as st
import pandas as pd
import pinecone
import time
import json 

# Consolidate imports from the same library
from langchain import hub
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_cohere import CohereRerank
from langchain.retrievers.contextual_compression import ContextualCompressionRetriever

# Import only necessary components
from langchain_pinecone import PineconeVectorStore
from langchain_core.messages import HumanMessage, AIMessage
from aws_secrets_initialization import PINECONE_API_KEY, INDEX_NAME, COHERE_API_KEY, FUNCTION_NAME, llm,embeddings,dynamodb_history,lambda_client

# Initialize services
retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")
documents_chain = create_stuff_documents_chain(llm, retrieval_qa_chat_prompt)
compressor = CohereRerank(top_n = 20,cohere_api_key = COHERE_API_KEY)


def generate_filter_conditions(selected_years, doc_types=None):
    """Creates and returns filter conditions based on selected years and document types."""
    conditions = {"year": {"$gte": selected_years[0], "$lte": selected_years[1]}}
    if doc_types and "ALL" not in doc_types:
        conditions["type"] = {"$in": doc_types}
    return conditions

def initialize_vector_store(index_name):
    """Sets up a Pinecone Vector Store for the given index name and returns it."""
    pinecone_client = pinecone.Pinecone(api_key=PINECONE_API_KEY)
    index = pinecone_client.Index(index_name)
    text_field = "text"
    vector_store = PineconeVectorStore(index, embeddings, text_field)
    return vector_store

def handle_query_retrieval(query, selected_years, doc_types):
    """Processes the user query, retrieves the information, and returns the answer along with sources."""
    id = st.session_state["id"]
    st_session_id = st.session_state["session_id"]
    user_id = st.session_state["user_id"]
    try:
        conditions = generate_filter_conditions(selected_years, doc_types)
        vector_store = initialize_vector_store(INDEX_NAME)
        base_retriever = vector_store.as_retriever(search_kwargs={'filter': conditions, 'k': 20})
        compression_retriever = ContextualCompressionRetriever(base_compressor=compressor, base_retriever=base_retriever)
        retrieval_chain = create_retrieval_chain(compression_retriever, documents_chain)
        filter_details = f"Applying filters: Years {selected_years[0]}-{selected_years[1]}, Types: {', '.join(doc_types) if doc_types else 'All types'}"
        response = retrieval_chain.invoke({"input": query, "filter": filter_details})
        sources_df = format_search_results_as_dataframe(response['context'])
        ai_sources = format_answer_sources(response['context'])
        ai_answer = response['answer']
        timestamp = int(time.time())
        dynamodb_history.add_user_message(HumanMessage(id=id, st_session_id = st_session_id, user_id = user_id,content=query,response_metadata={'timestamp': timestamp}))
        dynamodb_history.add_ai_message(AIMessage(id=id,st_session_id = st_session_id, user_id = user_id, content=ai_answer, 
                                                  response_metadata={'timestamp': timestamp,
                                                                     'source documents': ai_sources}))
        try:
            handle_prompt(id, st_session_id , user_id ,query)
        except Exception as e:
            print(f"Error: {e}")
        return ai_answer, sources_df
    except Exception as error:
        st.error(f"Error processing the query: {error}")
        return None, None

def handle_prompt(id, st_session_id , user_id ,content):

    payload = {
    "id": id,
    "st_session_id": st_session_id,
    "user_id": user_id,
    "content": content}

    response = lambda_client.invoke(
    FunctionName=FUNCTION_NAME,
    InvocationType='RequestResponse', 
    Payload=json.dumps(payload)
)

def format_search_results_as_dataframe(documents):
    """Converts search results into a pandas DataFrame for display."""
    results = []
    for document in documents:
        metadata = document.metadata
        title = metadata.get('title', '')
        page = metadata.get('page', '')
        source_url = metadata.get('source', '').replace('s3://', 'https://s3.amazonaws.com/')
        doc_type = metadata.get('type', '')
        year = metadata.get('year', '')
        relevance_score = metadata.get('relevance_score', '')
        porcentaje_relevance_score = relevance_score * 100
        if year:
            year = str(int(year))
        results.append({"Title": title, "Page": page, "Source": source_url, "Type": doc_type, "Year": year, "Relevance Score" : porcentaje_relevance_score})
    return pd.DataFrame(results)

def format_answer_sources(documents):
    """Converts search results into a formatted string for display."""
    results = []
    for document in documents:
        metadata = document.metadata
        title = metadata.get('title', '')
        source_url = metadata.get('source', '').replace('s3://', 'https://s3.amazonaws.com/')
        doc_type = metadata.get('type', '')
        year = metadata.get('year', '')
        if year:
            year = str(int(year))
        # Append each formatted line for the document
        results.append(f"Title: {title}, Source: {source_url}, Type: {doc_type}, Year: {year}")
    # Join all results into a single string with each entry on a new line
    return "\n".join(results)

