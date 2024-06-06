import streamlit as st
from streamlit.web.server.websocket_headers import _get_websocket_headers
from aws_secrets_initialization import dynamodb_history
from langchain_core.messages import SystemMessage
from uuid import uuid4
import time
import jwt

# Main application title
st.title("Policy Library Project TEST - DEV")
st.caption("A Digital Services Project")

def process_session_token_access():
    """
    WARNING: This function uses unsupported features of Streamlit.
    It decodes the session token without verifying its authenticity.
    It works well with the latest version of Streamlit (1.27).
    """
    headers = _get_websocket_headers()
    if not headers or "X-Amzn-Oidc-Accesstoken" not in headers:
        return {}
    return jwt.decode(headers["X-Amzn-Oidc-Accesstoken"], algorithms=["ES256"], options={"verify_signature": False})

# Process session token and get user information
access_token = process_session_token_access()
user = access_token.get("sub", "Unknown User")
st.write('Welcome: ', user)
st.session_state['user_id'] = user

# Initialize session state
def initialize_session_state():
    if 'session_id' not in st.session_state:
        st.session_state['session_id'] = str(uuid4())

def main_page():
    # User input form
    form = st.form(key='feedback-form')
    user_input = form.text_input('Enter your feedback')
    submit = form.form_submit_button('Submit',type="primary")
    st.write('Press submit to have your feedback submitted')
    if submit:
        st.session_state.page = "next"
        timestamp = int(time.time())
        user_id = st.session_state['user_id']
        dynamodb_history.add_message(SystemMessage(
            st_session_id=st.session_state['session_id'],
            user_id=user_id,
            content='Purpose',
            response_metadata={
                'timestamp': timestamp,
                'user_input': user_input
            }
        ))

def main_app():
    from app import main as app_main
    app_main()

def app():
    initialize_session_state()
    if "page" not in st.session_state:
        st.session_state.page = "main"

    if st.session_state.page == "main":
        main_page()
    elif st.session_state.page == "next":
        main_app()

if __name__ == "__main__":
    app()