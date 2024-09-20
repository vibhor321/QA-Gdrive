import streamlit as st
from streamlit_oauth import OAuth2Component
import base64
import json
from PIL import Image
from utils.helpers import (
    get_text_from_google_doc,
    get_text_chunks,
    update_vector_store,
    query_db,
    list_files_in_folder,
    ends_with_subdomain,
)
from streamlit_js_eval import streamlit_js_eval

favicon = Image.open("favicon.png")
title = st.secrets["app_title"]
st.set_page_config(
    page_title=title,
    page_icon=favicon,
    layout="centered",
    initial_sidebar_state="auto",
    menu_items=None,
)

if title:
    st.title(title)

if st.secrets["app_description"]:
    st.write(st.secrets["app_description"])

# create an OAuth2Component instance
CLIENT_ID = st.secrets["oauth"]["client_id"]
CLIENT_SECRET = st.secrets["oauth"]["client_secret"]
AUTHORIZE_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
REVOKE_ENDPOINT = "https://oauth2.googleapis.com/revoke"

if "auth" not in st.session_state:
    with st.sidebar:
        image = Image.open("logo.png")
        st.sidebar.image(image)
        # create a button to start the OAuth2 flow
        oauth2 = OAuth2Component(
            CLIENT_ID,
            CLIENT_SECRET,
            AUTHORIZE_ENDPOINT,
            TOKEN_ENDPOINT,
            TOKEN_ENDPOINT,
            REVOKE_ENDPOINT,
        )
        try:
            result = oauth2.authorize_button(
                name="Login with Google",
                icon="https://www.google.com.tw/favicon.ico",
                redirect_uri=st.secrets["oauth"]["redirect_uri"],
                scope="openid email profile https://www.googleapis.com/auth/documents https://www.googleapis.com/auth/drive",
                key="google",
                extras_params={"prompt": "consent", "access_type": "offline"},
                use_container_width=True,
                pkce="S256",
            )

            if result:
                # decode the id_token and get the user's email address
                id_token = result["token"]["id_token"]
                # verify the signature is an optional step for security
                payload = id_token.split(".")[1]
                # add padding to the payload if needed
                payload += "=" * (-len(payload) % 4)
                payload = json.loads(base64.b64decode(payload))
                email = payload["email"]
                if ends_with_subdomain(
                    email, st.secrets["authenticated_email_domains"]
                ):
                    st.session_state["auth"] = email
                    st.session_state["token"] = result["token"]["access_token"]
                    st.session_state["refresh_token"] = result["token"]["refresh_token"]
                    st.rerun()
                else:
                    st.write(
                        f"{email} not authenticated. Only emails ending with @rubicotech.in and @rubicotech.com can access the app"
                    )
        except Exception as e:
            st.text(f"Error encountered {e}, please reload the page and try again")
            if st.button("Reload page"):
                streamlit_js_eval(js_expressions="parent.window.location.reload()")

        # ADMIN METHODS FOR UPDATING THE VECTOR DB
if (
    "auth" in st.session_state
    and st.session_state["auth"] in st.secrets["admin_emails"]
):
    with st.sidebar:
        st.text("Admin Controls")
        if st.button("Process New Data"):
            headers = {
                "Authorization": f"Bearer {st.session_state['token']}",
                "Accept": "application/json",
            }
            newfiles = list_files_in_folder(
                st.secrets["folder_id"],
                st.session_state["token"],
                st.session_state["refresh_token"],
            )
            if newfiles is not None:
                text_content = ""
                for file in newfiles:
                    print("updating db from file", file)
                    file_content = get_text_from_google_doc(file, headers)
                    if file_content is not None:
                        text_content = text_content + file_content
                text_chunks = get_text_chunks(text_content)
                update_vector_store(text_chunks, "rubico_docs")
            st.success("Update Done")


if "auth" in st.session_state:
    user_question = st.chat_input("Ask a Question from the Google Document")
    if user_question:
        with st.spinner("Processing..."):
            query_db(user_question, "rubico_docs")
