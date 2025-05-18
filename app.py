import streamlit as st
from streamlit_option_menu import option_menu
st.set_page_config(page_title="SPBEBOT", page_icon="📊", layout="wide")

# Import fungsi halaman
from spbe_pages.about_spbe import show_about_spbe
from spbe_pages.documents_spbe import show_documents
from spbe_pages.chatbot_spbe import show_chatbot
from spbe_pages.template_prompt import show_prompt_template
from spbe_pages.hasil_penelitian import show_research_results
from spbe_pages.dashboard_spbe import show_dashboard


with st.sidebar:
    selected = option_menu(
        "Menu SPBEBOT",
        ["Tentang SPBE", "Documents SPBE", "Chatbot SPBE",  "Dashboard SPBE", "Template Prompt", "Hasil Penelitian"],
        icons=["info-circle", "filetype-pdf", "robot", "clipboard2-data", "file-earmark-text", "bar-chart"],
        menu_icon="cast",
        default_index=0,
    )

# Mapping menu ke fungsi halaman
pages = {
    "Tentang SPBE": show_about_spbe,
    "Documents SPBE": show_documents,
    "Chatbot SPBE": show_chatbot,
    "Dashboard SPBE": show_dashboard,
    "Template Prompt": show_prompt_template,
    "Hasil Penelitian": show_research_results,
}

# Tampilkan halaman sesuai menu
pages[selected]()