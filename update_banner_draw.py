import re

with open("agents/banner_agent.py", "r") as f:
    content = f.read()

# Replace _draw_banner body
draw_banner_new = """def _draw_banner(width: int, height: int, brief: CampaignBrief,
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

    return img"""

content = re.sub(r'def _draw_banner\(width: int, height: int, brief: CampaignBrief,\n                 label: str, rng: random\.Random\) -> Image\.Image:.*?return img', draw_banner_new, content, flags=re.DOTALL)

with open("agents/banner_agent.py", "w") as f:
    f.write(content)
