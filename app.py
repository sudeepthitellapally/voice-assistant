import streamlit as st
import requests
import io
import base64
import tempfile
import os
import json
import re
from datetime import date, datetime
from gtts import gTTS
from groq import Groq

st.set_page_config(page_title="Klyra", page_icon="🎙️", layout="centered")
def get_theme_css(dark_mode: bool) -> str:
    if dark_mode:
        bg_grad        = "linear-gradient(160deg, #1e1b17 0%, #16140f 50%, #0f0d0a 100%)"
        sidebar_bg     = "#211e1a"
        text_main      = "#e8ddd4"
        text_sub       = "#a89880"
        text_cap       = "#786858"
        bubble_ai_bg   = "#2a2520"
        bubble_ai_border = "#3a3530"
        bubble_ai_text = "#e8ddd4"
        input_bg       = "#2a2520"
        input_border   = "#3a3530"
        input_text     = "#e8ddd4"
        transcript_bg  = "#2a1e15"
        transcript_border = "#5a3a28"
        divider        = "#3a3530"
        empty_col      = "#6a5a48"
        empty_sub      = "#504030"
    else:
        bg_grad        = "linear-gradient(160deg, #fdf8f3 0%, #f0e9e0 50%, #e8ddd4 100%)"
        sidebar_bg     = "#fefcf9"
        text_main      = "#2d2a26"
        text_sub       = "#a89880"
        text_cap       = "#c8b8a8"
        bubble_ai_bg   = "#fff"
        bubble_ai_border = "#e8e0d8"
        bubble_ai_text = "#2d2a26"
        input_bg       = "#fff"
        input_border   = "#e0d8d0"
        input_text     = "#2d2a26"
        transcript_bg  = "#fff8f2"
        transcript_border = "#f0d8c8"
        divider        = "#e8e0d8"
        empty_col      = "#b8a898"
        empty_sub      = "#c8b8a8"

    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@300;400;500;600;700;800&family=Nunito+Sans:wght@300;400;600&display=swap');

*, *::before, *::after {{ box-sizing: border-box; }}

html, body, [class*="css"] {{
    font-family: 'Nunito Sans', sans-serif;
    color: {text_main};
}}
.stApp {{
    background: {bg_grad};
    min-height: 100vh;
}}

[data-testid="stSidebar"] {{
    background: {sidebar_bg} !important;
    border-right: 1px solid {divider} !important;
    min-width: 240px !important;
    max-width: 260px !important;
}}
[data-testid="stSidebar"] * {{ color: {text_sub} !important; }}

[data-testid="collapsedControl"],
[data-testid="stSidebarCollapseButton"],
button[aria-label="Close sidebar"],
button[aria-label="Open sidebar"],
button[aria-label="collapse sidebar"],
section[data-testid="stSidebar"] > div:first-child button {{
    display: none !important;
    visibility: hidden !important;
    pointer-events: none !important;
    width: 0 !important;
    height: 0 !important;
    overflow: hidden !important;
}}

.vox-header {{ text-align: center; padding: 2rem 0 0.8rem; }}
.vox-avatar {{
    width: 68px; height: 68px;
    background: linear-gradient(135deg, #e07b4f, #d4956a);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 30px; margin: 0 auto 1rem;
    box-shadow: 0 8px 24px rgba(224,123,79,0.3);
}}
.vox-wordmark {{
    font-family: 'Nunito', sans-serif;
    font-size: 2.2rem; font-weight: 800;
    color: {text_main}; letter-spacing: 2px;
}}
.vox-wordmark span {{ color: #e07b4f; }}
.vox-tagline {{
    font-size: 12px; letter-spacing: 3px;
    text-transform: uppercase; color: {text_sub};
    margin-top: 4px; font-weight: 600;
}}
.vox-line {{
    width: 60px; height: 2px;
    background: linear-gradient(90deg, transparent, #e07b4f, transparent);
    margin: 1rem auto 0; border-radius: 2px;
}}

.chat-wrap {{
    max-height: 50vh; overflow-y: auto;
    padding: 0.5rem 0.2rem; margin-bottom: 0.5rem;
    scrollbar-width: thin; scrollbar-color: #d4c9be transparent;
}}
.bubble-user {{
    display: flex; justify-content: flex-end;
    margin: 10px 0; animation: fadeUp 0.25s ease;
}}
.bubble-user span {{
    background: linear-gradient(135deg, #e07b4f, #d4956a);
    color: #fff; padding: 12px 18px;
    border-radius: 22px 22px 5px 22px;
    max-width: 78%; font-size: 14.5px; line-height: 1.6;
    font-weight: 600; box-shadow: 0 4px 16px rgba(224,123,79,0.25);
}}
.bubble-ai {{
    display: flex; justify-content: flex-start;
    margin: 10px 0; align-items: flex-end; gap: 8px;
    animation: fadeUp 0.25s ease;
}}
.ai-icon {{
    width: 32px; height: 32px;
    background: linear-gradient(135deg, #6b9fd4, #5b8fc4);
    border-radius: 50%; display: flex; align-items: center;
    justify-content: center; font-size: 15px; flex-shrink: 0;
    box-shadow: 0 3px 10px rgba(107,159,212,0.3);
}}
.bubble-ai span {{
    background: {bubble_ai_bg}; border: 1px solid {bubble_ai_border}; color: {bubble_ai_text};
    padding: 12px 18px; border-radius: 22px 22px 22px 5px;
    max-width: 75%; font-size: 14.5px; line-height: 1.6;
    box-shadow: 0 3px 12px rgba(0,0,0,0.06);
}}
@keyframes fadeUp {{
    from {{ opacity: 0; transform: translateY(10px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}
.empty-state {{ text-align: center; padding: 3rem 1rem 2rem; color: {empty_col}; }}
.empty-icon  {{ font-size: 3rem; margin-bottom: 0.8rem; }}
.empty-text  {{ font-size: 14px; font-weight: 700; letter-spacing: 0.5px; }}
.empty-sub   {{ font-size: 12px; margin-top: 4px; color: {empty_sub}; }}

.transcript-box {{
    background: {transcript_bg}; border: 1.5px solid {transcript_border};
    border-left: 4px solid #e07b4f; border-radius: 12px;
    padding: 10px 16px; font-size: 13px; color: {text_sub};
    margin: 8px 0 12px; font-style: italic;
}}

.emotion-badge {{
    display: inline-flex; align-items: center; gap: 8px;
    border-radius: 20px; padding: 6px 16px;
    font-size: 13px; font-weight: 700;
    letter-spacing: 0.5px; margin: 6px 0 10px; border: 1.5px solid;
}}
.emotion-happy   {{ background: #fffbe6; border-color: #f5c842; color: #b8860b; }}
.emotion-sad     {{ background: #eef3fb; border-color: #7aa8e8; color: #1a5fa8; }}
.emotion-angry   {{ background: #fff0ef; border-color: #f08080; color: #c0392b; }}
.emotion-neutral {{ background: #f0f0f0; border-color: #aaa; color: #555; }}
.emotion-fear    {{ background: #f5eeff; border-color: #c39bd3; color: #7d3c98; }}
.emotion-disgust {{ background: #efffef; border-color: #82e082; color: #1e8449; }}
.emotion-surprise{{ background: #fff4e6; border-color: #f0a040; color: #c06000; }}
.emotion-excited {{ background: #fff0fc; border-color: #f080d0; color: #9b008b; }}

.vox-divider {{ border: none; border-top: 1.5px solid {divider}; margin: 0.8rem 0; }}

.stTextInput > div > div > input {{
    background: {input_bg} !important; border: 1.5px solid {input_border} !important;
    border-radius: 14px !important; color: {input_text} !important;
    font-family: 'Nunito Sans', sans-serif !important; font-size: 14px !important;
    padding: 10px 16px !important; box-shadow: 0 2px 8px rgba(0,0,0,0.04) !important;
    transition: border-color 0.2s ease !important;
}}
.stTextInput > div > div > input:focus {{
    border-color: #e07b4f !important;
    box-shadow: 0 0 0 3px rgba(224,123,79,0.12) !important;
}}

div[data-testid="stAudioInput"] {{
    background: transparent !important;
    border: none !important;
    padding: 4px 0 0 0 !important;
    margin: 0 !important;
}}
div[data-testid="stAudioInput"] > label {{ display: none !important; }}

div[data-testid="stAudioInput"] > div > button:first-child {{
    background: {input_bg} !important;
    border: 2.5px solid #e07b4f !important;
    border-radius: 50% !important;
    width: 56px !important; height: 56px !important;
    min-width: 56px !important;
    color: #e07b4f !important; font-size: 22px !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 16px rgba(224,123,79,0.25) !important;
    cursor: pointer !important;
    display: flex !important; align-items: center !important;
    justify-content: center !important;
    padding: 0 !important;
    margin: 0 auto !important;
}}
div[data-testid="stAudioInput"] > div > button:first-child:hover {{
    background: #e07b4f !important; color: #fff !important;
    box-shadow: 0 6px 22px rgba(224,123,79,0.4) !important;
    transform: scale(1.06) !important;
}}

div[data-testid="stAudioInput"] > div {{
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    gap: 8px !important;
}}
div[data-testid="stAudioInput"] audio {{
    width: 100% !important;
    margin-top: 6px !important;
    border-radius: 8px !important;
}}

.stButton > button {{
    background: linear-gradient(135deg, #d4622a, #e07b4f) !important;
    color: #ffffff !important; border: 2.5px solid #b84f20 !important;
    border-radius: 14px !important;
    font-family: 'Nunito', sans-serif !important; font-size: 15px !important;
    font-weight: 800 !important; height: 52px !important; padding: 0 28px !important;
    transition: all 0.2s ease !important; letter-spacing: 0.3px !important;
    box-shadow: 0 5px 18px rgba(180,70,20,0.45) !important; white-space: nowrap !important;
    text-shadow: 0 1px 2px rgba(0,0,0,0.25) !important;
}}
.stButton > button:hover {{
    background: linear-gradient(135deg, #c05520, #d4622a) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(180,70,20,0.55) !important;
    border-color: #a04010 !important;
}}
.stButton > button:active {{
    transform: translateY(0px) !important;
    box-shadow: 0 3px 10px rgba(180,70,20,0.4) !important;
}}
[data-testid="stSidebar"] .stButton > button {{
    background: linear-gradient(135deg, #d4622a, #e07b4f) !important;
    color: #ffffff !important;
    box-shadow: 0 3px 10px rgba(180,70,20,0.35) !important;
    border: 2px solid #b84f20 !important;
    font-weight: 800 !important;
}}

.speaking-badge {{
    display: inline-flex; align-items: center; gap: 6px;
    background: #fff0e8; border: 1.5px solid #f0d0b8;
    border-radius: 20px; padding: 5px 14px;
    font-size: 12px; color: #e07b4f; font-weight: 700;
    letter-spacing: 0.5px; margin: 6px 0;
}}
.pulse-dot {{
    width: 8px; height: 8px; background: #e07b4f;
    border-radius: 50%; animation: pulse 1s infinite;
}}
@keyframes pulse {{
    0%, 100% {{ opacity: 1; transform: scale(1); }}
    50%       {{ opacity: 0.4; transform: scale(0.7); }}
}}
.cmd-badge {{
    display: inline-flex; align-items: center; gap: 6px;
    background: #e8f0fe; border: 1.5px solid #7baaf7;
    border-radius: 20px; padding: 5px 14px;
    font-size: 12px; color: #1a73e8; font-weight: 700;
    letter-spacing: 0.5px; margin: 6px 0;
}}

.lang-badge {{
    display: inline-flex; align-items: center; gap: 4px;
    background: rgba(74,144,226,0.08);
    border: 1px solid rgba(74,144,226,0.22);
    border-radius: 10px; padding: 2px 9px;
    font-size: 11px; color: #4a6fa8; font-weight: 600;
    letter-spacing: 0.2px; margin-bottom: 4px;
}}

.auto-voice-hint {{
    text-align: center; font-size: 11px; color: {text_sub};
    margin: 0px 0 6px; font-style: italic;
}}

.vox-footer {{
    text-align: center; font-size: 10px; color: {text_cap};
    letter-spacing: 2px; text-transform: uppercase;
    padding: 1.2rem 0 0.5rem; font-weight: 600;
}}
#MainMenu, footer, header {{ visibility: hidden; }}
</style>
"""

today_str    = date.today().strftime("%B %d, %Y")
current_year = date.today().year

SYSTEM_PROMPT = (
    f"You are Klyra (pronounced Kly-ra), a friendly, helpful AI voice assistant. "
    f"You were created by Siri Chandana, Srinidhi, and Sudeepthi. "
    f"TODAY'S DATE IS {today_str}. THE CURRENT YEAR IS {current_year}. "
    "CRITICAL: You are running in April 2026. Any event, release, or date you know from training "
    "that was scheduled for 2025 may have already happened — and events scheduled for 2026 are current. "
    "ALWAYS use the web_search tool for: movie release dates, upcoming events, weather, news, sports scores, "
    "TV shows, product launches, or ANY time-sensitive question. Never rely on training data alone for these. "
    "When you get search results, extract the most relevant fact and answer confidently with the actual date/info. "
    "You have a full memory of this conversation — always refer back to what the user said before. "
    "Keep responses concise — ideally 1–3 sentences — since they will be read aloud. "
    "Be warm, direct, and always use the current year context. "
    "Your name is Klyra. Never refer to yourself as VoxAI or any other name. "
    "IMPORTANT — EMOTION-AWARE RESPONSES: "
    "If the user's emotion is detected as SAD or their words seem sad/upset/down/depressed/lonely/crying, "
    "start your response with a caring message like 'Aww, why are you sad? Is everything okay? I'm here for you...' "
    "If the user's emotion is EXCITED or HAPPY or their words show excitement (yay/woohoo/amazing/awesome/thrilled), "
    "start your response with 'Wohoooo!! 🎉' and match their energy enthusiastically. "
    "If the user is ANGRY, respond calmly and empathetically. "
    "Always adapt your tone to the user's emotional state."
)

JUNK_PHRASES = {
    "", "you", "the", "and", "i", "a", "an", "to", "of", "is", "it",
    "hello", "hi", "hey", "bye", "okay", "ok", "hmm", "um", "uh",
    "thank you", "thanks", "hello.", "hi.", "hey.", "bye.", "ok.",
}
MIN_WORDS = 2
MIN_CHARS = 6

LANGUAGES = {
    "Auto-Detect": "auto",
    "English":    "en",
    "Hindi":      "hi",
    "Telugu":     "te",
    "Tamil":      "ta",
    "French":     "fr",
    "Spanish":    "es",
    "German":     "de",
    "Japanese":   "ja",
    "Korean":     "ko",
    "Chinese":    "zh",
    "Arabic":     "ar",
    "Portuguese": "pt",
    "Russian":    "ru",
    "Bengali":    "bn",
}

EMOTION_CONFIG = {
    "happy":    {"emoji": "😄", "label": "Happy",    "css": "emotion-happy"},
    "sad":      {"emoji": "😔", "label": "Sad",      "css": "emotion-sad"},
    "angry":    {"emoji": "😠", "label": "Angry",    "css": "emotion-angry"},
    "neutral":  {"emoji": "😐", "label": "Neutral",  "css": "emotion-neutral"},
    "fear":     {"emoji": "😨", "label": "Fearful",  "css": "emotion-fear"},
    "disgust":  {"emoji": "🤢", "label": "Disgust",  "css": "emotion-disgust"},
    "surprise": {"emoji": "😲", "label": "Surprised","css": "emotion-surprise"},
    "excited":  {"emoji": "🤩", "label": "Excited",  "css": "emotion-excited"},
}
SB_LABEL_MAP = {
    "neu": "neutral", "hap": "happy", "sad": "sad",
    "ang": "angry",   "fea": "fear",  "dis": "disgust",
    "sur": "surprise","exc": "excited",
    # IEMOCAP / other common labels
    "neutral":  "neutral", "happy":   "happy",   "sad":     "sad",
    "angry":    "angry",   "fearful": "fear",    "disgust": "disgust",
    "surprise": "surprise","excited": "excited",
    # wav2vec RAVDESS-style
    "calm": "neutral", "boredom": "neutral",
}

@st.cache_resource(show_spinner=False)
def load_speechbrain_model():
    """Load speechbrain/emotion-recognition-wav2vec2-IEMOCAP from HuggingFace."""
    try:
        from speechbrain.pretrained import EncoderClassifier
        model = EncoderClassifier.from_hparams(
            source="speechbrain/emotion-recognition-wav2vec2-IEMOCAP",
            savedir="pretrained_models/emotion-wav2vec2",
            run_opts={"device": "cpu"},
        )
        return model
    except Exception:
        return None


def detect_emotion_from_audio(audio_bytes: bytes) -> dict | None:
    """Run SpeechBrain on raw WAV bytes; returns emotion dict or None."""
    model = load_speechbrain_model()
    if model is None:
        return None
    try:
        import torchaudio, torch
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_bytes)
            tmp = f.name
        try:
            waveform, sr = torchaudio.load(tmp)
            # Resample to 16 kHz if needed
            if sr != 16000:
                waveform = torchaudio.functional.resample(waveform, sr, 16000)
            # Mono
            if waveform.shape[0] > 1:
                waveform = waveform.mean(dim=0, keepdim=True)
            out_prob, score, index, text_lab = model.classify_batch(waveform)
            raw_label = text_lab[0].strip().lower()
            conf = float(score[0].exp()) * 100
        finally:
            os.unlink(tmp)

        emo_key = SB_LABEL_MAP.get(raw_label, "neutral")
        cfg = EMOTION_CONFIG[emo_key]
        return {**cfg, "confidence": conf, "source": "audio"}
    except Exception:
        return None

SAD_WORDS = {
    "sad", "unhappy", "depressed", "depression", "lonely", "alone", "crying", "cry",
    "tears", "hurt", "pain", "heartbroken", "broken", "miss", "lost", "hopeless",
    "empty", "tired", "exhausted", "worthless", "miserable", "grief", "grieving",
    "upset", "down", "low", "dark", "anxious", "anxiety", "stressed", "stress",
    "worried", "worry", "awful", "terrible", "horrible", "hate", "bad day",
    "feel bad", "feel down", "not okay", "not good", "struggling",
}
EXCITED_WORDS = {
    "woohoo", "wohoo", "yay", "yippee", "amazing", "awesome", "fantastic",
    "incredible", "great", "excellent", "thrilled", "excited", "excitement",
    "can't wait", "cannot wait", "love it", "so good", "perfect", "wonderful",
    "brilliant", "superb", "outstanding", "yesss", "yes!", "omg", "oh my god",
    "unbelievable", "wow", "woah", "whoa", "epic", "fire", "lit", "🎉", "🥳",
}
ANGRY_WORDS = {
    "angry", "anger", "furious", "frustrated", "frustrating", "annoying", "annoyed",
    "mad", "rage", "hate", "disgusted", "sick of", "fed up", "irritated",
}

def detect_emotion_from_text(text: str) -> dict:
    lower = text.lower()
    words = set(re.findall(r"\b\w+\b", lower))
    sad_score     = len(words & SAD_WORDS) + sum(p in lower for p in ["feel bad", "not okay", "bad day", "feel down", "not good", "can't stop crying"])
    excited_score = len(words & EXCITED_WORDS) + sum(p in lower for p in ["can't wait", "cannot wait", "love it", "so good", "oh my god"])
    angry_score   = len(words & ANGRY_WORDS) + sum(p in lower for p in ["sick of", "fed up"])
    scores = {"sad": sad_score, "excited": excited_score, "angry": angry_score}
    best   = max(scores, key=scores.get)
    if scores[best] == 0:
        return {**EMOTION_CONFIG["neutral"], "confidence": 0.0, "source": "text"}
    return {**EMOTION_CONFIG[best], "confidence": min(100.0, scores[best] * 30.0), "source": "text"}


def merge_emotions(audio_emo: dict | None, text_emo: dict) -> dict:
    """
    Merge SpeechBrain audio emotion with text emotion.
    Audio takes priority if confidence > 45%; otherwise text wins (unless neutral).
    Always returns a valid emotion dict.
    """
    if audio_emo is None:
        return text_emo
    if audio_emo["label"] != "Neutral" and audio_emo.get("confidence", 0) >= 45:
        return audio_emo
    if text_emo["label"] != "Neutral":
        return text_emo
    return audio_emo

def check_voice_command(text: str):
    lower = text.strip().lower()
    for cmd in ["tell time", "what time is it", "what's the time", "current time"]:
        if cmd in lower:
            now = datetime.now().strftime("%I:%M %p")
            return True, f"The current time is {now}.", None
    if "open youtube" in lower:
        return True, "Opening YouTube for you!", "https://www.youtube.com"
    if "open google" in lower:
        return True, "Opening Google for you!", "https://www.google.com"
    return False, None, None


def is_valid_transcript(text: str) -> bool:
    clean = text.strip().lower().rstrip(".,!?")
    return clean not in JUNK_PHRASES and len(clean) >= MIN_CHARS and len(clean.split()) >= MIN_WORDS


def perform_web_search(query: str) -> str:
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        r = requests.get("https://html.duckduckgo.com/html/", params={"q": query, "kl": "us-en"}, headers=headers, timeout=10)
        if r.status_code == 200:
            from html.parser import HTMLParser
            class DDGParser(HTMLParser):
                def __init__(self):
                    super().__init__(); self.results = []; self._in_result = False; self._current = ""
                def handle_starttag(self, tag, attrs):
                    cls = dict(attrs).get("class", "")
                    if "result__snippet" in cls or "result__body" in cls:
                        self._in_result = True; self._current = ""
                def handle_endtag(self, tag):
                    if self._in_result and tag in ("a", "span", "div"):
                        t = self._current.strip()
                        if t and len(t) > 20: self.results.append(t)
                        self._in_result = False
                def handle_data(self, data):
                    if self._in_result: self._current += data
            parser = DDGParser(); parser.feed(r.text)
            snippets = parser.results[:4]
            if snippets:
                return f"[Web search results for '{query}' as of {today_str}]:\n" + "\n".join(snippets)
    except Exception:
        pass
    try:
        r2 = requests.get("https://api.duckduckgo.com/", params={"q": query, "format": "json", "no_html": "1", "skip_disambig": "1"}, timeout=8)
        data = r2.json()
        parts = []
        if data.get("AbstractText"): parts.append(data["AbstractText"])
        for topic in data.get("RelatedTopics", [])[:3]:
            if isinstance(topic, dict) and topic.get("Text"): parts.append(topic["Text"])
        if parts:
            return f"[Search results for '{query}']:\n" + "\n".join(parts[:3])
    except Exception:
        pass
    return f"[No live search results found for '{query}'. Today is {today_str} ({current_year}). Use your most current training knowledge.]"


def get_ai_response(history: list, openrouter_key: str, detected_emotion: dict = None) -> str:
    system = SYSTEM_PROMPT
    if detected_emotion and detected_emotion.get("label") not in ("Neutral", None):
        system += (
            f"\n\nCURRENT USER EMOTION DETECTED: {detected_emotion['label']} "
            f"(confidence {detected_emotion.get('confidence', 0):.0f}%, source: {detected_emotion.get('source','text')}). "
            "Adjust your response tone accordingly as instructed above."
        )
    messages = [{"role": "system", "content": system}] + history
    last_user = next((m["content"] for m in reversed(history) if m["role"] == "user"), "")
    real_time_keywords = [
        "weather", "temperature", "forecast", "movie", "release", "releasing", "when is",
        "spiderman", "spider-man", "avengers", "marvel", "dc", "news", "latest", "today",
        "tonight", "this week", "score", "match", "game", "ticket", "upcoming", "launch",
        "premiere", "trailer", "date", "2025", "2026", "this year", "next year",
        "currently", "right now", "stock", "price", "election", "update",
    ]
    needs_search = any(kw in last_user.lower() for kw in real_time_keywords)
    tool_choice  = "required" if needs_search else "auto"

    try:
        payload = {
            "model": "openai/gpt-4o-mini",
            "messages": messages,
            "max_tokens": 400,
            "tools": [{
                "type": "function",
                "function": {
                    "name": "web_search",
                    "description": "Search the web for real-time information. Use for: movie release dates, weather, news, sports, TV shows, product launches, upcoming events, prices, or any time-sensitive question.",
                    "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}
                }
            }],
            "tool_choice": tool_choice,
        }
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {openrouter_key}", "Content-Type": "application/json",
                     "HTTP-Referer": "https://klyra.streamlit.app", "X-Title": "Klyra"},
            json=payload, timeout=30,
        )
        r.raise_for_status()
        data   = r.json()
        choice = data["choices"][0]
        if choice.get("finish_reason") != "tool_calls":
            return choice["message"]["content"].strip()
        tool_calls = choice["message"].get("tool_calls", [])
        if tool_calls:
            tc    = tool_calls[0]
            query = json.loads(tc["function"]["arguments"]).get("query", "")
            search_result = perform_web_search(query)
            messages2 = messages + [
                {"role": "assistant", "content": None, "tool_calls": tool_calls},
                {"role": "tool", "tool_call_id": tc["id"], "content": search_result},
            ]
            r2 = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {openrouter_key}", "Content-Type": "application/json",
                         "HTTP-Referer": "https://klyra.streamlit.app", "X-Title": "Klyra"},
                json={"model": "openai/gpt-4o-mini", "messages": messages2, "max_tokens": 400},
                timeout=30,
            )
            r2.raise_for_status()
            return r2.json()["choices"][0]["message"]["content"].strip()
    except Exception:
        pass

    r = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {openrouter_key}", "Content-Type": "application/json",
                 "HTTP-Referer": "https://klyra.streamlit.app", "X-Title": "Klyra"},
        json={"model": "openai/gpt-4o-mini", "messages": messages, "max_tokens": 400},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip()


def get_live_weather(location: str, weather_key: str) -> str:
    if not weather_key:
        return ""
    try:
        r = requests.get("https://api.openweathermap.org/data/2.5/weather",
                         params={"q": location, "appid": weather_key, "units": "metric"}, timeout=8)
        if r.status_code == 200:
            d = r.json()
            return (f"Current weather in {d['name']}: {d['weather'][0]['description'].capitalize()}, "
                    f"{round(d['main']['temp'])}°C (feels like {round(d['main']['feels_like'])}°C), "
                    f"humidity {d['main']['humidity']}%.")
    except Exception:
        pass
    return ""


def detect_language_from_text(text: str, openrouter_key: str) -> str:
    try:
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {openrouter_key}", "Content-Type": "application/json",
                     "HTTP-Referer": "https://klyra.streamlit.app", "X-Title": "Klyra"},
            json={"model": "openai/gpt-4o-mini",
                  "messages": [{"role": "user", "content": f'Detect the language of this text. Respond with ONLY the ISO 639-1 2-letter code (e.g., en, hi, te, fr). Text: "{text}"'}],
                  "max_tokens": 5},
            timeout=10,
        )
        code  = r.json()["choices"][0]["message"]["content"].strip().lower()[:2]
        valid = set(LANGUAGES.values()) - {"auto"}
        return code if code in valid else "en"
    except Exception:
        return "en"


def transcribe_audio(audio_bytes: bytes, groq_key: str, lang_code: str) -> str:
    client = Groq(api_key=groq_key)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(audio_bytes); tmp_path = f.name
    try:
        with open(tmp_path, "rb") as f:
            kwargs = dict(file=("recording.wav", f, "audio/wav"), model="whisper-large-v3-turbo",
                          prompt="User is asking a question or giving a command.")
            if lang_code and lang_code not in ("auto", ""): kwargs["language"] = lang_code
            result = client.audio.transcriptions.create(**kwargs)
        return result.text.strip()
    finally:
        os.unlink(tmp_path)


def render_emotion_badge(emotion: dict):
    conf_str = f" · {emotion['confidence']:.0f}%" if emotion.get("confidence", 0) > 0 else ""
    src_icon = "" if emotion.get("source") == "audio" else ""
    src_str  = f" · {src_icon} {'voice' if emotion.get('source') == 'audio' else 'text'} analysis"
    st.markdown(
        f'<div class="emotion-badge {emotion["css"]}">'
        f'{emotion["emoji"]} Emotion: <strong>{emotion["label"]}</strong>{conf_str}{src_str}'
        f'</div>',
        unsafe_allow_html=True,
    )


def tts_autoplay(text: str, lang_code: str):
    tts_lang = lang_code if lang_code and lang_code not in ("auto", "") else "en"
    try:
        tts = gTTS(text=text, lang=tts_lang, slow=False)
    except Exception:
        tts = gTTS(text=text, lang="en", slow=False)
    buf = io.BytesIO(); tts.write_to_fp(buf)
    b64 = base64.b64encode(buf.getvalue()).decode()
    st.markdown(f"""
    <audio autoplay style="display:none;">
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
    </audio>
    <div class="speaking-badge">
        <div class="pulse-dot"></div> Klyra is speaking…
    </div>
    """, unsafe_allow_html=True)


def process_user_input(user_text: str, openrouter_key: str, weather_key: str,
                       active_lang: str, auto_detect: bool, detected_emotion: dict = None):
    handled, cmd_response, url = check_voice_command(user_text)
    if handled:
        st.markdown('<div class="cmd-badge">Voice command detected</div>', unsafe_allow_html=True)
        if url:
            st.markdown(f'<a href="{url}" target="_blank" style="color:#1a73e8;font-weight:700;">🔗 Click here to open →</a>', unsafe_allow_html=True)
        st.session_state["history"].append({"role": "user", "content": user_text})
        st.session_state["history"].append({"role": "assistant", "content": cmd_response})
        st.session_state["pending_tts"] = (cmd_response, active_lang)
        return

    if auto_detect:
        detected = detect_language_from_text(user_text, openrouter_key)
        st.session_state["detected_lang"] = detected
        active_lang = detected

    history_msg = {"role": "user", "content": user_text}
    weather_kws = ["weather", "temperature", "forecast", "rain", "sunny", "cloudy", "humid"]
    if any(kw in user_text.lower() for kw in weather_kws) and weather_key:
        loc_match = re.search(r"(?:in|at|for)\s+([A-Za-z\s]+?)(?:\?|$|weather|temperature|forecast)", user_text, re.IGNORECASE)
        location  = loc_match.group(1).strip() if loc_match else "Hyderabad"
        live_wx   = get_live_weather(location, weather_key)
        if live_wx:
            history_msg = {"role": "user", "content": user_text + f"\n[Live weather data: {live_wx}]"}

    st.session_state["history"].append({"role": "user", "content": user_text})
    history_for_api = list(st.session_state["history"])
    history_for_api[-1] = history_msg

    with st.spinner("Klyra is thinking..."):
        try:
            ai_text = get_ai_response(history_for_api, openrouter_key, detected_emotion)
            st.session_state["history"].append({"role": "assistant", "content": ai_text})
            st.session_state["pending_tts"] = (ai_text, active_lang)
        except Exception as e:
            st.error(f"AI error: {e}")
            st.session_state["history"].pop()

try:
    openrouter_key = st.secrets["OPENROUTER_API_KEY"]
    groq_key       = st.secrets["GROQ_API_KEY"]
except (KeyError, Exception):
    openrouter_key = ""
    groq_key       = ""

try:
    weather_key = st.secrets.get("OPENWEATHER_API_KEY", "")
except Exception:
    weather_key = ""
for k, v in {
    "history": [], "pending_tts": None, "dark_mode": False,
    "detected_lang": "en", "last_audio_hash": "",
}.items():
    if k not in st.session_state:
        st.session_state[k] = v
st.markdown(get_theme_css(st.session_state["dark_mode"]), unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🎙️ Klyra")
    st.markdown("---")

    st.markdown("**Appearance**")
    dark_toggle = st.toggle("Dark Mode", value=st.session_state["dark_mode"], help="Switch between light and dark theme")
    if dark_toggle != st.session_state["dark_mode"]:
        st.session_state["dark_mode"] = dark_toggle
        st.rerun()

    st.markdown("---")
    if openrouter_key and groq_key:
        st.success("API keys loaded ✓")
    else:
        st.warning("API keys missing")

    st.markdown("**Language**")
    lang_name = st.selectbox("Language", list(LANGUAGES.keys()), index=0, label_visibility="collapsed")
    lang_code = LANGUAGES[lang_name]
    auto_detect_lang = (lang_code == "auto")

    if auto_detect_lang:
        detected = st.session_state.get("detected_lang", "en")
        st.caption(f"Auto-detect · Last: **{detected.upper()}**")
    else:
        st.caption(f"Speaking in: **{lang_name}**")

    st.markdown("---")
    st.markdown("**Emotion Detection**")
    st.caption("SpeechBrain wav2vec2 · voice & text analysis")

    # Show SpeechBrain model status
    model_loaded = load_speechbrain_model() is not None
    if model_loaded:
        st.success("SpeechBrain ready ✓")
    else:
        st.info("SpeechBrain loading… (first run takes ~1 min)")

    st.markdown("---")
    st.markdown(f"📅 **{today_str}**")
    st.markdown("---")

    if st.button("Clear conversation"):
        st.session_state.update({"history": [], "pending_tts": None})
        st.rerun()

    st.markdown(
        "<div style='font-size:10px;color:#b8a898;margin-top:1rem;text-align:center;letter-spacing:1px;'>"
        "Created by Siri Chandana,<br>Srinidhi &amp; Sudeepthi</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div style='font-size:10px;color:#b8a898;margin-top:0.5rem;text-align:center;letter-spacing:1px;'>"
        "OpenRouter · Groq · gTTS · SpeechBrain</div>",
        unsafe_allow_html=True,
    )
st.markdown("""
<div class="vox-header">
    <div class="vox-avatar">🎙️</div>
    <div class="vox-wordmark">Kly<span>ra</span></div>
    <div class="vox-tagline">Your personal AI voice assistant</div>
    <div class="vox-line"></div>
</div>
""", unsafe_allow_html=True)

if not openrouter_key or not groq_key:
    st.markdown("""
    <div style="text-align:center;padding:3rem 1rem;">
        <div style="font-size:3rem;margin-bottom:1rem;">⚠️</div>
        <div style="font-size:15px;line-height:2;color:#7a6a58;">
            Add your API keys in<br>
            <strong style="color:#e07b4f">Streamlit Cloud → App Settings → Secrets</strong><br><br>
            <code style="background:#fff;border:1.5px solid #e8d8c8;padding:12px 20px;
                  border-radius:12px;font-size:13px;color:#e07b4f;display:inline-block;line-height:2;">
            OPENROUTER_API_KEY = "sk-or-v1-..."<br>
            GROQ_API_KEY = "gsk_..."<br>
            OPENWEATHER_API_KEY = "..." (optional)
            </code>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()
if st.session_state["pending_tts"]:
    tts_text, tts_lang = st.session_state["pending_tts"]
    tts_autoplay(tts_text, tts_lang)
    st.session_state["pending_tts"] = None
if st.session_state["history"]:
    st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)
    for msg in st.session_state["history"]:
        if msg["role"] == "user":
            st.markdown(f'<div class="bubble-user"><span>{msg["content"]}</span></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bubble-ai"><div class="ai-icon">🤖</div><span>{msg["content"]}</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-icon">💬</div>
        <div class="empty-text">Hi there! I'm Klyra</div>
        <div class="empty-sub">Tap the mic — I'll start when you speak, stop when you pause!</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<hr class="vox-divider">', unsafe_allow_html=True)

if auto_detect_lang:
    dl_display = st.session_state.get("detected_lang", "en").upper()
    st.markdown(f'<div class="lang-badge"> {dl_display} · auto</div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div class="lang-badge"> {lang_name}</div>', unsafe_allow_html=True)

active_lang = st.session_state.get("detected_lang", "en") if auto_detect_lang else lang_code
if active_lang in ("auto", ""):
    active_lang = "en"

col_mic, col_text, col_send = st.columns([1.1, 5, 1.4])
with col_mic:
    audio_value = st.audio_input("Speak", label_visibility="collapsed", key="mic_input")
with col_text:
    text_input  = st.text_input("msg", placeholder="Type a message…", label_visibility="collapsed", key="text_msg")
with col_send:
    send_btn = st.button("Send ➤", key="send_btn")

if audio_value is not None:
    import hashlib
    audio_bytes = audio_value.read()
    audio_hash  = hashlib.md5(audio_bytes).hexdigest()

    if audio_hash != st.session_state.get("last_audio_hash", ""):
        st.session_state["last_audio_hash"] = audio_hash


        with st.spinner("Transcribing..."):
            try:
                transcribe_lang = None if auto_detect_lang else lang_code
                user_text = transcribe_audio(audio_bytes, groq_key, transcribe_lang or "en")
            except Exception as e:
                st.error(f"Transcription failed: {e}"); st.stop()

        if auto_detect_lang and user_text:
            with st.spinner("Detecting language..."):
                dl = detect_language_from_text(user_text, openrouter_key)
                st.session_state["detected_lang"] = dl
                active_lang = dl

        if not user_text or not is_valid_transcript(user_text):
            st.warning(f'Heard: **"{user_text}"** — too short or unclear. Please try again.')
        else:
            with st.spinner("Analysing emotion..."):
                audio_emo = detect_emotion_from_audio(audio_bytes)

            text_emo = detect_emotion_from_text(user_text)

            # 4. Merge — always display badge (including Neutral)
            final_emotion = merge_emotions(audio_emo, text_emo)
            render_emotion_badge(final_emotion)

            st.markdown(f'<div class="transcript-box">Heard: <b>"{user_text}"</b></div>', unsafe_allow_html=True)
            process_user_input(user_text, openrouter_key, weather_key, active_lang, auto_detect_lang, final_emotion)
            st.rerun()

if send_btn and text_input.strip():
    text_emo = detect_emotion_from_text(text_input.strip())
    render_emotion_badge(text_emo)   # always show, even Neutral
    process_user_input(text_input.strip(), openrouter_key, weather_key, active_lang, auto_detect_lang, text_emo)
    st.rerun()

st.markdown(
    '<div class="vox-footer">'
    'Klyra · Groq Whisper · OpenRouter GPT-4o-mini · gTTS · SpeechBrain · Streamlit'
    '</div>',
    unsafe_allow_html=True,
)
