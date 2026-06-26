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
from PIL import Image, ImageDraw, ImageFont
from config import config
from agents.content_strategy_agent import CampaignBrief


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

    img = Image.new("RGB", (width, height), bg_dark)
    _vertical_gradient(img, bg_dark, bg_light)
    draw = ImageDraw.Draw(img)

    # ── Subtle dot texture ─────────────────────────────────────────────────
    dot_color = tuple(min(255, c + 20) for c in bg_light)
    _dot_grid(draw, width, height, dot_color, spacing=max(28, width // 22), r=2)

    # ── Soft background orbs ───────────────────────────────────────────────
    for _ in range(4):
        cx = rng.randint(-width // 5, width + width // 5)
        cy = rng.randint(-height // 5, height + height // 5)
        r = rng.randint(width // 5, width // 2)
        orb = tuple(min(255, c + 30) for c in bg_light)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=orb)

    # ── TOP HEADER BAR ─────────────────────────────────────────────────────
    hdr_h = int(height * 0.11)
    draw.rectangle([0, 0, width, hdr_h], fill=text_dark)
    draw.rectangle([0, hdr_h - 4, width, hdr_h], fill=accent)  # accent stripe

    hdr_font = _get_font(max(14, int(width * 0.036)), bold=True)
    _safe_text(draw, (width // 2, hdr_h // 2),
               "✦  SUTO CAFÉ  ·  SILIGURI  ✦", hdr_font, accent)

    # ── HERO EMOJI — glowing centre ────────────────────────────────────────
    hero_emoji = _get_hero_emoji(brief, tone)
    emoji_y = int(height * 0.335)
    emoji_size = int(width * 0.21)

    # Glow halo
    glow_r = int(width * 0.195)
    glow_col = tuple(min(255, c + 45) for c in bg_light)
    draw.ellipse([width // 2 - glow_r, emoji_y - glow_r,
                  width // 2 + glow_r, emoji_y + glow_r], fill=glow_col)

    emoji_font = _get_font(emoji_size, bold=False)
    _safe_text(draw, (width // 2, emoji_y), hero_emoji, emoji_font, text_light)

    # ── SPARKLES around emoji ──────────────────────────────────────────────
    sparkle_ring = [
        (0.18, 0.21, 0.030), (0.82, 0.21, 0.024),
        (0.12, 0.39, 0.020), (0.88, 0.39, 0.020),
        (0.22, 0.48, 0.016), (0.78, 0.48, 0.016),
    ]
    for rx, ry, rs in sparkle_ring:
        _draw_sparkle(draw, width * rx, height * ry, width * rs, accent)

    # Scattered mini-stars
    for _ in range(7):
        sx = rng.randint(int(width * 0.04), int(width * 0.96))
        sy = rng.randint(int(height * 0.13), int(height * 0.58))
        sr = rng.randint(int(width * 0.007), int(width * 0.015))
        _draw_star(draw, sx, sy, sr, highlight, points=4)

    # ── TEXT PANEL ─────────────────────────────────────────────────────────
    panel_top    = int(height * 0.56)
    panel_bot    = int(height * 0.88)
    panel_margin = int(width * 0.06)
    panel_col    = tuple(max(0, c - 25) for c in bg_dark)

    draw.rectangle([panel_margin, panel_top, width - panel_margin, panel_bot],
                   fill=panel_col)
    # Accent top stripe on panel
    draw.rectangle([panel_margin, panel_top,
                    width - panel_margin, panel_top + 5], fill=accent)

    # Campaign / theme title
    title_font = _get_font(max(16, int(width * 0.046)), bold=True)
    title_text  = brief.theme_display.upper()
    title_y     = panel_top + int((panel_bot - panel_top) * 0.24)
    title_lines = _wrap_text(draw, title_text, title_font, int(width * 0.80))
    line_gap    = int(width * 0.054)
    for i, line in enumerate(title_lines[:2]):
        _safe_text(draw, (width // 2, title_y + i * line_gap),
                   line, title_font, text_light)

    # Hero items
    items_font = _get_font(max(12, int(width * 0.030)), bold=False)
    items_str  = "  ·  ".join(brief.hero_items[:3])
    items_y    = panel_top + int((panel_bot - panel_top) * 0.65)
    _safe_text(draw, (width // 2, items_y), items_str, items_font, accent)

    # ── CTA BOTTOM BAR ─────────────────────────────────────────────────────
    cta_top = int(height * 0.88)
    draw.rectangle([0, cta_top, width, height], fill=accent)
    draw.rectangle([0, cta_top, width, cta_top + 3], fill=text_dark)

    cta_font = _get_font(max(11, int(width * 0.030)), bold=True)
    cta_text = (brief.cta or "Visit us today!")[:50]
    cta_mid  = cta_top + (height - cta_top) // 2
    _safe_text(draw, (width // 2, cta_mid), f"→  {cta_text}  ←",
               cta_font, text_dark)

    # ── Corner tone emojis ─────────────────────────────────────────────────
    corner_ems  = TONE_EMOJIS.get(tone, ["✨", "⭐"])
    corner_font = _get_font(max(10, int(width * 0.038)), bold=False)
    for (ex, ey), em in zip(
        [(int(width * 0.09), int(height * 0.155)),
         (int(width * 0.91), int(height * 0.155))],
        corner_ems[:2]
    ):
        _safe_text(draw, (ex, ey), em, corner_font, text_light)

    # ── PoC watermark ──────────────────────────────────────────────────────
    wm_font = _get_font(max(8, int(width * 0.017)))
    try:
        draw.text((8, height - 14), f"[PoC] {label}", font=wm_font, fill=text_dark)
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
