"""Central configuration for Suto Café PoC.
Reads from: .env (local) → Streamlit secrets (Community Cloud) → defaults.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Support Streamlit Community Cloud secrets (st.secrets acts like env vars)
def _get(key: str, default: str = "") -> str:
    """Read from os.environ first, then try st.secrets if available."""
    val = os.getenv(key, "")
    if not val:
        try:
            import streamlit as st
            val = st.secrets.get(key, default)
        except Exception:
            val = default
    return val or default


def _writable_dir() -> str:
    """Return a writable base directory.
    On Streamlit Cloud the repo root (/mount/src/...) is read-only,
    so we fall back to /tmp which is always writable."""
    src_dir = os.path.dirname(os.path.abspath(__file__))
    if os.access(src_dir, os.W_OK):
        return src_dir          # local development — write beside the code
    return "/tmp/suto_cafe"     # Streamlit Cloud / any read-only host


_BASE = _writable_dir()


class Config:
    GROQ_API_KEY: str = _get("GROQ_API_KEY")
    OPENWEATHER_API_KEY: str = _get("OPENWEATHER_API_KEY")
    DEMO_MODE: bool = _get("DEMO_MODE", "false").lower() == "true"
    GROQ_MODEL: str = _get("GROQ_MODEL", "llama-3.1-8b-instant")
    CAFE_NAME: str = _get("CAFE_NAME", "Suto Café")
    CAFE_LOCATION: str = _get("CAFE_LOCATION", "Siliguri, West Bengal")
    DB_PATH: str = os.path.join(_BASE, "suto_poc.db")
    OUTPUT_DIR: str = os.path.join(_BASE, "output")
    BANNERS_DIR: str = os.path.join(_BASE, "output", "banners")
    POSTS_DIR: str = os.path.join(_BASE, "output", "posts")

    @property
    def llm_available(self) -> bool:
        return bool(self.GROQ_API_KEY) and not self.DEMO_MODE

    @property
    def weather_available(self) -> bool:
        return bool(self.OPENWEATHER_API_KEY) and not self.DEMO_MODE

config = Config()

# Ensure output directories exist
os.makedirs(config.BANNERS_DIR, exist_ok=True)
os.makedirs(config.POSTS_DIR, exist_ok=True)
