"""FareGo look and feel: deep green + amber on a light background."""
from pathlib import Path

import streamlit as st

_ASSETS = Path(__file__).resolve().parent.parent / "assets"

_CSS = """
<style>
.block-container { padding-top: 2rem; max-width: 920px; }

/* hero banner at the top of each page */
.fg-hero {
    background: #0B6E4F;
    color: #FFFFFF;
    padding: 20px 24px;
    border-radius: 14px;
    border-bottom: 5px solid #F4B400;
    margin-bottom: 1.2rem;
}
.fg-hero-row { display: flex; align-items: center; gap: 16px; }
.fg-hero svg { flex: 0 0 auto; }
.fg-hero h1 { color: #FFFFFF; margin: 0; padding: 0; font-size: 1.8rem; line-height: 1.2; }
.fg-hero p { color: #E3F3EA; margin: 4px 0 0 0; }

/* metric cards */
div[data-testid="stMetric"] {
    background: #EAF4EE;
    border-left: 5px solid #F4B400;
    padding: 14px 18px;
    border-radius: 10px;
}

/* "how it works" step cards */
.fg-steps { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 12px; margin: 0.5rem 0 1.2rem 0; }
.fg-step { background: #EAF4EE; border-radius: 12px; padding: 14px 16px; border-top: 4px solid #F4B400; }
.fg-step b { display: block; color: #0B6E4F; font-size: 1.6rem; line-height: 1.1; }
.fg-step span { color: #1B2A24; font-weight: 600; display: block; margin-top: 2px; }
.fg-step small { color: #46594F; }

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

_BUS = (
    '<svg width="46" height="46" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">'
    '<rect x="4" y="8" width="40" height="28" rx="7" fill="#F4B400"/>'
    '<rect x="9" y="13" width="9" height="9" rx="2" fill="#0B6E4F"/>'
    '<rect x="20" y="13" width="9" height="9" rx="2" fill="#0B6E4F"/>'
    '<rect x="31" y="13" width="8" height="9" rx="2" fill="#0B6E4F"/>'
    '<rect x="9" y="27" width="30" height="3" rx="1.5" fill="#0B6E4F"/>'
    '<circle cx="14" cy="38" r="4.5" fill="#FFFFFF"/>'
    '<circle cx="34" cy="38" r="4.5" fill="#FFFFFF"/>'
    "</svg>"
)


def _sidebar_logo():
    try:
        st.logo(str(_ASSETS / "logo.svg"), icon_image=str(_ASSETS / "icon.svg"), size="large")
    except Exception:
        pass  # older Streamlit without st.logo, or the file is missing: skip


def apply_style():
    st.markdown(_CSS, unsafe_allow_html=True)
    _sidebar_logo()


def page_header(title, subtitle="", icon=""):
    """Green banner with the FareGo bus logo. Pass fixed text only (not user input)."""
    apply_style()
    sub = f"<p>{subtitle}</p>" if subtitle else ""
    st.markdown(
        f'<div class="fg-hero"><div class="fg-hero-row">{_BUS}'
        f"<div><h1>{title}</h1>{sub}</div></div></div>",
        unsafe_allow_html=True,
    )


def steps(items):
    """Row of numbered cards. items = [(title, small text), ...] (fixed text only)."""
    cards = "".join(
        f'<div class="fg-step"><b>{i}</b><span>{t}</span><small>{d}</small></div>'
        for i, (t, d) in enumerate(items, start=1)
    )
    st.markdown(f'<div class="fg-steps">{cards}</div>', unsafe_allow_html=True)