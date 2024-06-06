import streamlit as st

def main_page():
    st.title("Main Page")
    if st.button("Go to Next Page"):
        st.session_state.page = "next"


def load_policy_chat_app():
    from app import main as policy_chat_st_main
    policy_chat_st_main()

def next_page():
    st.title("Next Page")
    st.write("This is the next page.")
    if st.button("Go Back"):
        st.session_state.page = "main"

def app():
    if "page" not in st.session_state:
        st.session_state.page = "main"

    if st.session_state.page == "main":
        main_page()
    elif st.session_state.page == "next":
        load_policy_chat_app()

if __name__ == "__main__":
    app()