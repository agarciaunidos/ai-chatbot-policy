import streamlit as st



def load_policy_doc_app():
    from policy_document_st import main as policy_document_st_main
    policy_document_st_main()

def load_dynamodb_app():
    from app_dy import main as db_app
    db_app()

def load_policy_chat_app():
    from policy_chat_st import main as policy_chat_st_main
    policy_chat_st_main()


def main():
    """Main entry point of the application."""
    try:
        st.sidebar.image('https://unidosus.org/wp-content/themes/unidos/images/unidosus-logo-color-2x.png', use_column_width=True)
        st.sidebar.title("Navigation")
        pagina = st.sidebar.selectbox("Select a page:", ["Policy Document App", "Chat Document App"])

        if pagina == "Policy Document App":
            load_policy_doc_app()
        elif pagina == "Chat Document App":
            load_policy_chat_app()
    except Exception as e:
        st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()