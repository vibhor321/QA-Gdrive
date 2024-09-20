import streamlit as st
from utils.helpers import get_current_page
from streamlit_extras.colored_header import colored_header
from PIL import Image
from utils.helpers import get_manager, get_current_page
from time import sleep

cookie_manager = get_manager()





def sidebar():
    image = Image.open("logo.png")
    st.sidebar.image(image)
    with st.sidebar:
        colored_header(
            label="App Menu",
            description="Menu Items",
            color_name="violet-70",
        )
