import streamlit as st
from streamlit.web.server.websocket_headers import _get_websocket_headers
import jwt
from uuid import uuid4
import json
import jwt
import requests
import base64

# Main application title
st.title("Policy Library Project TEST - DEV")
st.caption("A Digital Services Project")

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
st.session_state['user_id'] = user


# Initialize session state
def initialize_session_state():
    if 'session_id' not in st.session_state:
        st.session_state['session_id'] = str(uuid4())

def main_page():
    if st.button("Feedback"):
        st.session_state.page = "next"

def main_app():
    from app import main as app
    app()


def app():
    if "page" not in st.session_state:
        st.session_state.page = "main"

    if st.session_state.page == "main":
        main_page()
    elif st.session_state.page == "next":
        main_app()

if __name__ == "__main__":
    app()