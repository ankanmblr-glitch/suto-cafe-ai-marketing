"""
Publishing Agent — PoC version.
Generates realistic HTML previews of Facebook, Instagram, and WhatsApp posts.

Image strategy: SVG graphics are generated inline inside each HTML file.
  - Zero file-path issues (no external src= references)
  - SVGs are ~5 KB each — no iframe budget problems
  - Fully theme-aware: colours, emoji, items, CTA all match the campaign brief

In production: calls Meta Graph API + WATI WhatsApp API with DALL-E 3 images.
"""
from __future__ import annotations
import os
import random
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Any
from config import config
from agents.content_strategy_agent import CampaignBrief
from agents.copywriter_agent import CopyVariants, _coerce_text
from agents.banner_agent import BannerResult


@dataclass
class PublishResult:
    campaign_id: str
    channels_published: List[str]
    post_urls: Dict[str, str]
    mock_post_ids: Dict[str, str]
    reach_estimate: int
    source: str = "mock_html_preview"

    def summary(self) -> str:
        return (f"Published to {', '.join(self.channels_published)} | "
                f"Est. reach: {self.reach_estimate:,} | Campaign: {self.campaign_id}")


# ── Theme palettes (bg_dark, bg_mid, accent, text_light) ──────────────────
_PALETTE: Dict[str, tuple] = {
    "cozy":       ("#2d1810", "#8c461e", "#f0be78", "#fff8eb"),
    "refreshing": ("#002d5a", "#006eb0", "#50d2ff", "#e6f8ff"),
    "festive":    ("#640a05", "#c84200", "#ffb900", "#fffadc"),
    "energetic":  ("#0a3c00", "#288c1e", "#a0eb32", "#f0ffdb"),
    "warm":       ("#461e00", "#be640f", "#ffc846", "#fffae1"),
    "playful":    ("#3c0050", "#960096", "#ff64dc", "#ffebff"),
    "romantic":   ("#500a1e", "#be2850", "#ffa0b4", "#fff0f5"),
    "monsoon":    ("#142850", "#325a96", "#64b4ff", "#e1f0ff"),
}

_FOOD_EMOJI: Dict[str, str] = {
    "frappe": "🥤", "coffee": "☕", "maggi": "🍜", "hot chocolate": "☕",
    "pizza": "🍕", "falafel": "🌯", "wrap": "🌯", "waffle": "🧇",
    "nachos": "🌮", "smoothie": "🥤", "mocktail": "🍹", "tea": "🍵",
    "chai": "🍵", "brownie": "🍫", "cake": "🎂", "sandwich": "🥪",
    "burger": "🍔", "pasta": "🍝", "juice": "🍊", "shake": "🥛",
    "ice": "🧊", "cold": "🧊", "latte": "☕", "espresso": "☕",
}

_TONE_CORNER: Dict[str, List[str]] = {
    "cozy":       ["☕", "🕯️"],  "refreshing": ["🧊", "💧"],
    "festive":    ["🎉", "🪔"],  "energetic":  ["⚡", "🌿"],
    "warm":       ["🌟", "☀️"], "playful":    ["🎈", "🌈"],
    "romantic":   ["💖", "🌸"], "monsoon":    ["🌧️", "☔"],
}


def _hero_emoji(brief: CampaignBrief) -> str:
    for item in brief.hero_items:
        il = item.lower()
        for kw, em in _FOOD_EMOJI.items():
            if kw in il:
                return em
    tone_corners = _TONE_CORNER.get(brief.tone, ["☕", "✨"])
    return tone_corners[0]


def _sparkle_pts(cx: float, cy: float, r: float) -> str:
    """Return SVG polygon points for a 4-pointed diamond sparkle."""
    return (f"{cx:.1f},{cy-r:.1f} {cx+r*0.28:.1f},{cy-r*0.28:.1f} "
            f"{cx+r:.1f},{cy:.1f} {cx+r*0.28:.1f},{cy+r*0.28:.1f} "
            f"{cx:.1f},{cy+r:.1f} {cx-r*0.28:.1f},{cy+r*0.28:.1f} "
            f"{cx-r:.1f},{cy:.1f} {cx-r*0.28:.1f},{cy-r*0.28:.1f}")


def _dot_row(w: int, h: int, gap: int, fill: str, opacity: float) -> str:
    dots = []
    for x in range(0, w + gap, gap):
        for y in range(0, h + gap, gap):
            dots.append(f'<circle cx="{x}" cy="{y}" r="2" fill="{fill}" opacity="{opacity}"/>')
    return "".join(dots)


def _make_svg(brief: CampaignBrief, w: int, h: int) -> str:
    """
    Generate a rich inline SVG campaign graphic themed to the brief.
    Sections: header bar → glow + hero emoji → sparkle ring → text panel → CTA bar.
    """
    tone   = brief.tone if brief.tone in _PALETTE else "warm"
    bg_dk, bg_md, accent, txt_lt = _PALETTE[tone]

    emoji  = _hero_emoji(brief)
    title  = brief.theme_display[:32]
    items  = " · ".join(brief.hero_items[:3])
    cta    = (brief.cta or "Visit us today!")[:50]
    corners = _TONE_CORNER.get(tone, ["✨", "⭐"])

    # layout constants (proportional)
    hdr_h   = int(h * 0.115)
    em_y    = int(h * 0.36)
    em_sz   = int(w * 0.20)
    pan_top = int(h * 0.565)
    pan_bot = int(h * 0.880)
    cta_top = pan_bot

    sparkles = [
        (w * 0.17, h * 0.22, w * 0.026),
        (w * 0.83, h * 0.22, w * 0.021),
        (w * 0.11, h * 0.41, w * 0.018),
        (w * 0.89, h * 0.41, w * 0.018),
        (w * 0.21, h * 0.50, w * 0.013),
        (w * 0.79, h * 0.50, w * 0.013),
    ]
    sparkle_svg = "".join(
        f'<polygon points="{_sparkle_pts(cx, cy, r)}" fill="{accent}"/>'
        for cx, cy, r in sparkles
    )

    # mini star scatters
    rng = random.Random(hash(brief.campaign_theme))
    mini_stars = "".join(
        f'<polygon points="{_sparkle_pts(rng.randint(int(w*0.05), int(w*0.95)), rng.randint(int(h*0.14), int(h*0.56)), w*0.011)}" fill="{accent}" opacity="0.65"/>'
        for _ in range(6)
    )

    return f"""<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" style="width:100%;display:block">
  <defs>
    <linearGradient id="bgG{w}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{bg_dk}"/>
      <stop offset="100%" stop-color="{bg_md}"/>
    </linearGradient>
    <filter id="glow{w}" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="10" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>

  <!-- Background -->
  <rect width="{w}" height="{h}" fill="url(#bgG{w})"/>

  <!-- Dot texture -->
  {_dot_row(w, h, max(28, w // 22), bg_md, 0.45)}

  <!-- Decorative orbs -->
  <circle cx="{int(w*0.12)}" cy="{int(h*0.19)}" r="{int(w*0.19)}" fill="{bg_md}" opacity="0.32"/>
  <circle cx="{int(w*0.88)}" cy="{int(h*0.79)}" r="{int(w*0.21)}" fill="{bg_md}" opacity="0.28"/>

  <!-- Header bar -->
  <rect width="{w}" height="{hdr_h}" fill="{bg_dk}" opacity="0.88"/>
  <rect y="{hdr_h-4}" width="{w}" height="4" fill="{accent}"/>
  <text x="{w//2}" y="{int(hdr_h*0.65)}" text-anchor="middle"
        font-family="Arial,Helvetica,sans-serif" font-size="{max(12,int(w*0.038))}"
        font-weight="bold" fill="{accent}">✦  SUTO CAFÉ  ·  SILIGURI  ✦</text>

  <!-- Glow halo -->
  <circle cx="{w//2}" cy="{em_y}" r="{int(w*0.20)}" fill="{bg_md}" opacity="0.55" filter="url(#glow{w})"/>

  <!-- Hero emoji -->
  <text x="{w//2}" y="{em_y}" text-anchor="middle" dominant-baseline="central"
        font-size="{em_sz}">{emoji}</text>

  <!-- Sparkle ring + mini stars -->
  {sparkle_svg}
  {mini_stars}

  <!-- Corner tone emojis -->
  <text x="{int(w*0.09)}" y="{int(h*0.175)}" text-anchor="middle"
        dominant-baseline="central" font-size="{max(10,int(w*0.048))}">{corners[0]}</text>
  <text x="{int(w*0.91)}" y="{int(h*0.175)}" text-anchor="middle"
        dominant-baseline="central" font-size="{max(10,int(w*0.048))}">{corners[1] if len(corners)>1 else corners[0]}</text>

  <!-- Text panel -->
  <rect x="{int(w*0.05)}" y="{pan_top}" width="{int(w*0.90)}" height="{pan_bot-pan_top}"
        fill="{bg_dk}" opacity="0.76" rx="10" ry="10"/>
  <rect x="{int(w*0.05)}" y="{pan_top}" width="{int(w*0.90)}" height="5"
        fill="{accent}" rx="3" ry="3"/>

  <!-- Campaign title -->
  <text x="{w//2}" y="{pan_top + int((pan_bot-pan_top)*0.30)}" text-anchor="middle"
        font-family="Arial,Helvetica,sans-serif" font-size="{max(14,int(w*0.048))}"
        font-weight="bold" fill="{txt_lt}" letter-spacing="0.5">{title}</text>

  <!-- Hero items -->
  <text x="{w//2}" y="{pan_top + int((pan_bot-pan_top)*0.65)}" text-anchor="middle"
        font-family="Arial,Helvetica,sans-serif" font-size="{max(10,int(w*0.030))}"
        fill="{accent}">{items}</text>

  <!-- CTA bar -->
  <rect y="{cta_top}" width="{w}" height="{h-cta_top}" fill="{accent}"/>
  <rect y="{cta_top}" width="{w}" height="3" fill="{bg_dk}" opacity="0.45"/>
  <text x="{w//2}" y="{cta_top + (h-cta_top)//2}" text-anchor="middle"
        dominant-baseline="central"
        font-family="Arial,Helvetica,sans-serif" font-size="{max(10,int(w*0.033))}"
        font-weight="bold" fill="{bg_dk}">→  {cta}  ←</text>
</svg>"""


# ── HTML templates ─────────────────────────────────────────────────────────

FB_TEMPLATE = """\
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Facebook Post Preview</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
          background:#f0f2f5; margin:0; padding:20px;
          display:flex; justify-content:center; }}
  .post {{ background:#fff; border-radius:8px; width:500px;
           box-shadow:0 1px 3px rgba(0,0,0,.2); overflow:hidden; }}
  .header {{ padding:12px 16px; display:flex; align-items:center; gap:10px; }}
  .avatar {{ width:40px; height:40px; border-radius:50%; flex-shrink:0;
             background:linear-gradient(135deg,#4a2c0a,#c87941);
             display:flex; align-items:center; justify-content:center;
             color:#fff; font-weight:700; font-size:18px; }}
  .page-info .name {{ font-weight:600; font-size:15px; color:#050505; }}
  .page-info .meta {{ font-size:13px; color:#65676b; }}
  .caption {{ padding:0 16px 12px; font-size:15px; line-height:1.6;
              color:#050505; white-space:pre-wrap; }}
  .img-wrap {{ width:100%; overflow:hidden; background:#e4e6eb; }}
  .stats {{ padding:6px 16px; font-size:13px; color:#65676b;
            border-top:1px solid #e4e6eb; border-bottom:1px solid #e4e6eb; }}
  .actions {{ padding:4px 16px; display:flex; gap:8px; }}
  .btn {{ flex:1; padding:8px; border:none; background:none; font-size:14px;
          color:#65676b; cursor:pointer; border-radius:4px; font-weight:600; }}
  .btn:hover {{ background:#f0f2f5; }}
  .poc {{ background:#1877f2; color:#fff; font-size:10px;
          padding:2px 7px; border-radius:4px; margin-left:6px; }}
</style>
</head>
<body>
<div class="post">
  <div class="header">
    <div class="avatar">S</div>
    <div class="page-info">
      <div class="name">Suto Café <span class="poc">PoC Preview</span></div>
      <div class="meta">Just now · 🌐 Public · Facebook Page</div>
    </div>
  </div>
  <div class="caption">{caption}</div>
  <div class="img-wrap">{svg}</div>
  <div class="stats">👍 ❤️ 😍 &nbsp;<strong>247 people</strong>&nbsp;·&nbsp;34 comments&nbsp;·&nbsp;18 shares</div>
  <div class="actions">
    <button class="btn">👍 Like</button>
    <button class="btn">💬 Comment</button>
    <button class="btn">↗ Share</button>
  </div>
</div>
</body></html>"""

IG_TEMPLATE = """\
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Instagram Post Preview</title>
<style>
  body {{ font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
          background:#fafafa; margin:0; padding:20px;
          display:flex; justify-content:center; }}
  .post {{ background:#fff; border:1px solid #dbdbdb; border-radius:3px; width:470px; }}
  .header {{ padding:14px; display:flex; align-items:center; gap:10px;
             border-bottom:1px solid #efefef; }}
  .avatar {{ width:32px; height:32px; border-radius:50%; flex-shrink:0;
             background:linear-gradient(45deg,#f09433,#e6683c,#dc2743,#cc2366,#bc1888);
             display:flex; align-items:center; justify-content:center;
             color:#fff; font-weight:700; font-size:14px; }}
  .username {{ font-weight:600; font-size:14px; color:#262626; }}
  .img-wrap {{ width:100%; aspect-ratio:1; overflow:hidden; background:#efefef; }}
  .actions {{ padding:8px 16px 0; }}
  .action-icons {{ font-size:24px; display:flex; gap:12px; margin-bottom:4px; }}
  .likes {{ font-weight:600; font-size:14px; padding:0 16px; color:#262626; }}
  .caption-area {{ padding:4px 16px 8px; font-size:14px; line-height:1.5;
                   color:#262626; white-space:pre-wrap; }}
  .comments {{ padding:0 16px 12px; font-size:14px; color:#8e8e8e; }}
  .time {{ padding:0 16px 12px; font-size:10px; color:#8e8e8e; text-transform:uppercase; }}
  .poc {{ background:linear-gradient(45deg,#405de6,#833ab4);
          color:#fff; font-size:10px; padding:2px 6px;
          border-radius:3px; margin-left:8px; }}
</style>
</head>
<body>
<div class="post">
  <div class="header">
    <div class="avatar">S</div>
    <div class="username">suto_cafe_siliguri <span class="poc">PoC Preview</span></div>
  </div>
  <div class="img-wrap">{svg}</div>
  <div class="actions"><div class="action-icons">❤️ 💬 ✈️</div></div>
  <div class="likes">1,247 likes</div>
  <div class="caption-area"><strong>suto_cafe_siliguri</strong> {caption}</div>
  <div class="comments">View all 89 comments</div>
  <div class="time">Just now · Siliguri, West Bengal</div>
</div>
</body></html>"""

WA_TEMPLATE = """\
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>WhatsApp Broadcast Preview</title>
<style>
  body {{ font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
          background:#e5ddd5; margin:0; padding:20px;
          background-image:url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23c5b8a8' fill-opacity='0.3'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/svg%3E");
          display:flex; flex-direction:column; align-items:center; }}
  .wa-header {{ background:#075e54; color:#fff; width:470px; padding:10px 16px;
               display:flex; align-items:center; gap:10px;
               border-radius:8px 8px 0 0; box-sizing:border-box; }}
  .wa-icon {{ font-size:28px; }}
  .wa-title {{ font-weight:600; font-size:15px; }}
  .wa-sub {{ font-size:12px; opacity:.8; }}
  .chat {{ width:470px; padding:14px 16px; box-sizing:border-box; }}
  .bcast-lbl {{ font-size:12px; color:#8e8e8e; text-align:center;
                background:rgba(255,255,255,.65); padding:4px 12px;
                border-radius:12px; margin-bottom:12px; }}
  .bubble {{ background:#dcf8c6; border-radius:8px 8px 8px 0;
             max-width:360px; box-shadow:0 1px 1px rgba(0,0,0,.1);
             overflow:hidden; position:relative; }}
  .bubble::before {{ content:''; position:absolute; left:-8px; top:0;
                     border:8px solid transparent;
                     border-right-color:#dcf8c6; border-top:0; }}
  .bubble-img {{ width:100%; display:block; }}
  .bubble-text {{ padding:8px 12px; font-size:14.5px; line-height:1.5;
                  color:#262626; white-space:pre-wrap; }}
  .time-read {{ text-align:right; font-size:11px; color:#8e8e8e; padding:0 10px 8px; }}
  .poc {{ background:#25d366; color:#fff; font-size:10px;
          padding:2px 7px; border-radius:4px; margin-left:8px; }}
</style>
</head>
<body>
<div class="wa-header">
  <div class="wa-icon">📱</div>
  <div>
    <div class="wa-title">Suto Café Broadcast <span class="poc">PoC Preview</span></div>
    <div class="wa-sub">1,240 subscribers · WhatsApp Business API (WATI)</div>
  </div>
</div>
<div class="chat">
  <div class="bcast-lbl">📢 Broadcast message to all subscribers</div>
  <div class="bubble">
    <div class="bubble-img">{svg}</div>
    <div class="bubble-text">{caption}</div>
    <div class="time-read">Just now ✓✓</div>
  </div>
</div>
</body></html>"""


class PublishingAgent:

    def run(self, brief: CampaignBrief, copy: CopyVariants,
            banner: BannerResult) -> PublishResult:
        ts          = datetime.now().strftime("%Y%m%d_%H%M%S")
        campaign_id = f"SUTO-{ts}"
        post_urls   = {}
        published   = []

        os.makedirs(config.POSTS_DIR, exist_ok=True)

        # Pre-generate SVGs for each aspect ratio
        svg_square   = _make_svg(brief, w=600, h=600)   # IG 1:1
        svg_portrait = _make_svg(brief, w=600, h=500)   # FB 6:5
        svg_wa       = _make_svg(brief, w=400, h=400)   # WA square

        def _cap(channel: str) -> str:
            variants = getattr(copy, channel, {})
            raw = variants.get(copy.selected, variants.get("b", ""))
            return _coerce_text(raw)

        # ── Facebook ───────────────────────────────────────────────────────
        if "facebook" in brief.channels:
            html = FB_TEMPLATE.format(caption=_cap("facebook"), svg=svg_portrait)
            path = os.path.join(config.POSTS_DIR, f"{ts}_facebook.html")
            with open(path, "w", encoding="utf-8") as f:
                f.write(html)
            post_urls["facebook"] = path
            published.append("facebook")

        # ── Instagram ──────────────────────────────────────────────────────
        if "instagram" in brief.channels:
            html = IG_TEMPLATE.format(caption=_cap("instagram"), svg=svg_square)
            path = os.path.join(config.POSTS_DIR, f"{ts}_instagram.html")
            with open(path, "w", encoding="utf-8") as f:
                f.write(html)
            post_urls["instagram"] = path
            published.append("instagram")

        # ── WhatsApp ───────────────────────────────────────────────────────
        if "whatsapp" in brief.channels:
            html = WA_TEMPLATE.format(caption=_cap("whatsapp"), svg=svg_wa)
            path = os.path.join(config.POSTS_DIR, f"{ts}_whatsapp.html")
            with open(path, "w", encoding="utf-8") as f:
                f.write(html)
            post_urls["whatsapp"] = path
            published.append("whatsapp")

        return PublishResult(
            campaign_id=campaign_id,
            channels_published=published,
            post_urls=post_urls,
            mock_post_ids={ch: f"mock_{ch}_{random.randint(10000,99999)}"
                           for ch in published},
            reach_estimate=random.randint(800, 4200)
        )
