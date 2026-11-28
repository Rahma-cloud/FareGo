"""FareGo look and feel: deep green + amber on a light background."""
import streamlit as st

_CSS = """
<style>
.block-container { padding-top: 2rem; max-width: 920px; }

/* hero banner at the top of each page */
.fg-hero {
    background: #0B6E4F;
    color: #FFFFFF;
    padding: 22px 26px;
    border-radius: 14px;
    border-bottom: 5px solid #F4B400;
    margin-bottom: 1.2rem;
}
.fg-hero h1 { color: #FFFFFF; margin: 0; padding: 0; font-size: 1.8rem; }
.fg-hero p { color: #E3F3EA; margin: 6px 0 0 0; }

/* metric cards */
div[data-testid="stMetric"] {
    background: #EAF4EE;
    border-left: 5px solid #F4B400;
    padding: 14px 18px;
    border-radius: 10px;
}

/* buttons */
div.stButton > button,
div[data-testid="stFormSubmitButton"] > button,
div[data-testid="stDownloadButton"] > button {
    border-radius: 10px;
    font-weight: 600;
}

/* sidebar */
section[data-testid="stSidebar"] { background: #EAF4EE; }

footer { visibility: hidden; }
</style>
"""


def apply_style():
    st.markdown(_CSS, unsafe_allow_html=True)


def page_header(title, subtitle="", icon=""):
    """Green banner with an amber underline. Pass fixed text only (not user input)."""
    apply_style()
    heading = f"{icon} {title}".strip()
    sub = f"<p>{subtitle}</p>" if subtitle else ""
    st.markdown(f'<div class="fg-hero"><h1>{heading}</h1>{sub}</div>', unsafe_allow_html=True)