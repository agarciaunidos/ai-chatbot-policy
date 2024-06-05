import streamlit as st
from uuid import uuid4
import json
import jwt
import requests
import base64
from aws_secrets_initialization import ALB_ARN


# Main application title
st.title("Policy Library Project TEST - DEV")
st.caption("A Digital Services Project")
# URL 
###########
#CODE TO GET THE HEADERS FROM THE WEBSOCKET

from streamlit.web.server.websocket_headers import _get_websocket_headers
import jwt

def process_session_token_access():
    '''
    WARNING: We use unsupported features of Streamlit
             However, this is quite fast and works well with
             the latest version of Streamlit (1.27)
             Also, this does not verify the session token's
             authenticity. It only decodes the token.
    '''
    headers = _get_websocket_headers()
    if not headers or "X-Amzn-Oidc-Accesstoken" not in headers:
        return {}
    return jwt.decode(
        headers["X-Amzn-Oidc-Accesstoken"], algorithms=["ES256"], options={"verify_signature": False}
    )


access_token = process_session_token_access()
user = access_token.get("sub")
st.write('Welcome: ', user)
#st.write('decoded_tokens ', decoded_tokens)
#######

#STREAMLIT APP INITIALIZATION

st.session_state['user_id'] = user

# Initialize session state
def initialize_session_state():
    if 'session_id' not in st.session_state:
        st.session_state['session_id'] = str(uuid4())

def load_policy_doc_app():
    from policy_document_st import main as policy_document_st_main
    policy_document_st_main()

def load_dynamodb_app():
    from app_dy import main as db_app
    db_app()

def load_policy_chat_app():
    from policy_chat_st import main as policy_chat_st_main
    policy_chat_st_main()


# Sidebar
st.sidebar.image('https://unidosus.org/wp-content/themes/unidos/images/unidosus-logo-color-2x.png', use_column_width=True)
st.sidebar.title("Navigation")
pagina = st.sidebar.selectbox("Select a page:", ["Policy Document App", "Chat Document App"])

if pagina == "Policy Document App":
    load_policy_doc_app()
elif pagina == "Chat Document App":
    load_policy_chat_app()
