"""
Social Media Copywriter Agent
Uses Groq LLM for real copy. Falls back to rich mock variants.
Generates 3 variants per channel: Hindi-heavy, English-punchy, Mixed.
"""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from typing import Dict, Any
from config import config
from agents.content_strategy_agent import CampaignBrief


def _coerce_text(v: Any) -> str:
    """
    Groq sometimes returns variant values as {"text": "...", "image": ""}
    instead of a plain string. Always return a plain string.
    """
    if isinstance(v, dict):
        return str(v.get("text") or v.get("caption") or v.get("content") or "").strip()
    return str(v).strip() if v else ""


@dataclass
class CopyVariants:
    facebook: Dict[str, str]    # {a, b, c}
    instagram: Dict[str, str]
    whatsapp: Dict[str, str]
    selected: str               # "a" | "b" | "c"
    selection_reason: str
    llm_source: str

    def best_copy(self, channel: str) -> str:
        variants = getattr(self, channel, {})
        return variants.get(self.selected, variants.get("b", ""))


COPY_SYSTEM = """You are a social media copywriter for Suto Café, Siliguri.
Brand voice: warm, local, youthful. Mix Hindi/Bengali naturally. Short punchy sentences.
Given a campaign brief, generate copy for facebook, instagram, and whatsapp.
Each channel needs 3 variants: a (Hindi-heavy/emotional), b (English/punchy/youth), c (mixed/story/family).

Platform format rules:
- Instagram: 3-5 sentences, 5-8 emojis woven in, 10-15 hashtags on a new line at the end, end with a question or tag-a-friend CTA.
- Facebook: 4-6 sentences, storytelling/warm tone, 3-5 hashtags at end, include "Hill Cart Road" or area hint.
- WhatsApp: 2-3 short lines MAX, zero hashtags, conversational like a friend texting, mention a price (e.g. "from ₹130").

CRITICAL OUTPUT RULES:
1. Every variant value MUST be a plain text string. Do NOT wrap it in an object or dict.
2. Do NOT include any "image", "media", or "url" keys anywhere.
3. Return ONLY a JSON object shaped exactly like this:
{
  "facebook":  {"a": "<plain text>", "b": "<plain text>", "c": "<plain text>"},
  "instagram": {"a": "<plain text>", "b": "<plain text>", "c": "<plain text>"},
  "whatsapp":  {"a": "<plain text>", "b": "<plain text>", "c": "<plain text>"},
  "selected": "b",
  "selection_reason": "<one sentence>"
}"""


class CopywriterAgent:

    def run(self, brief: CampaignBrief) -> CopyVariants:
        if config.llm_available:
            try:
                return self._groq_copy(brief)
            except Exception as e:
                print(f"[Copywriter] Groq error: {e}, using mock")
        return self._mock_copy(brief)

    def _groq_copy(self, brief: CampaignBrief) -> CopyVariants:
        from groq import Groq
        client = Groq(api_key=config.GROQ_API_KEY)
        prompt = f"""
Campaign brief:
Theme: {brief.theme_display}
Hero items: {', '.join(brief.hero_items)}
Tone: {brief.tone}
Key messages: {'; '.join(brief.key_messages)}
Local reference: {brief.local_reference}
Hashtags: {' '.join(brief.hashtags_primary + brief.hashtags_local)}
CTA: {brief.cta}
"""
        resp = client.chat.completions.create(
            model=config.GROQ_MODEL,
            messages=[
                {"role": "system", "content": COPY_SYSTEM},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.85
        )
        data = json.loads(resp.choices[0].message.content)

        def _sanitise_channel(raw: dict) -> dict:
            """Ensure every variant value is a plain string."""
            return {k: _coerce_text(v) for k, v in raw.items()} if isinstance(raw, dict) else {}

        return CopyVariants(
            facebook=_sanitise_channel(data.get("facebook", {})),
            instagram=_sanitise_channel(data.get("instagram", {})),
            whatsapp=_sanitise_channel(data.get("whatsapp", {})),
            selected=data.get("selected", "b"),
            selection_reason=data.get("selection_reason", "Best balance of local feel and reach"),
            llm_source="groq"
        )

    def _mock_copy(self, brief: CampaignBrief) -> CopyVariants:
        item1 = brief.hero_items[0] if brief.hero_items else "Suto Special Frappe"
        item2 = brief.hero_items[1] if len(brief.hero_items) > 1 else "Cold Coffee"
        tags = " ".join(brief.hashtags_primary + brief.hashtags_local)

        templates = {
            "cozy": {
                "ig_a": f"Baarish + {item1} = ❤️\n\nSiliguri ki thand mein kuch warm chahiye? Humara {item1} bilkul wahi hai jo aapko chahiye 🍜☕\n\nAao, baith jao, feel karo ghar jaisi warmth 🏠✨\n\nAapka favourite corner kaun sa hai? 👇\n{tags}",
                "ig_b": f"Rain outside. {item1} inside. 🌧️☕\n\nSuto Café is your cozy escape on rainy Siliguri afternoons. Pull up a chair, we've saved your spot 🪑\n\nTag a friend who needs a warm break today! 💛\n{tags}",
                "ig_c": f"Siliguri ki baarish ka ek alag hi maza hai — especially jab saath ho humara {item1} 🌧️🍜\n\nFamily ho, dost ho, ya sirf khud — Suto Café mein sabka swagat hai 🤗\n\nKaun aa raha hai aaj? ☔\n{tags}",
                "fb_a": f"🌧️ Baarish ka din aur ghar se bahar nikalna mushkil? Suto Café mein aa jao!\n\nHumara {item1} aur warm corner tumhara intezaar kar raha hai. Siliguri ki baarish aur ek perfect hot drink — better combo kya hoga?\n\nAao, feel karo. Tum deserve karte ho yeh break ☕\n#{brief.hashtags_primary[0] if brief.hashtags_primary else 'SutoCafe'} #Siliguri",
                "fb_b": f"Your monsoon HQ is here. 🌧️\n\nRainy Siliguri afternoons hit different when you're at Suto Café with a hot {item1} in hand. We're cozy, we're warm, and we're waiting for you.\n\nFind us on Hill Cart Road area. Open all day! ☕\n{' '.join(brief.hashtags_primary[:3])}",
                "fb_c": f"Nothing beats a rainy afternoon at a cozy café. ☔\n\nAt Suto Café, we've got your favourite hot drinks and comfort food ready — from our signature {item1} to warm bites that feel like a hug. Bring the family, bring your friends, or just bring yourself.\n\nYou deserve this break today! 🏡\n{' '.join(brief.hashtags_primary[:3])}",
                "wa_a": f"Baarish ho rahi hai Siliguri mein! ☔\nHumara {item1} + cozy corner ready hai.\nAa jao — ₹{110 if 'Maggi' in item1 else 130} se shuru 🍜\nSuto Café mein milte hain!",
                "wa_b": f"Rainy day in Siliguri? 🌧️\nCome to Suto Café — hot {item1} waiting for you!\nPerfect comfort food from ₹{110 if 'Maggi' in item1 else 120} 😋\nSee you soon!",
                "wa_c": f"Aaj baarish mein Suto Café plan karo! ☔\n{item1} + {item2} — sab ready hai.\nFamily aur dosto ke saath aao, warm raho 🤗"
            },
            "refreshing": {
                "ig_a": f"Garmi mein yeh piya? ✅ Life sorted! ☀️\n\nSiliguri ki {brief.local_reference} mein sirf ek hi solution hai — Suto ka {item1} 🧊❄️\n\nFriends ko tag karo jo ab bhi suffer kar rahe hain! 👇\n{tags}",
                "ig_b": f"HOT outside. COLD inside. 🥵➡️😎\n\nSuto Special Frappe hits different when Siliguri temps hit {35 if 'hot' in brief.campaign_theme else 30}° 🌡️❄️\n\nTag your heat-survivor squad below! 👇\n{tags}",
                "ig_c": f"Siliguri mein garmi ka ek hi ilaaj — Suto Café ka {item1}! ☀️🧊\n\nPerfect for the whole family — kids, parents, everyone loves a cold treat on hot days 🎉\n\nKaun aa raha hai aaj? Drop a ❄️ in the comments!\n{tags}",
                "fb_a": f"☀️ {brief.local_reference} heat finally met its match!\n\nHumara {item1} aur {item2} is summer mein jo relief dete hain — woh koi aur nahi de sakta. Siliguri ka sabse refreshing café experience hamare yahan hai.\n\nAao, ek ghante ke liye AC mein baith jao aur kuch cold peeo 🧊\n{' '.join(brief.hashtags_primary[:3])}",
                "fb_b": f"Beat the Siliguri heat the right way. ☀️\n\nOur {item1} is crafted to cool you down and make your day better. One sip and the summer doesn't feel so bad.\n\nCome in, chill out, stay a while. Hill Cart Road area — you know where to find us! 🧊\n{' '.join(brief.hashtags_primary[:3])}",
                "fb_c": f"Summers in Siliguri are no joke — but Suto Café makes them bearable! 😄☀️\n\nOur cold {item1} and chilled {item2} are the perfect antidote to afternoon heat. Great for the family, awesome with friends, or just a solo chill session.\n\nCome over and cool down with us today! ❄️\n{' '.join(brief.hashtags_primary[:3])}",
                "wa_a": f"Siliguri ki garmi mein aa gaye? 😅\nHumara {item1} bilkul ready hai! 🧊\n₹{180} mein yeh beat karo heat 🔥\nSuto Café mein milte hain!",
                "wa_b": f"Too hot in Siliguri? 🥵\nSuto's {item1} is the answer! ❄️\nCooling you down from ₹130 onwards 😎\nCome on in!",
                "wa_c": f"Garmi ka solution = Suto Café! ☀️🧊\n{item1} + {item2} — perfect summer duo\nFamily ke saath aa jao, sab ke liye kuch na kuch hai 😄"
            },
            "festive": {
                "ig_a": f"🎉 {brief.theme_display}! 🎉\n\nSuto Café mein tyohaar ka maza alag hi hota hai! Apne special {item1} ke saath celebrate karo yeh khaas din 🥳\n\nApne favourite log ko tag karo aur plan banao! ✨\n{tags}",
                "ig_b": f"Festival season hits different at Suto Café! 🎊\n\n{item1} + {item2} + your favourite people = the perfect celebration combo 🥂✨\n\nTag who you're celebrating with! 👇\n{tags}",
                "ig_c": f"Yeh tyohaar yaadon mein rehega — Suto Café ke saath! 🎉\n\nParivaar ho ya dost, sabke liye humara {item1} ready hai 🥰\n\nAao celebrate karte hain! ✨\n{tags}",
                "fb_a": f"🎊 {brief.theme_display} pe Suto Café ka vishesh swagat!\n\nIs khaas mauqe par humara {item1} aur {item2} ke saath celebrate karo. Siliguri ka sabse cozy café aapka intezaar kar raha hai 🎉\n\nApne family aur dost ke saath aao! ✨\n{' '.join(brief.hashtags_primary[:3])}",
                "fb_b": f"Celebrating {brief.theme_display} the Suto way! 🎉\n\nBring your people, pick your drinks, make it special. Our {item1} is the perfect companion for this wonderful occasion.\n\nCome visit us — we'd love to be part of your celebration! 🥂\n{' '.join(brief.hashtags_primary[:3])}",
                "fb_c": f"Every festival is better when shared with good food and good people. 🎊\n\nAt Suto Café, we've got the perfect setting for your {brief.theme_display} celebration — from our famous {item1} to a welcoming atmosphere for the whole family.\n\nCome make memories with us! ✨\n{' '.join(brief.hashtags_primary[:3])}",
                "wa_a": f"🎉 {brief.theme_display} Mubarak! 🎊\nSuto Café mein celebrate karo!\n{item1} aur {item2} ready hain 😍\nAao milte hain!",
                "wa_b": f"Happy {brief.theme_display}! 🎉\nCome celebrate at Suto Café!\nSpecial drinks & food waiting 🥂\nSee you soon!",
                "wa_c": f"Tyohaar pe Suto Café plan karo! 🎊\n{item1} + {item2} — perfect celebration combo\nFamily ke saath zaroor aana 😊"
            },
        }

        tone_key = "cozy" if brief.tone in ["cozy", "warm"] else \
                   "refreshing" if brief.tone in ["refreshing", "energetic", "playful"] else "festive"
        t = templates.get(tone_key, templates["refreshing"])

        return CopyVariants(
            facebook={"a": t["fb_a"], "b": t["fb_b"], "c": t["fb_c"]},
            instagram={"a": t["ig_a"], "b": t["ig_b"], "c": t["ig_c"]},
            whatsapp={"a": t["wa_a"], "b": t["wa_b"], "c": t["wa_c"]},
            selected="b",
            selection_reason="Variant B: best balance of English readability + local flavor for max reach",
            llm_source="mock"
        )
