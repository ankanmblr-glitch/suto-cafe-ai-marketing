import re

with open("agents/banner_agent.py", "r") as f:
    content = f.read()

# Add requests and io imports
import_str = """from PIL import Image, ImageDraw, ImageFont, ImageFilter
from config import config
from agents.content_strategy_agent import CampaignBrief
import requests
import io
import json
"""
content = re.sub(r'from PIL import Image, ImageDraw, ImageFont\nfrom config import config\nfrom agents\.content_strategy_agent import CampaignBrief', import_str, content)

# Add image download and load logic
download_str = """# ── Image Assets ────────────────────────────────────────────────────────
IMAGES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "demo_data", "images")

# Map keywords to public Unsplash source URLs for realistic food backgrounds
UNSPLASH_MAP = {
    "coffee": "https://images.unsplash.com/photo-1497935586351-b67a49e012bf?w=1024&q=80", # cold coffee/frappe
    "pizza": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=1024&q=80",
    "burger": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=1024&q=80",
    "wrap": "https://images.unsplash.com/photo-1626804475297-41609ea0eb4eb?w=1024&q=80", # falafel wrap
    "maggi": "https://images.unsplash.com/photo-1612929633738-8fe44f7ec841?w=1024&q=80", # noodles
    "tea": "https://images.unsplash.com/photo-1558160074-4d7d8bdf4256?w=1024&q=80",
    "waffle": "https://images.unsplash.com/photo-1562376552-0d160a2f9fa4?w=1024&q=80",
    "default": "https://images.unsplash.com/photo-1554118811-1e0d58224f24?w=1024&q=80" # cafe background
}

def _get_background_image(brief: CampaignBrief) -> Image.Image:
    \"\"\"Fetches or loads a local background image for the campaign.\"\"\"
    os.makedirs(IMAGES_DIR, exist_ok=True)

    # Determine the best keyword
    keyword = "default"
    hero_text = " ".join(brief.hero_items).lower()
    for k in UNSPLASH_MAP:
        if k in hero_text and k != "default":
            keyword = k
            break
    if keyword == "default" and "frappe" in hero_text:
        keyword = "coffee"
    if keyword == "default" and "brownie" in hero_text:
        keyword = "waffle" # close enough dessert

    img_path = os.path.join(IMAGES_DIR, f"{keyword}.jpg")

    # Download if missing
    if not os.path.exists(img_path):
        try:
            url = UNSPLASH_MAP[keyword]
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                with open(img_path, 'wb') as f:
                    f.write(r.content)
        except Exception as e:
            print(f"[BannerAgent] Error downloading image for {keyword}: {e}")

    # Load and return image (or fallback to a black image if download failed)
    if os.path.exists(img_path):
        try:
            return Image.open(img_path).convert("RGB")
        except Exception:
            pass

    return Image.new("RGB", (1024, 1024), (40, 40, 40))

# ── Drawing primitives ─────────────────────────────────────────────────────"""

content = content.replace("# ── Drawing primitives ─────────────────────────────────────────────────────", download_str)

with open("agents/banner_agent.py", "w") as f:
    f.write(content)
