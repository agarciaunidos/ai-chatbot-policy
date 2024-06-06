import streamlit as st
from streamlit.web.server.websocket_headers import _get_websocket_headers
from aws_secrets_initialization import dynamodb_history
from langchain_core.messages import SystemMessage
import jwt
from uuid import uuid4
import time
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

#st_session_id = st.session_state['session_id']        

def main_page():
    #st.write("Purpose of Using AI Tool")
    #user_input = st.text_input("What is the purpose of using this tool?", "")
    
    form = st.form(key='my-form')
    user_input = form.text_input('Enter your feedback')
    submit = form.form_submit_button('Submit')

    st.write('Press submit to have your feedback submited')

    if submit:
        #st.write(f'hello {name}')
        st.session_state.page = "next"
        timestamp = int(time.time())
        user_id = st.session_state['user_id']
        dynamodb_history.add_message(SystemMessage(st_session_id=st.session_state['session_id'],user_id = user_id, content='Purpose',
                                                  response_metadata={
                                                      'timestamp': timestamp,
                                                      'user_input': user_input}))


    #if st.button("Feedback"):
        #st.session_state.page = "next"

def main_app():
    from app import main as app
    app()


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