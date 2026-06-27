"""
Banner Generator Agent — PIL-based image generation.
Creates on-brand café visuals without DALL-E (zero cost).
Upgraded: rich gradients, decorative stars/sparkles, text panels, themed colours.
In production: calls DALL-E 3 for photorealistic images.
"""
from __future__ import annotations
import os
import math
import random
from dataclasses import dataclass
from datetime import datetime
from typing import List, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from config import config
from agents.content_strategy_agent import CampaignBrief
import requests
import io
import json



@dataclass
class BannerResult:
    square_path: str    # 1:1 — Instagram feed
    story_path: str     # 9:16 — Story / Reel cover
    feed_path: str      # 4:5 — FB/IG portrait feed
    all_paths: List[str]


# ── Colour palettes ────────────────────────────────────────────────────────
# (bg_dark, bg_light, accent, text_light, text_dark, highlight)
PALETTES = {
    "cozy":       ((45,  24,  16),  (140,  70,  30),  (240, 190, 120), (255, 248, 235), (30,  15,   5), (220, 120,  40)),
    "refreshing": ((0,   45,  90),  (0,   110, 170),  (80,  210, 255), (230, 248, 255), (0,   25,  60), (0,  190, 240)),
    "festive":    ((100, 10,   5),  (200,  60,   0),  (255, 185,   0), (255, 250, 220), (70,   5,   0), (255, 140,   0)),
    "energetic":  ((10,  60,   0),  (40,  140,  30),  (160, 235,  50), (240, 255, 215), (5,   40,   0), (100, 200,  20)),
    "warm":       ((70,  30,   0),  (190, 100,  15),  (255, 200,  70), (255, 250, 225), (50,  20,   0), (230, 150,  20)),
    "playful":    ((60,   0,  80),  (150,   0, 170),  (255, 100, 220), (255, 235, 255), (40,   0,  55), (200,   0, 230)),
    "romantic":   ((80,  10,  30),  (190,  40,  80),  (255, 160, 180), (255, 240, 245), (55,   5,  20), (230,  80, 120)),
    "monsoon":    ((20,  40,  80),  (50,   90, 150),  (100, 180, 255), (225, 240, 255), (10,  25,  60), (60,  140, 220)),
}

FOOD_EMOJIS = {
    "tandoori maggi": "🍜", "hot chocolate": "☕", "cappuccino": "☕",
    "cold coffee": "🧊",    "frappe": "🥤",        "brownie": "🍫",
    "ice tea": "🍹",        "pizza": "🍕",          "falafel": "🌯",
    "waffle": "🧇",         "nachos": "🌮",         "smoothie": "🥤",
    "mocktail": "🍹",       "sandwich": "🥪",       "burger": "🍔",
    "pasta": "🍝",          "chai": "🍵",            "tea": "🍵",
    "coffee": "☕",         "juice": "🍊",           "shake": "🥛",
    "cake": "🎂",           "cookie": "🍪",          "donut": "🍩",
    "muffin": "🧁",         "latte": "☕",           "espresso": "☕",
}

TONE_EMOJIS = {
    "cozy":       ["☕", "🕯️", "🍵"],
    "refreshing": ["🧊", "💧", "✨"],
    "festive":    ["🎉", "🪔", "⭐"],
    "energetic":  ["⚡", "🌿", "💪"],
    "warm":       ["🌟", "☀️", "🍂"],
    "playful":    ["🎈", "🌈", "✨"],
    "romantic":   ["💖", "🌸", "✨"],
    "monsoon":    ["🌧️", "☔", "💙"],
}


# ── Font helpers ───────────────────────────────────────────────────────────

def _get_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = (
        ["C:/Windows/Fonts/arialbd.ttf",
         "C:/Windows/Fonts/calibrib.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
         "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
         "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"]
        if bold else
        ["C:/Windows/Fonts/arial.ttf",
         "C:/Windows/Fonts/calibri.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
         "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
         "/usr/share/fonts/truetype/freefont/FreeSans.ttf"]
    )
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()


# ── Image Assets ────────────────────────────────────────────────────────
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
    """Fetches or loads a local background image for the campaign."""
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

# ── Drawing primitives ─────────────────────────────────────────────────────

def _vertical_gradient(img: Image.Image, top: Tuple, bottom: Tuple) -> None:
    w, h = img.size
    draw = ImageDraw.Draw(img)
    for y in range(h):
        t = y / h
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        draw.line([(0, y), (w, y)], fill=(r, g, b))


def _draw_sparkle(draw: ImageDraw.Draw, cx: float, cy: float, r: float, fill: Tuple) -> None:
    """4-pointed diamond sparkle."""
    pts = [
        (cx,           cy - r),
        (cx + r * 0.25, cy - r * 0.25),
        (cx + r,       cy),
        (cx + r * 0.25, cy + r * 0.25),
        (cx,           cy + r),
        (cx - r * 0.25, cy + r * 0.25),
        (cx - r,       cy),
        (cx - r * 0.25, cy - r * 0.25),
    ]
    draw.polygon(pts, fill=fill)


def _draw_star(draw: ImageDraw.Draw, cx: float, cy: float, r: float,
               fill: Tuple, points: int = 5) -> None:
    pts = []
    for i in range(points * 2):
        angle = math.pi / points * i - math.pi / 2
        rad = r if i % 2 == 0 else r * 0.42
        pts.append((cx + rad * math.cos(angle), cy + rad * math.sin(angle)))
    draw.polygon(pts, fill=fill)


def _dot_grid(draw: ImageDraw.Draw, w: int, h: int, color: Tuple,
              spacing: int = 40, r: int = 2) -> None:
    for x in range(0, w + spacing, spacing):
        for y in range(0, h + spacing, spacing):
            draw.ellipse([x - r, y - r, x + r, y + r], fill=color)


def _wrap_text(draw: ImageDraw.Draw, text: str, font: ImageFont.FreeTypeFont,
               max_width: int) -> List[str]:
    words = text.split()
    lines, current = [], ""
    for word in words:
        test = (current + " " + word).strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines or [text]


def _safe_text(draw: ImageDraw.Draw, xy: Tuple, text: str,
               font: ImageFont.FreeTypeFont, fill: Tuple,
               anchor: str = "mm") -> None:
    try:
        draw.text(xy, text, font=font, anchor=anchor, fill=fill)
    except Exception:
        draw.text((xy[0] - 40, xy[1] - 10), text, font=font, fill=fill)


def _get_hero_emoji(brief: CampaignBrief, tone: str) -> str:
    for item in brief.hero_items:
        item_lower = item.lower()
        for keyword, em in FOOD_EMOJIS.items():
            if keyword in item_lower:
                return em
    return TONE_EMOJIS.get(tone, ["☕"])[0]


# ── Main banner renderer ───────────────────────────────────────────────────

def _draw_banner(width: int, height: int, brief: CampaignBrief,
                 label: str, rng: random.Random) -> Image.Image:
    tone = brief.tone if brief.tone in PALETTES else "warm"
    bg_dark, bg_light, accent, text_light, text_dark, highlight = PALETTES[tone]

    # 1. Load Background Image
    bg_img = _get_background_image(brief)

    # 2. Crop and Resize to fit target dimensions (width x height)
    bg_w, bg_h = bg_img.size
    target_ratio = width / height
    bg_ratio = bg_w / bg_h

    if bg_ratio > target_ratio:
        # bg is wider than needed
        new_w = int(bg_h * target_ratio)
        offset = (bg_w - new_w) // 2
        bg_img = bg_img.crop((offset, 0, offset + new_w, bg_h))
    else:
        # bg is taller than needed
        new_h = int(bg_w / target_ratio)
        offset = (bg_h - new_h) // 2
        bg_img = bg_img.crop((0, offset, bg_w, offset + new_h))

    img = bg_img.resize((width, height), Image.Resampling.LANCZOS)

    # 3. Apply Gradient Overlay
    # Create an overlay image with an alpha channel
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw_overlay = ImageDraw.Draw(overlay)

    # Generate a vertical gradient alpha overlay: top to bottom (dark to semi-transparent to dark)
    for y in range(height):
        t = y / height
        # Parabolic opacity curve: darker at top (0.8) and bottom (0.9), lighter in middle (0.4)
        opacity = int(255 * (0.8 - 0.4 * math.sin(t * math.pi) + 0.1 * t))

        # We blend the tone's bg_dark color
        r, g, b = bg_dark
        draw_overlay.line([(0, y), (width, y)], fill=(r, g, b, min(255, opacity + 40)))

    # Merge overlay with image
    img = img.convert("RGBA")
    img = Image.alpha_composite(img, overlay).convert("RGB")

    draw = ImageDraw.Draw(img)

    # ── TOP HEADER BAR ─────────────────────────────────────────────────────
    hdr_h = int(height * 0.11)

    hdr_font = _get_font(max(14, int(width * 0.036)), bold=True)
    _safe_text(draw, (width // 2, hdr_h // 2),
               "✦  SUTO CAFÉ  ·  SILIGURI  ✦", hdr_font, accent)

    # ── TEXT PANEL ─────────────────────────────────────────────────────────
    panel_top    = int(height * 0.56)
    panel_bot    = int(height * 0.88)

    # Draw an elegant translucent card for text
    card_margin = int(width * 0.08)
    card_top = int(height * 0.45)
    card_bot = int(height * 0.85)

    card_overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    card_draw = ImageDraw.Draw(card_overlay)
    card_col = (bg_dark[0], bg_dark[1], bg_dark[2], 200) # 80% opacity

    # Rounded rectangle using polygon/ellipse approximation or simple rectangle if needed. Let's do simple for speed but with border
    card_draw.rectangle([card_margin, card_top, width - card_margin, card_bot], fill=card_col)
    card_draw.rectangle([card_margin, card_top, width - card_margin, card_bot], outline=accent, width=2)

    img = img.convert("RGBA")
    img = Image.alpha_composite(img, card_overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    # Campaign / theme title
    title_font = _get_font(max(18, int(width * 0.05)), bold=True)
    title_text  = brief.theme_display.upper()
    title_y     = card_top + int((card_bot - card_top) * 0.3)
    title_lines = _wrap_text(draw, title_text, title_font, int(width * 0.70))
    line_gap    = int(width * 0.06)
    for i, line in enumerate(title_lines[:2]):
        _safe_text(draw, (width // 2, title_y + i * line_gap),
                   line, title_font, text_light)

    # Hero items
    items_font = _get_font(max(14, int(width * 0.035)), bold=False)
    items_str  = "  ·  ".join(brief.hero_items[:3])
    items_y    = card_top + int((card_bot - card_top) * 0.75)
    _safe_text(draw, (width // 2, items_y), items_str, items_font, accent)

    # ── CTA BOTTOM BAR ─────────────────────────────────────────────────────
    cta_top = int(height * 0.88)
    draw.rectangle([0, cta_top, width, height], fill=accent)
    draw.rectangle([0, cta_top, width, cta_top + 3], fill=text_dark)

    cta_font = _get_font(max(12, int(width * 0.032)), bold=True)
    cta_text = (brief.cta or "Visit us today!")[:50]
    cta_mid  = cta_top + (height - cta_top) // 2
    _safe_text(draw, (width // 2, cta_mid), f"→  {cta_text}  ←",
               cta_font, text_dark)

    # ── PoC watermark ──────────────────────────────────────────────────────
    wm_font = _get_font(max(10, int(width * 0.02)))
    try:
        draw.text((8, height - 16), f"[PoC] {label}", font=wm_font, fill=text_dark)
    except Exception:
        pass

    return img


# ── Agent ──────────────────────────────────────────────────────────────────

class BannerAgent:

    def run(self, brief: CampaignBrief) -> BannerResult:
        # Deterministic seed per campaign so repeated previews are consistent
        rng = random.Random(hash(brief.campaign_theme + brief.tone))
        ts  = datetime.now().strftime("%Y%m%d_%H%M%S")
        slug = brief.campaign_theme[:20].replace(" ", "_")

        os.makedirs(config.BANNERS_DIR, exist_ok=True)

        square_path = os.path.join(config.BANNERS_DIR, f"{ts}_{slug}_1x1.png")
        story_path  = os.path.join(config.BANNERS_DIR, f"{ts}_{slug}_9x16.png")
        feed_path   = os.path.join(config.BANNERS_DIR, f"{ts}_{slug}_4x5.png")

        _draw_banner(1024, 1024, brief, "1:1 Instagram Feed",    rng).save(square_path)
        _draw_banner(608,  1080, brief, "9:16 Story/Reel Cover", rng).save(story_path)
        _draw_banner(820,  1024, brief, "4:5 FB/IG Portrait",    rng).save(feed_path)

        return BannerResult(
            square_path=square_path,
            story_path=story_path,
            feed_path=feed_path,
            all_paths=[square_path, story_path, feed_path]
        )
