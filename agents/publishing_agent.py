"""
Publishing Agent — PoC version.
Generates realistic HTML previews of Facebook, Instagram, and WhatsApp posts.
In production: calls Meta Graph API + WATI WhatsApp API.
"""
from __future__ import annotations
import os
import random
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List
from config import config
from agents.content_strategy_agent import CampaignBrief
from agents.copywriter_agent import CopyVariants
from agents.banner_agent import BannerResult


@dataclass
class PublishResult:
    campaign_id: str
    channels_published: List[str]
    post_urls: Dict[str, str]   # channel -> HTML preview path
    mock_post_ids: Dict[str, str]
    reach_estimate: int
    source: str = "mock_html_preview"

    def summary(self) -> str:
        return (f"Published to {', '.join(self.channels_published)} | "
                f"Est. reach: {self.reach_estimate:,} | Campaign: {self.campaign_id}")


FB_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Facebook Post Preview — {cafe}</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
          background: #f0f2f5; margin: 0; padding: 20px; display: flex;
          justify-content: center; }}
  .post {{ background: white; border-radius: 8px; width: 500px; padding: 0;
           box-shadow: 0 1px 3px rgba(0,0,0,0.2); overflow: hidden; }}
  .header {{ padding: 12px 16px; display: flex; align-items: center; gap: 10px; }}
  .avatar {{ width: 40px; height: 40px; border-radius: 50%;
             background: linear-gradient(135deg, #4a2c0a, #c87941);
             display: flex; align-items: center; justify-content: center;
             color: white; font-weight: bold; font-size: 18px; }}
  .page-info .name {{ font-weight: 600; font-size: 15px; color: #050505; }}
  .page-info .meta {{ font-size: 13px; color: #65676b; }}
  .caption {{ padding: 0 16px 12px; font-size: 15px; line-height: 1.5;
              color: #050505; white-space: pre-wrap; }}
  .image {{ width: 100%; aspect-ratio: 1.2; object-fit: cover;
            background: {img_bg}; display: flex; align-items: center;
            justify-content: center; font-size: 80px; }}
  img.banner {{ width: 100%; display: block; }}
  .actions {{ padding: 4px 16px; border-top: 1px solid #e4e6eb; display: flex;
              gap: 8px; }}
  .btn {{ flex: 1; padding: 8px; border: none; background: none; font-size: 15px;
          color: #65676b; cursor: pointer; border-radius: 4px; font-weight: 600; }}
  .btn:hover {{ background: #f0f2f5; }}
  .stats {{ padding: 6px 16px; font-size: 13px; color: #65676b;
             border-bottom: 1px solid #e4e6eb; }}
  .poc-badge {{ background: #1877f2; color: white; font-size: 11px;
                padding: 2px 8px; border-radius: 4px; }}
</style>
</head>
<body>
<div class="post">
  <div class="header">
    <div class="avatar">S</div>
    <div class="page-info">
      <div class="name">{cafe} <span class="poc-badge">PoC Preview</span></div>
      <div class="meta">Just now · 🌐 Public · Facebook Page</div>
    </div>
  </div>
  <div class="caption">{caption}</div>
  {img_tag}
  <div class="stats">👍 ❤️ 😍 &nbsp; <strong>247 people</strong> &nbsp;·&nbsp; 34 comments &nbsp;·&nbsp; 18 shares</div>
  <div class="actions">
    <button class="btn">👍 Like</button>
    <button class="btn">💬 Comment</button>
    <button class="btn">↗ Share</button>
  </div>
</div>
</body></html>"""

IG_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Instagram Post Preview — {cafe}</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
          background: #fafafa; margin: 0; padding: 20px;
          display: flex; justify-content: center; }}
  .post {{ background: white; border: 1px solid #dbdbdb; border-radius: 3px;
           width: 470px; }}
  .header {{ padding: 14px; display: flex; align-items: center; gap: 10px;
             border-bottom: 1px solid #efefef; }}
  .avatar {{ width: 32px; height: 32px; border-radius: 50%;
             background: linear-gradient(45deg, #f09433, #e6683c, #dc2743, #cc2366, #bc1888);
             display: flex; align-items: center; justify-content: center;
             color: white; font-weight: bold; font-size: 14px; }}
  .username {{ font-weight: 600; font-size: 14px; color: #262626; }}
  .image-area {{ width: 100%; background: {img_bg}; aspect-ratio: 1;
                 display: flex; align-items: center; justify-content: center;
                 font-size: 120px; overflow: hidden; }}
  img.banner {{ width: 100%; display: block; }}
  .actions {{ padding: 8px 16px 0; }}
  .action-icons {{ font-size: 24px; display: flex; gap: 12px; margin-bottom: 4px; }}
  .likes {{ font-weight: 600; font-size: 14px; padding: 0 16px; color: #262626; }}
  .caption-area {{ padding: 4px 16px 8px; font-size: 14px; line-height: 1.4;
                   color: #262626; white-space: pre-wrap; }}
  .hashtags {{ color: #00376b; }}
  .comments {{ padding: 0 16px 12px; font-size: 14px; color: #8e8e8e; }}
  .time {{ padding: 0 16px 12px; font-size: 10px; color: #8e8e8e; text-transform: uppercase; }}
  .poc-badge {{ background: linear-gradient(45deg, #405de6, #833ab4);
                color: white; font-size: 10px; padding: 2px 6px;
                border-radius: 3px; margin-left: 8px; }}
</style>
</head>
<body>
<div class="post">
  <div class="header">
    <div class="avatar">S</div>
    <div class="username">suto_cafe_siliguri <span class="poc-badge">PoC Preview</span></div>
  </div>
  <div class="image-area">{img_content}</div>
  <div class="actions">
    <div class="action-icons">❤️ 💬 ✈️</div>
  </div>
  <div class="likes">1,247 likes</div>
  <div class="caption-area"><strong>suto_cafe_siliguri</strong> {caption}</div>
  <div class="comments">View all 89 comments</div>
  <div class="time">Just now · Siliguri, West Bengal</div>
</div>
</body></html>"""

WA_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>WhatsApp Broadcast Preview</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
          background: #e5ddd5; margin: 0; padding: 20px;
          background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23c5b8a8' fill-opacity='0.3'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
          display: flex; flex-direction: column; align-items: center; }}
  .header {{ background: #075e54; color: white; width: 470px; padding: 10px 16px;
             display: flex; align-items: center; gap: 10px; border-radius: 8px 8px 0 0; }}
  .wa-icon {{ font-size: 28px; }}
  .header-text .title {{ font-weight: 600; font-size: 15px; }}
  .header-text .sub {{ font-size: 12px; opacity: 0.8; }}
  .chat-area {{ background: transparent; width: 470px; padding: 16px;
               min-height: 200px; }}
  .bubble {{ background: #dcf8c6; border-radius: 8px 8px 8px 0; padding: 8px 12px;
             max-width: 340px; box-shadow: 0 1px 1px rgba(0,0,0,0.1);
             font-size: 14.5px; line-height: 1.5; color: #262626;
             white-space: pre-wrap; position: relative; }}
  .bubble::before {{ content: ''; position: absolute; left: -8px; top: 0;
                     border: 8px solid transparent;
                     border-right-color: #dcf8c6; border-top: 0; }}
  .time-read {{ text-align: right; font-size: 11px; color: #8e8e8e; margin-top: 4px; }}
  .broadcast-label {{ font-size: 12px; color: #8e8e8e; margin-top: 8px;
                      text-align: center; background: rgba(255,255,255,0.6);
                      padding: 4px 12px; border-radius: 12px; }}
  .poc-label {{ background: #25d366; color: white; font-size: 10px;
                padding: 2px 8px; border-radius: 4px; margin-left: 8px; }}
</style>
</head>
<body>
<div class="header">
  <div class="wa-icon">📱</div>
  <div class="header-text">
    <div class="title">Suto Café Broadcast <span class="poc-label">PoC Preview</span></div>
    <div class="sub">1,240 subscribers · WhatsApp Business API (WATI)</div>
  </div>
</div>
<div class="chat-area">
  <div class="broadcast-label">📢 Broadcast message to all subscribers</div>
  <br>
  <div class="bubble">
    {caption}
    <div class="time-read">Just now ✓✓</div>
  </div>
</div>
</body></html>"""


class PublishingAgent:

    def run(self, brief: CampaignBrief, copy: CopyVariants,
            banner: BannerResult) -> PublishResult:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        campaign_id = f"SUTO-{ts}"
        post_urls = {}
        published = []

        # Determine banner image tag
        img_bg = "#c87941"
        img_tag_fb = f'<img class="banner" src="{banner.square_path}" alt="Campaign Banner">'
        img_tag_ig = f'<img class="banner" src="{banner.square_path}" alt="Campaign Banner">'

        # Facebook
        if "facebook" in brief.channels:
            fb_caption = copy.facebook.get(copy.selected, copy.facebook.get("b", ""))
            html = FB_TEMPLATE.format(
                cafe="Suto Café",
                caption=fb_caption,
                img_bg=img_bg,
                img_tag=img_tag_fb
            )
            path = os.path.join(config.POSTS_DIR, f"{ts}_facebook.html")
            with open(path, "w", encoding="utf-8") as f:
                f.write(html)
            post_urls["facebook"] = path
            published.append("facebook")

        # Instagram
        if "instagram" in brief.channels:
            ig_caption = copy.instagram.get(copy.selected, copy.instagram.get("b", ""))
            html = IG_TEMPLATE.format(
                cafe="Suto Café",
                caption=ig_caption,
                img_bg=img_bg,
                img_content=f'<img class="banner" src="{banner.square_path}" alt="Banner">'
            )
            path = os.path.join(config.POSTS_DIR, f"{ts}_instagram.html")
            with open(path, "w", encoding="utf-8") as f:
                f.write(html)
            post_urls["instagram"] = path
            published.append("instagram")

        # WhatsApp
        if "whatsapp" in brief.channels:
            wa_caption = copy.whatsapp.get(copy.selected, copy.whatsapp.get("b", ""))
            html = WA_TEMPLATE.format(caption=wa_caption)
            path = os.path.join(config.POSTS_DIR, f"{ts}_whatsapp.html")
            with open(path, "w", encoding="utf-8") as f:
                f.write(html)
            post_urls["whatsapp"] = path
            published.append("whatsapp")

        return PublishResult(
            campaign_id=campaign_id,
            channels_published=published,
            post_urls=post_urls,
            mock_post_ids={ch: f"mock_{ch}_{random.randint(10000,99999)}" for ch in published},
            reach_estimate=random.randint(800, 4200)
        )
