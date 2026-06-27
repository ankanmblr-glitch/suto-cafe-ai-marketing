import re

with open("agents/publishing_agent.py", "r") as f:
    content = f.read()

import_str = """from agents.copywriter_agent import CopyVariants, _coerce_text
from agents.banner_agent import BannerResult, _get_background_image
import base64
from io import BytesIO
"""
content = re.sub(r'from agents\.copywriter_agent import CopyVariants, _coerce_text\nfrom agents\.banner_agent import BannerResult', import_str, content)


make_svg_new = """def _make_svg(brief: CampaignBrief, w: int, h: int) -> str:
    \"\"\"
    Generate a rich inline SVG campaign graphic themed to the brief, embedding a real image background.
    \"\"\"
    tone   = brief.tone if brief.tone in _PALETTE else "warm"
    bg_dk, bg_md, accent, txt_lt = _PALETTE[tone]

    title  = brief.theme_display[:32]
    items  = " · ".join(brief.hero_items[:3])
    cta    = (brief.cta or "Visit us today!")[:50]

    # 1. Get real image background as base64
    bg_img = _get_background_image(brief)

    # Crop and Resize to fit target dimensions
    bg_w, bg_h = bg_img.size
    target_ratio = w / h
    bg_ratio = bg_w / bg_h
    if bg_ratio > target_ratio:
        new_w = int(bg_h * target_ratio)
        offset = (bg_w - new_w) // 2
        bg_img = bg_img.crop((offset, 0, offset + new_w, bg_h))
    else:
        new_h = int(bg_w / target_ratio)
        offset = (bg_h - new_h) // 2
        bg_img = bg_img.crop((0, offset, bg_w, offset + new_h))

    bg_img = bg_img.resize((w, h))
    buffered = BytesIO()
    bg_img.save(buffered, format="JPEG", quality=75)
    img_str = base64.b64encode(buffered.getvalue()).decode()
    b64_url = f"data:image/jpeg;base64,{img_str}"

    # layout constants
    hdr_h   = int(h * 0.115)
    pan_top = int(h * 0.50)
    pan_bot = int(h * 0.85)
    cta_top = pan_bot
    card_margin = int(w * 0.08)

    return f\"\"\"<svg viewBox="0 0 {w} {h}" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="gradOver" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="{bg_dk}" stop-opacity="0.75" />
      <stop offset="50%" stop-color="{bg_dk}" stop-opacity="0.35" />
      <stop offset="100%" stop-color="{bg_dk}" stop-opacity="0.9" />
    </linearGradient>
  </defs>

  <!-- Background Image -->
  <image href="{b64_url}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid slice" />

  <!-- Overlay Gradient -->
  <rect width="{w}" height="{h}" fill="url(#gradOver)" />

  <!-- Header bar -->
  <text x="{w//2}" y="{hdr_h//2}" text-anchor="middle" dominant-baseline="central"
        font-family="Arial,sans-serif" font-size="{max(14,int(w*0.038))}"
        font-weight="bold" fill="{accent}">✦  SUTO CAFÉ · SILIGURI  ✦</text>

  <!-- Content Card -->
  <rect x="{card_margin}" y="{pan_top}" width="{w - card_margin*2}" height="{pan_bot - pan_top}" rx="8" fill="{bg_dk}" fill-opacity="0.85" />
  <rect x="{card_margin}" y="{pan_top}" width="{w - card_margin*2}" height="{pan_bot - pan_top}" rx="8" fill="none" stroke="{accent}" stroke-width="2" />

  <!-- Title -->
  <text x="{w//2}" y="{pan_top + int((pan_bot-pan_top)*0.4)}" text-anchor="middle"
        font-family="Arial,sans-serif" font-size="{max(18,int(w*0.055))}"
        font-weight="bold" fill="{txt_lt}">{title.upper()}</text>

  <!-- Items -->
  <text x="{w//2}" y="{pan_top + int((pan_bot-pan_top)*0.75)}" text-anchor="middle"
        font-family="Arial,sans-serif" font-size="{max(12,int(w*0.035))}"
        fill="{accent}">{items}</text>

  <!-- CTA bar -->
  <rect y="{cta_top}" width="{w}" height="{h-cta_top}" fill="{accent}"/>
  <rect y="{cta_top}" width="{w}" height="3" fill="{bg_dk}" opacity="0.45"/>
  <text x="{w//2}" y="{cta_top + (h-cta_top)//2}" text-anchor="middle"
        dominant-baseline="central"
        font-family="Arial,sans-serif" font-size="{max(12,int(w*0.035))}"
        font-weight="bold" fill="{bg_dk}">→  {cta}  ←</text>
</svg>\"\"\"
"""

content = re.sub(r'def _make_svg\(brief: CampaignBrief, w: int, h: int\) -> str:.*?</svg>"""', make_svg_new, content, flags=re.DOTALL)

with open("agents/publishing_agent.py", "w") as f:
    f.write(content)
