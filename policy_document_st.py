import streamlit as st
from datetime import datetime
from uuid import uuid4
import time
import streamlit.components.v1 as components

# Import customized modules for specific functionalities
from document_retrieval import handle_query_retrieval
from aws_secrets_initialization import dynamodb_history
from streamlit_feedback import streamlit_feedback
from langchain_core.messages import SystemMessage

# Constants
MIN_YEAR = 2000
MAX_YEAR = 2024
DOCUMENT_TYPES = ['ALL', 'Annual Report', 'Fact Sheet', 'Article', 'Letter',
                  'Research Report', 'Appeal Letter', 'Book', 'Other']

# Initialize session state
def initialize_session_state():
    if 'session_id' not in st.session_state:
        st.session_state['session_id'] = str(uuid4())
    st.session_state.setdefault("messages", [{"role": "user", "content": "UUS Assistant"}])
    if 'prompt' not in st.session_state:
        st.session_state.prompt = None


# Handle user query
def handle_user_query(user_query, selected_years, selected_types):
    try:
        # Process the user query and retrieve answer and sources
        st.session_state["id"] = str(uuid4())  # Assign new unique ID for each query
        st.info("Your Input: " + user_query)
        answer, sources_metadata = handle_query_retrieval(user_query, selected_years, selected_types)
        st.session_state.prompt = user_query
        st.subheader('Answer:')
        st.write(answer)
        st.subheader('Sources:')
        st.data_editor(sources_metadata, column_config={"Source": st.column_config.LinkColumn("Source"),
                                                        "Relevance Score": st.column_config.NumberColumn("Relevance Score", format='%.2f %%')},
                       hide_index=True)
        # Feedback form within a Streamlit form
        with st.form('feedback_form'):
            streamlit_feedback(feedback_type="faces", optional_text_label="[Optional] Please provide an explanation", 
                                align="flex-start", key='fb_k', on_submit= handle_feedback)
            st.form_submit_button('Save Feedback', on_click=handle_feedback)
    except Exception as e:
        st.error(f"An error occurred: {e}")

# Handle user feedback
def handle_feedback():
    """Logs feedback received from the user."""
    id = st.session_state["id"]
    st_session_id = st.session_state["session_id"]
    user_id = st.session_state['user_id']
    face_feedback_score = {"😀": 5, "🙂": 4, "😐": 3, "🙁": 2, "😞": 1}
    try:
        if st.session_state.fb_k is None:
            return  # If feedback is not available, do nothing
        
        thumb_feedback = st.session_state.fb_k.get("score")
        feedback_text = st.session_state.fb_k.get("text")
        
        # Check for blank feedback
        if not thumb_feedback and not feedback_text:
            return  # If feedback is blank, do nothing

        timestamp = int(time.time())
        score = face_feedback_score.get(thumb_feedback, 0)
        dynamodb_history.add_message(SystemMessage(id=id, user_id=user_id, content='feedback', st_session_id=st_session_id,
                                                  response_metadata={
                                                      'timestamp': timestamp,
                                                      'face_feedback': thumb_feedback,
                                                      'feedback_text': feedback_text,
                                                      'score': score,
                                                  }))
    except KeyError as ke:
        st.error(f"Key error occurred while handling feedback: {ke}")
    except ValueError as ve:
        st.error(f"Value error occurred while handling feedback: {ve}")
    except Exception as e:
        st.error(f"An unexpected error occurred while handling feedback: {e}")



def launch_new_app():
    from prompt_retrieval import main as prompt_retrieval_main
    prompt_retrieval_main()

def main():
    # Initialize session state
    initialize_session_state()

    st.header("Policy Document Assistant")
    # Display chat messages from session state
    for message in st.session_state.messages:
        st.chat_message(message["role"]).write(message["content"])

    # Sidebar configuration for document filtering
    with st.sidebar:
        st.header("Contact Us")
        # Create the email link using HTML
        email = "apatricio@unidosus.org"
        email_html = f'<a href="mailto:{email}">{email}</a>'
        # Display the email link in the sidebar
        st.markdown("To report any suggestion or error, contact us at:")
        components.html(email_html, height=30)
        st.title("Select Time Period")
        selected_years = st.slider("Year", min_value=MIN_YEAR, max_value=MAX_YEAR, 
                                   value=(2012, 2024), step=1, format="%d")
        st.title("Select Document Type")
        selected_types = st.multiselect('Select Type:', DOCUMENT_TYPES)
        if st.button("Similar Prompts", disabled=not st.session_state.prompt):
            st.write(st.session_state.prompt)
            launch_new_app()
            st.session_state.prompt = None

    # Main chat input for queries
    user_query = st.chat_input()
    if user_query:
        handle_user_query(user_query, selected_years, selected_types)
    else:
        st.error("Please enter your prompt.")

if __name__ == "__main__":
    main()