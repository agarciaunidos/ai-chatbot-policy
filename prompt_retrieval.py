import streamlit as st
import pinecone
import boto3
import json
from aws_secrets_initialization import pinecone_api_key, pinecone_index_name

# Initialize AWS Bedrock client
bedrock_client = boto3.client("bedrock-runtime", region_name='us-east-1')
# Initialize Pinecone
pc = pinecone.Pinecone(api_key=pinecone_api_key)
pinecone_index_name = 'uus-policy-prompts'
index = pc.Index(pinecone_index_name)
model_kwargs = {"dimensions": 256}

def get_embedding(text):
    response = bedrock_client.invoke_model(
        modelId="amazon.titan-embed-text-v2:0",
        contentType="application/json",
        accept="application/json",
        body=json.dumps({
            "inputText": text,
            "dimensions": 256
        })
    )
    embedding = json.loads(response['body'].read())['embedding']
    return embedding

def get_similar_prompts(query, k=5):
    query_embedding = get_embedding(query)
    results = index.query(vector=query_embedding, top_k=k, include_metadata=True)
    return [(match['metadata']['text'], match['score']) for match in results['matches']]

st.title("Similar Prompt Extractor")

query = st.text_input("Enter your prompt:")
k = st.slider("Number of similar prompts to retrieve:", min_value=1, max_value=10, value=5)

if st.button("Find Similar Prompts"):
    if query:
        with st.spinner("Searching for similar prompts..."):
            similar_prompts = get_similar_prompts(query, k)
        
        st.subheader("Similar Prompts:")
        for i, (prompt, score) in enumerate(similar_prompts, 1):
            st.write(f"{i}. {prompt} (Similarity: {score:.4f})")
    else:
        st.warning("Please enter a prompt to search for similar ones.")