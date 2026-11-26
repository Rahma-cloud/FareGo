"""Driver QR codes (scan-to-pay). The QR holds a link containing the
driver's qr_code value from the drivers table (for example DRV-0003)."""
import io

import qrcode
import streamlit as st


def app_base_url():
    # Set app_url at the TOP of .streamlit/secrets.toml (above [mysql]).
    try:
        return str(st.secrets["app_url"]).rstrip("/")
    except Exception:
        return "http://localhost:8501"


def driver_link(qr_code):
    return f"{app_base_url()}/Pay?driver={qr_code}"


def qr_png_bytes(text):
    buf = io.BytesIO()
    qrcode.make(text).save(buf, format="PNG")
    return buf.getvalue()