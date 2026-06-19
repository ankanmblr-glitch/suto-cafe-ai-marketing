"""
Banner Generator Agent — PIL-based image generation.
Creates on-brand café visuals without DALL-E (zero cost).
In production: calls DALL-E 3 for photorealistic images.
"""
from __future__ import annotations
import os
import random
from dataclasses import dataclass, field
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


# Theme color palettes
PALETTES = {
    "cozy":       [(45, 24, 16),   (180, 100, 50),  (240, 200, 160), (255, 248, 240)],
    "refreshing": [(0, 60, 100),   (0, 140, 200),   (100, 220, 255), (230, 248, 255)],
    "festive":    [(120, 20, 10),  (220, 80, 0),    (255, 180, 0),   (255, 248, 220)],
    "energetic":  [(20, 80, 0),    (60, 160, 40),   (160, 230, 60),  (240, 255, 220)],
    "warm":       [(80, 40, 0),    (200, 120, 20),  (255, 200, 80),  (255, 250, 230)],
    "playful":    [(80, 0, 100),   (180, 0, 200),   (255, 100, 220), (255, 230, 255)],
}

FOOD_EMOJIS = {
    "Tandoori Maggi": "🍜", "Hot Chocolate": "☕", "Cappuccino": "☕",
    "Cold Coffee": "🧊", "Suto Special Frappe": "🥤", "Brownie Frappe": "🍫",
    "Ice Tea": "🍹", "Pizza": "🍕", "Falafel Wrap": "🌯",
    "Waffle": "🧇", "Nachos": "🌮", "Smoothie": "🥤", "Mocktail": "🍹",
}


def _get_font(size: int, bold: bool = False):
    """Return a PIL font, falling back gracefully."""
    try:
        # Try Windows fonts
        for path in [
            "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        ]:
            if os.path.exists(path):
                return ImageFont.truetype(path, size)
    except Exception:
        pass
    return ImageFont.load_default()


def _vertical_gradient(draw: ImageDraw.Draw, w: int, h: int,
                        top: Tuple, bottom: Tuple):
    for y in range(h):
        t = y / h
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        draw.line([(0, y), (w, y)], fill=(r, g, b))


def _draw_banner(width: int, height: int, brief: CampaignBrief, label: str) -> Image.Image:
    palette = PALETTES.get(brief.tone, PALETTES["warm"])
    bg_top, bg_mid, accent, text_bg = palette

    img = Image.new("RGB", (width, height), bg_top)
    draw = ImageDraw.Draw(img)

    # Gradient background
    _vertical_gradient(draw, width, height, bg_top, bg_mid)

    # Decorative circles
    for _ in range(8):
        cx = random.randint(0, width)
        cy = random.randint(0, height)
        r = random.randint(30, 120)
        alpha_color = tuple(max(0, c - 30) for c in bg_mid)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=alpha_color)

    # Accent bar at bottom
    bar_h = int(height * 0.08)
    draw.rectangle([0, height - bar_h, width, height], fill=accent)

    # Main emoji / food icon
    emoji_font = _get_font(int(height * 0.18), bold=False)
    hero_emoji = "☕"
    for item in brief.hero_items:
        for keyword, em in FOOD_EMOJIS.items():
            if keyword.lower() in item.lower():
                hero_emoji = em
                break
        else:
            continue
        break
    # Draw large emoji in center-top area
    try:
        draw.text((width // 2, int(height * 0.25)), hero_emoji, font=emoji_font,
                  anchor="mm", fill=accent)
    except Exception:
        draw.text((width // 2 - 40, int(height * 0.2)), hero_emoji, fill=accent)

    # Theme display name
    title_font = _get_font(max(16, int(width * 0.045)), bold=True)
    title = brief.theme_display
    if len(title) > 24:
        title = title[:22] + "…"
    try:
        draw.text((width // 2, int(height * 0.52)), title, font=title_font,
                  anchor="mm", fill=text_bg)
    except Exception:
        draw.text((20, int(height * 0.5)), title, fill=text_bg)

    # Hero items
    items_font = _get_font(max(12, int(width * 0.032)), bold=False)
    items_str = "  •  ".join(brief.hero_items[:3])
    if len(items_str) > 36:
        items_str = items_str[:34] + "…"
    try:
        draw.text((width // 2, int(height * 0.63)), items_str, font=items_font,
                  anchor="mm", fill=accent)
    except Exception:
        draw.text((20, int(height * 0.62)), items_str, fill=accent)

    # Café name
    cafe_font = _get_font(max(10, int(width * 0.028)), bold=True)
    try:
        draw.text((width // 2, int(height * 0.74)), "SUTO CAFÉ • SILIGURI",
                  font=cafe_font, anchor="mm", fill=text_bg)
    except Exception:
        draw.text((20, int(height * 0.73)), "SUTO CAFÉ • SILIGURI", fill=text_bg)

    # CTA on accent bar
    cta_font = _get_font(max(10, int(width * 0.026)), bold=True)
    cta = brief.cta[:40] if brief.cta else "Visit us today!"
    try:
        draw.text((width // 2, height - bar_h // 2), cta,
                  font=cta_font, anchor="mm", fill=bg_top)
    except Exception:
        draw.text((20, height - bar_h - 5), cta, fill=bg_top)

    # Size label watermark (PoC indicator)
    wm_font = _get_font(max(8, int(width * 0.022)))
    try:
        draw.text((10, 10), f"[PoC] {label}", font=wm_font, fill=accent)
    except Exception:
        pass

    return img


class BannerAgent:

    def run(self, brief: CampaignBrief) -> BannerResult:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        theme_slug = brief.campaign_theme[:20]

        square_path = os.path.join(config.BANNERS_DIR, f"{ts}_{theme_slug}_1x1.png")
        story_path  = os.path.join(config.BANNERS_DIR, f"{ts}_{theme_slug}_9x16.png")
        feed_path   = os.path.join(config.BANNERS_DIR, f"{ts}_{theme_slug}_4x5.png")

        _draw_banner(1024, 1024, brief, "1:1 Instagram Feed").save(square_path)
        _draw_banner(608, 1080, brief, "9:16 Story/Reel Cover").save(story_path)
        _draw_banner(820, 1024, brief, "4:5 FB/IG Portrait").save(feed_path)

        return BannerResult(
            square_path=square_path,
            story_path=story_path,
            feed_path=feed_path,
            all_paths=[square_path, story_path, feed_path]
        )
