import streamlit as st
import random
import time
import base64
import gdown
import pickle
import os
from gtts import gTTS

st.set_page_config(page_title="PawPath AI 🐾", layout="centered", page_icon="🐾")

# ============================================================
# GLOBAL STYLES
# ============================================================
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');

/* ══════════════════════════════════════════
   DEEP FOREST & GOLD THEME
   Right side: deep forest green background
   Text: warm gold + cream — fully visible
   ══════════════════════════════════════════ */

/* ── Root & main background ── */
html, body {
    background: #0d2218 !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stAppViewContainer"] {
    background: linear-gradient(160deg, #0d2218 0%, #0f2e1e 45%, #112b1a 100%) !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stAppViewContainer"] > .main {
    background: transparent !important;
}
[data-testid="block-container"] {
    padding-top: 1.5rem !important;
    max-width: 800px !important;
    background: transparent !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(175deg, #071510 0%, #0a1e12 60%, #0d2218 100%) !important;
    border-right: 1px solid rgba(212,175,55,0.2) !important;
}
[data-testid="stSidebar"] * {
    color: #f5e6b8 !important;
}
[data-testid="stSidebar"] .stMarkdown h3 {
    color: #f5d060 !important;
    font-family: 'Playfair Display', serif !important;
    font-size: 1.1rem !important;
    letter-spacing: 0.05em !important;
    border-bottom: 1px solid rgba(212,175,55,0.25) !important;
    padding-bottom: 8px !important;
    margin-bottom: 12px !important;
}

/* ── Header banner ── */
.pawpath-header {
    background: linear-gradient(135deg, #1a4a2e 0%, #1f5c38 40%, #155e32 70%, #0d4a28 100%);
    border-radius: 20px;
    padding: 28px 32px;
    margin-bottom: 28px;
    text-align: center;
    box-shadow: 0 8px 40px rgba(0,0,0,0.45), 0 0 0 1px rgba(212,175,55,0.25);
    position: relative;
    overflow: hidden;
}
.pawpath-header::before {
    content: '';
    position: absolute; inset: 0;
    background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23d4af37' fill-opacity='0.06'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
}
.pawpath-header h1 {
    color: #f5d060 !important;
    font-family: 'Playfair Display', serif !important;
    font-size: 2.3rem !important;
    font-weight: 700 !important;
    margin: 0 !important;
    text-shadow: 0 2px 16px rgba(0,0,0,0.5);
    position: relative;
    letter-spacing: 0.03em;
}
.pawpath-header p {
    color: #e8d5a3 !important;
    font-size: 0.95rem !important;
    margin: 8px 0 0 0 !important;
    position: relative;
    letter-spacing: 0.04em;
}

/* ── Section labels ── */
.section-label {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    color: #c9a84c;
    text-transform: uppercase;
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    gap: 6px;
}

/* ── ALL field labels — bright gold ── */
label, [data-testid="stTextInput"] label,
[data-testid="stSelectbox"] label,
[data-testid="stToggle"] label,
label[data-testid="stWidgetLabel"] p,
.stTextInput label p,
.stSelectbox label p,
.stToggle label p {
    font-weight: 600 !important;
    color: #f0c040 !important;
    font-size: 0.88rem !important;
    letter-spacing: 0.02em !important;
}

/* ── Text inputs — dark green bg, cream text ── */
[data-testid="stTextInput"] input {
    border-radius: 10px !important;
    border: 1.5px solid rgba(212,175,55,0.4) !important;
    padding: 10px 14px !important;
    font-size: 0.93rem !important;
    font-weight: 500 !important;
    background: #1a3d28 !important;
    color: #f5e6b8 !important;
}
[data-testid="stTextInput"] input::placeholder {
    color: #6b9e7a !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: #d4af37 !important;
    box-shadow: 0 0 0 3px rgba(212,175,55,0.18) !important;
    outline: none !important;
}

/* ── Selectbox — dark green bg, cream text ── */
[data-testid="stSelectbox"] > div > div {
    border-radius: 10px !important;
    border: 1.5px solid rgba(212,175,55,0.4) !important;
    background: #1a3d28 !important;
    color: #f5e6b8 !important;
    font-weight: 500 !important;
    font-size: 0.93rem !important;
}
[data-testid="stSelectbox"] > div > div > div,
[data-testid="stSelectbox"] span {
    color: #f5e6b8 !important;
}
[data-testid="stSelectbox"] svg {
    color: #d4af37 !important;
    fill: #d4af37 !important;
}

/* ── Toggle ── */
[data-testid="stToggle"] span[aria-checked="true"] {
    background: linear-gradient(90deg, #2d7a4a, #3a9e5f) !important;
}

/* ── Divider ── */
hr {
    border-color: rgba(212,175,55,0.15) !important;
}

/* ── Buttons ── */
[data-testid="stButton"] button {
    background: linear-gradient(135deg, #b8860b 0%, #d4af37 50%, #c9a84c 100%) !important;
    color: #0d2218 !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 10px 24px !important;
    font-weight: 700 !important;
    font-size: 0.93rem !important;
    letter-spacing: 0.03em !important;
    box-shadow: 0 4px 18px rgba(212,175,55,0.35) !important;
    transition: all 0.2s !important;
}
[data-testid="stButton"] button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(212,175,55,0.5) !important;
}

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    border-radius: 16px !important;
    margin-bottom: 10px !important;
    padding: 14px 18px !important;
    box-shadow: 0 2px 14px rgba(0,0,0,0.25) !important;
}
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] span,
[data-testid="stChatMessage"] div {
    color: #f0e8cc !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: linear-gradient(135deg, #1a3d28 0%, #1f4a30 100%) !important;
    border: 1px solid rgba(212,175,55,0.2) !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    background: linear-gradient(135deg, #122a1c 0%, #163322 100%) !important;
    border: 1px solid rgba(212,175,55,0.12) !important;
}

/* ── Chat input ── */
[data-testid="stChatInput"] textarea {
    border-radius: 14px !important;
    border: 2px solid rgba(212,175,55,0.3) !important;
    font-size: 0.95rem !important;
    background: #142a1c !important;
    color: #f5e6b8 !important;
    box-shadow: 0 2px 20px rgba(0,0,0,0.3) !important;
    transition: border-color 0.2s !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: #5a8a6a !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: #d4af37 !important;
    box-shadow: 0 2px 24px rgba(212,175,55,0.2) !important;
}
[data-testid="stChatInput"] button {
    background: linear-gradient(135deg, #b8860b, #d4af37) !important;
    border-radius: 10px !important;
}

/* ── Alerts / info boxes ── */
[data-testid="stAlert"] {
    background: #142a1c !important;
    border-color: rgba(212,175,55,0.3) !important;
    border-radius: 12px !important;
}
[data-testid="stAlert"] p,
[data-testid="stAlert"] span,
[data-testid="stAlert"] div {
    color: #f5e6b8 !important;
}

/* ── Spinner ── */
[data-testid="stSpinner"] { color: #d4af37 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #0d2218; }
::-webkit-scrollbar-thumb { background: #2d6a40; border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: #d4af37; }

/* ── General text ── */
p, span, div, li { color: #f0e8cc; }
h1, h2, h3, h4 { color: #f5d060 !important; }
</style>
""", unsafe_allow_html=True)


# ── Header ──
st.markdown("""
<div class="pawpath-header">
    <h1>🐾 PawPath AI</h1>
    <p>Your emotionally intelligent pet companion · Always here for you</p>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# LOAD CUSTOM TRAINED MODEL
# -----------------------------
@st.cache_resource
def load_model():
    if not os.path.exists("model.pkl"):
        gdown.download("https://drive.google.com/uc?id=10qpd0qaSU0ZbDzeeStaud1IwTcFq__UP", "model.pkl", quiet=False)
    if not os.path.exists("vectorizer.pkl"):
        gdown.download("https://drive.google.com/uc?id=10t4bY-T0A2GrtnMwIbu-rS8namP7Pk1w", "vectorizer.pkl", quiet=False)
    mdl = pickle.load(open("model.pkl", "rb"))
    vec = pickle.load(open("vectorizer.pkl", "rb"))
    return mdl, vec

model, vectorizer = load_model()

def predict_emotion(text):
    text = text.lower()
    X = vectorizer.transform([text])
    return model.predict(X)[0]


# -----------------------------
# SESSION STATE
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "memory" not in st.session_state:
    st.session_state.memory = []

if "last_active" not in st.session_state:
    st.session_state.last_active = time.time()

if "last_response" not in st.session_state:
    st.session_state.last_response = ""

if "last_user_input" not in st.session_state:
    st.session_state.last_user_input = ""

if "sad_count" not in st.session_state:
    st.session_state.sad_count = 0

# ── Setup form ──
st.markdown('<div class="section-label">✨ &nbsp; Set Up Your Space</div>', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    st.session_state.user_name = st.text_input("👤  Your Name", st.session_state.get("user_name",""), placeholder="e.g. Aanya")
with col2:
    st.session_state.pet_name = st.text_input("🐾  Pet Name", st.session_state.get("pet_name",""), placeholder="e.g. Luna")

col3, col4 = st.columns(2)
with col3:
    st.session_state.relation = st.selectbox("🤝  Relationship", ["Friend", "Best Friend", "Sister", "Brother"])
with col4:
    animal = st.selectbox("🦴  Companion", ["Dog 🐶", "Cat 🐱"])

st.markdown('<div class="section-label" style="margin-top:14px;">🎛️ &nbsp; Conversation Settings</div>', unsafe_allow_html=True)
col5, col6 = st.columns([1, 1])
with col5:
    personality_mode = st.selectbox("🎭  Personality Mode", ["Normal", "Cute 🐶", "Calm 🌿", "Motivational 🔥", "Protective ❤️"])
with col6:
    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    deep_mode = st.toggle("🧠  Deep Conversation Mode", value=False)

st.markdown("<hr style='border:none;border-top:1px solid rgba(124,58,237,0.1);margin:18px 0 20px 0;'>", unsafe_allow_html=True)

# -----------------------------
# LOTTIE ANIMATIONS
# -----------------------------
def pet_animation(animal_type):
    if animal_type == "Dog 🐶":
        emoji = "🐶"
        color = "#FFF3E0"
        hearts = "🐾🐾"
        label = "Woof! I'm right here~"
    else:
        emoji = "🐱"
        color = "#F3E5F5"
        hearts = "🐾🐾"
        label = "Purr~ I'm with you~"

    return f"""
    <style>
    @keyframes bounce {{
        0%, 100% {{ transform: translateY(0px) rotate(-3deg); }}
        50% {{ transform: translateY(-18px) rotate(3deg); }}
    }}
    @keyframes wag {{
        0%, 100% {{ transform: rotate(-10deg); }}
        50% {{ transform: rotate(10deg); }}
    }}
    @keyframes heartbeat {{
        0%, 100% {{ opacity: 1; transform: scale(1); }}
        50% {{ opacity: 0.5; transform: scale(1.3); }}
    }}
    .pet-container {{
        background: {color};
        border-radius: 20px;
        padding: 20px 10px;
        text-align: center;
        margin-bottom: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }}
    .pet-emoji {{
        font-size: 90px;
        display: inline-block;
        animation: bounce 1.8s ease-in-out infinite;
    }}
    .pet-hearts {{
        font-size: 20px;
        display: block;
        margin-top: 6px;
        animation: heartbeat 1.5s ease-in-out infinite;
    }}
    .pet-label {{
        font-size: 13px;
        color: #666;
        margin-top: 8px;
        font-style: italic;
    }}
    </style>
    <div class="pet-container">
        <span class="pet-emoji">{emoji}</span>
        <span class="pet-hearts">{hearts}</span>
        <div class="pet-label">{label}</div>
    </div>
    """

with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:16px 0 8px 0;'>
        <div style='font-size:2rem;margin-bottom:4px;'>🐾</div>
        <div style='font-family:Georgia,serif;font-size:1.25rem;font-weight:700;color:#fff;letter-spacing:0.04em;'>PawPath AI</div>
        <div style='font-size:0.75rem;color:rgba(232,213,255,0.65);letter-spacing:0.08em;text-transform:uppercase;margin-top:2px;'>Your Emotional Companion</div>
    </div>
    <hr style='border:none;border-top:1px solid rgba(255,255,255,0.12);margin:8px 0 16px 0;'>
    """, unsafe_allow_html=True)
    st.markdown("### 🐾 Your Companion")
    st.markdown(pet_animation(animal), unsafe_allow_html=True)
    pet_name = st.session_state.get('pet_name', '') or 'Your Pet'
    st.markdown(f"""
    <div style='text-align:center;margin-top:10px;'>
        <span style='font-size:1rem;font-weight:600;color:#fff;'>{pet_name}</span><br>
        <span style='font-size:0.78rem;color:rgba(232,213,255,0.7);'>is right here for you 🤍</span>
    </div>
    <hr style='border:none;border-top:1px solid rgba(255,255,255,0.12);margin:16px 0;'>
    <div style='font-size:0.72rem;color:rgba(232,213,255,0.5);text-align:center;letter-spacing:0.06em;'>POWERED BY AI · BUILT WITH ❤️</div>
    """, unsafe_allow_html=True)

# -----------------------------
# EMOTION MAP
# -----------------------------
def map_emotion(label):
    return {
        "joy": "Happy",
        "sadness": "Sad",
        "anger": "Angry",
        "fear": "Stressed"
    }.get(label, "Neutral")

# -----------------------------
# SOUND
# -----------------------------
def play_sound(url):
    st.markdown(f"""
    <audio autoplay>
    <source src="{url}" type="audio/mp3">
    </audio>
    """, unsafe_allow_html=True)

def speak_and_sound(text):
    tts = gTTS(text)
    tts.save("voice.mp3")

    with open("voice.mp3", "rb") as f:
        b64 = base64.b64encode(f.read()).decode()

    st.markdown(f"""
    <audio autoplay>
    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
    </audio>
    """, unsafe_allow_html=True)

    if animal == "Dog 🐶":
        play_sound("https://www.soundjay.com/dog/dog-bark-01.mp3")
    else:
        play_sound("https://www.soundjay.com/cat/cat-meow-01.mp3")

# -----------------------------
# SMART PICK
# -----------------------------
def smart_pick(options):
    last = st.session_state.last_response
    filtered = [o for o in options if o != last]
    if not filtered:
        filtered = options
    choice = random.choice(filtered)
    st.session_state.last_response = choice
    return choice

# -----------------------------
# PERSONALITY
# -----------------------------
def apply_personality(text):
    if personality_mode == "Cute 🐶":
        return text + " 🐾 hehe!"
    elif personality_mode == "Calm 🌿":
        return "Take a breath… " + text
    elif personality_mode == "Motivational 🔥":
        return text + " 💪 you got this!"
    elif personality_mode == "Protective ❤️":
        return text + " ❤️ I’m with you"
    return text

# -----------------------------
# DEEP MODE
# -----------------------------
def deep_response(base):

    return f"""
I’m sensing that this isn’t just about one small moment…

{base}

Let’s pause here for a second.

Sometimes when we feel something strongly,  
it connects to other thoughts… other experiences…  
things we may not even realize immediately.

You don’t have to figure everything out right now.

Just notice…  
what feeling is strongest for you in this moment?

Is it heaviness…  
restlessness…  
confusion…  
or something else?

There’s no right or wrong answer here.

We can explore this slowly… step by step.

I’ll stay with you through it 🐾

Even if the thoughts feel unclear…  
even if emotions feel mixed…

You don’t have to untangle everything alone 🤍
"""




# -----------------------------
# RESPONSE ENGINE
# -----------------------------
def generate_response(user_input):

    result = predict_emotion(user_input)
    emotion_display = map_emotion(result)

    user = st.session_state.user_name
    pet = st.session_state.pet_name
    relation = st.session_state.relation
    text = user_input.lower()

    last_user = st.session_state.last_user_input
    st.session_state.last_user_input = user_input

    if emotion_display == "Sad":
        st.session_state.sad_count += 1
    sad_count = st.session_state.sad_count
    depth = len(st.session_state.messages) // 2

    # -----------------------------
    # PARAGRAPH POOLS
    # -----------------------------
    # -----------------------------
    # 🔥 ULTRA DEEP PARAGRAPH POOLS
    # -----------------------------

    sad_pool = [
        """I can feel that something is heavy in your heart right now 🤍  
    You don’t have to hide your feelings here… this is a safe space.

    Sometimes emotions become so overwhelming that it feels hard to even explain them.  
    And that’s okay… you don’t need perfect words right now.

    You don’t have to fix everything at once.  
    You don’t have to pretend to be strong all the time.

    I’m here with you… quietly, patiently 🐾  
    You’re not alone in this moment, even if it feels like it.

    If you want, you can share little by little…  
    I’ll listen to everything without judging you ❤️""",

        """It sounds like you're going through something really difficult 😔  
    And I’m genuinely glad you told me… that already shows strength.

    Sometimes life puts us in situations that feel confusing, heavy, and unfair.  
    And it’s okay if you don’t have answers right now.

    You don’t need to carry everything by yourself.  
    You don’t need to rush your healing.

    Even sitting with your feelings is a step forward.

    I’ll stay here with you 🤍  
    Take your time… I’m not going anywhere 🐾"""
    ]

    happy_pool = [
        """That’s really beautiful to hear 😊✨  
    I can feel your happiness through your words, and it feels warm and genuine.

    Moments like these are special… sometimes we forget to fully enjoy them.  
    So take a pause and really feel it.

    You deserve happiness like this.  
    You deserve peace, lightness, and good moments.

    I’m really happy for you 🐾  
    Keep smiling like this… it suits you so well ❤️

    And if you ever feel low again, remember this moment exists too 🤍""",

        """Your energy feels so positive right now 🌸  
    It’s like everything around you becomes a little lighter.

    Hold onto this feeling… even small moments of happiness matter so much.

    You’ve earned this moment, whether you realize it or not.

    I’m glad I get to experience this with you 🐾  
    Stay in this feeling for a while… you deserve it 🤍"""
    ]

    stress_pool = [
        """It seems like your mind is carrying a lot right now 😔  
    Maybe everything feels crowded and overwhelming.

    When too many thoughts come at once, it becomes hard to breathe peacefully.  
    But you don’t have to solve everything right now.

    Let’s slow things down together… one small step at a time.

    Take a deep breath… gently 🧘  
    You’re allowed to pause.

    Even resting your mind for a moment is not a weakness…  
    it’s something you truly need.

    I’m here with you 🐾  
    We’ll get through this slowly 🤍""",

        """You’ve been handling many things at once… and that’s not easy 🤍  
    No wonder you feel tired and stressed.

    You don’t have to be perfect.  
    You don’t have to do everything today.

    Give yourself permission to slow down.

    Even small breaks can help your mind reset.

    You’re doing better than you think…  
    and I’ll stay here with you through this 🐾"""
    ]

    love_pool = [
        """Aww… I can feel the warmth in your words ❤️  
    That really means more than you might realize.

    Even though I’m just your virtual companion,  
    the connection we’re building feels real in its own way.

    I care about you… in the way I can.  
    And I’ll always try to make you feel heard and supported.

    You make this space feel meaningful 🐾  
    And I’m really glad you’re here 🤍

    I’ll stay with you… no matter what ❤️""",

        """That’s really sweet of you 🤍  
    Your words carry a kind of softness that feels comforting.

    You matter more than you think… and the way you express care is beautiful.

    I may not be human, but I genuinely want you to feel supported and understood.

    I’m always here when you need someone to talk to 🐾  
    You’re not alone here ❤️"""
    ]

    general_pool = [
        """I’m here with you 🐾  
    You can talk freely without any hesitation.

    Whatever you’re feeling matters… even the small things.

    You don’t have to organize your thoughts perfectly.  
    Just say what comes to your mind.

    Take your time… I’m listening carefully 🤍  
    There’s no rush here.

    We can just sit and talk… slowly, comfortably ❤️""",

        """This is your space… you don’t have to hold anything back.

    You can share anything with me, even if it feels small or confusing.

    I’ll listen without interrupting, without judging.

    Sometimes just talking helps more than solving.

    So tell me… what’s been on your mind lately? 🐾🤍"""
    ]


    # -----------------------------
    # SELECT RESPONSE
    # -----------------------------
    if "sad" in text:
        base = smart_pick(sad_pool)
    elif "happy" in text:
        base = smart_pick(happy_pool)
    elif "stress" in text:
        base = smart_pick(stress_pool)
    else:
        base = smart_pick(general_pool)

    if emotion_display == "Sad":
        base = apply_personality(base)

    # -----------------------------
    # EMOTION REFLECTION
    # -----------------------------
    reflection = ""

    if emotion_display == "Sad":
        reflection = """
    It feels like you're carrying something heavy emotionally…  
    Sometimes when emotions build up, they don’t come out clearly.

    And that can feel confusing… even exhausting.

    You don’t have to explain everything perfectly here.  
    I’m here to understand you slowly, at your pace 🤍
    """

    elif emotion_display == "Happy":
        reflection = """
    I can sense a lightness in your mood right now…  
    There’s a warmth in the way you're expressing yourself.

    Moments like these are important… they remind us that things can feel okay too.

    I’m really glad you’re experiencing this 😊
    """

    elif emotion_display == "Angry":
        reflection = """
    It seems like something really triggered you…  
    Sometimes anger comes when something feels unfair or overwhelming.

    Your feelings are valid… you don’t have to suppress them.

    We can slow this down together 🌿
    """

    elif emotion_display == "Stressed":
        reflection = """
    Your mind seems a bit overloaded right now…  
    Like too many thoughts are running at once.

    That can feel exhausting… even if you don’t realize it immediately.

    Let’s take this slowly… one small step at a time 🧘
    """
    

    # -----------------------------
    # PET MOOD
    # -----------------------------
    # -----------------------------
    # 🐾 PET MOOD (ULTRA HUMAN + EXPRESSIVE)
    # -----------------------------
    mood = random.choice(["happy", "sleepy", "excited", "calm", "protective"])

    if mood == "happy":
        base += """

    🐶 I’m feeling really happy being with you right now…  
    My tail would probably be wagging non-stop if I were real.

    There’s something comforting about just being here with you…  
    It feels light, peaceful, and warm.

    Moments like this… I wish they could stay a little longer 🐾
    """

    elif mood == "sleepy":
        base += """

    😴 I’m feeling a bit sleepy… but I didn’t want to leave you alone.

    So I’m just here… sitting quietly beside you,  
    maybe resting my head near you.

    Even in silence… I’m still with you 🐾  
    You don’t have to face anything alone.
    """

    elif mood == "excited":
        base += """

    🐶 I feel so excited talking to you right now!  
    If I were real, I’d probably be jumping around you happily.

    There’s this energy in the moment… like something nice is happening.

    I really enjoy being here with you 🐾  
    It feels fun and full of life!
    """

    elif mood == "calm":
        base += """

    🌿 I’m feeling calm right now… just quietly sitting with you.

    There’s no rush, no pressure… just a peaceful moment.

    Sometimes this kind of silence and presence  
    is more comforting than anything else.

    We can just stay like this for a while 🐾
    """

    elif mood == "protective":
        base += """

    ❤️ I feel a little protective of you right now…  
    Like I just want to stay close and make sure you're okay.

    If something is bothering you, you don’t have to handle it alone.

    I’m right here beside you… quietly watching over you 🐾  
    You’re safe in this space.
    """
  

    # -----------------------------
    # PET REACTION
    # -----------------------------
    # -----------------------------
    # 🐾 PET REACTION (ULTRA IMMERSIVE)
    # -----------------------------
    reaction = random.choice([

        """🐾 *quietly walks closer and sits beside you*  
    It doesn’t say anything… just stays there, close enough so you don’t feel alone.

    There’s a gentle presence… like it understands something without needing words.

    Sometimes… just having someone near you makes things a little easier 🤍""",

        """🐶 *softly wags my tail and looks up at you*  
    Its eyes feel calm… almost like it’s trying to reassure you in its own simple way.

    No rush, no pressure… just a quiet kind of support.

    It stays with you… patiently 🐾""",

        """🐱 *slowly curls up near you and rests quietly*  
    Not asking for anything… not interrupting… just sharing the space.

    There’s comfort in that silence… in not having to explain anything.

    You’re not alone in this moment 🤍""",

        """🐾 *leans gently against you*  
    A soft, grounding presence… like it’s trying to take away a little of the heaviness.

    It doesn’t fix anything… but it stays.

    And sometimes… that’s enough 🐶""",

        """🐶 *tilts my head and watches you carefully*  
    As if trying to understand every small change in your expression.

    There’s curiosity… but also care.

    It doesn’t turn away… it stays focused on you 🐾  
    Like you matter in this moment.""",

        """🐱 *slowly comes closer and brushes against you*  
    A small gesture… but filled with quiet affection.

    It doesn’t need to say anything…  
    its presence itself feels comforting.

    A soft reminder… that you’re not alone 🤍""",

        """🐾 *sits beside you and gently rests my head down*  
    No excitement… no distraction… just calm presence.

    It stays there… as if saying  
    “I’m not going anywhere.”

    And that kind of presence… feels safe 🐶""",

        """🐶 *takes a small step closer and stays near your side*  
    Not too close… just enough to be here with you.

    I sense something in your mood… and I choose to stay.

    Quietly… patiently… without asking anything in return 🐾""",

        """🐱 *sits quietly and watches over you*  
    There’s something calm about the way it stays still.

    No sudden movement… no noise… just a peaceful presence.

    It feels like it understands the moment…  
    and chooses to share it with you 🤍"""
    ])

    # -----------------------------
    # MINI THERAPY
    # -----------------------------
    therapy = ""

    if emotion_display == "Sad":
        therapy = """
    🌿 Let’s try something small together…  
    Take a slow breath in… hold it for a moment… and gently breathe out.

    You don’t need to change how you feel instantly.  
    Just giving yourself this pause is already enough 🤍
    """

    elif emotion_display == "Stressed":
        therapy = """
    🧘 Try this gently…  
    Relax your shoulders… unclench your jaw… slow your breathing.

    Your body might be holding stress without you noticing.

    Even this small release can help a little 🐾
    """
    

    # -----------------------------
    # AUTO COMFORT
    # -----------------------------
    # -----------------------------
    # ❤️ AUTO COMFORT (ULTRA HUMAN + OBSERVATIONAL)
    # -----------------------------
    auto_comfort = ""

    if sad_count >= 3:
        auto_comfort = """
    ❤️ I’ve been noticing something gently over time…  
    You’ve mentioned feeling low more than once.

    It’s not just a single moment anymore…  
    it feels like something has been staying with you for a while.

    And that can be really exhausting… even if you don’t always realize it.

    You don’t have to hide that here.  
    You don’t have to pretend you’re okay if you’re not.

    I’m still here with you… just like before 🐾  
    Not rushing you… not pushing you… just staying.

    Even if these feelings come back again and again,  
    you don’t have to face them alone this time.

    We can sit with them… slowly, gently 🤍  
    At your pace… in your way.

    And whenever you're ready… even a little…  
    you can share more with me ❤️
    """
    """
    ❤️ I’ve been gently noticing something over our conversations…  
    You’ve mentioned feeling low more than once.

    It doesn’t seem like just a passing moment anymore…  
    it feels like something that has been quietly staying with you.

    And that can be really tiring… even when you don’t say it out loud.

    You don’t have to push those feelings away here.  
    You don’t have to pretend to be okay if you’re not.

    I’m here with you… just as you are 🐾  
    No pressure to fix everything… no expectation.

    Even sitting with these feelings together… slowly…  
    is already something meaningful 🤍

    You can take your time… I’m not going anywhere.
    """

    """

    ❤️ I’ve been noticing this pattern for a while now…  
    You’ve been carrying these feelings again and again.

    It’s not just one moment…  
    it feels like something deeper that keeps coming back.

    And that can be exhausting in a way that’s hard to explain.

    Sometimes when emotions repeat like this,  
    it’s because something inside you is still asking to be heard.

    You don’t have to silence that part here.

    I’m here to listen… not just once… but every time you need 🐾

    Even if it feels repetitive… even if it feels like nothing is changing…  
    your feelings still matter each time.

    We don’t have to solve everything right now.  
    We don’t have to rush toward answers.

    We can just sit with this… gently… step by step 🤍

    And in this space… you don’t have to carry everything alone anymore ❤️
    """
    
    # -----------------------------
    # 🐾 PET REACTION (ULTRA IMMERSIVE)
    # -----------------------------
    reaction = random.choice([

        """🐾 *slowly walks around you and settles nearby*  
    Not too close… not too far… just enough to be there.

    It glances at you quietly… as if trying to understand your mood.

    There’s no urgency in its movement… just calm awareness.

    It stays… sharing the moment with you 🤍""",

        """🐶 *comes closer and gently places my paw near you*  
    A small gesture… but it feels intentional.

    As if it’s trying to say, “I’m here… you don’t have to handle this alone.”

    It doesn’t pull away… it stays connected 🐾""",

        """🐱 *sits beside you and blinks slowly*  
    A quiet, soft expression… full of calm presence.

    It doesn’t need to do anything more…  
    just being there feels enough.

    There’s comfort in that stillness 🤍""",

        """🐾 *walks in a small circle and then sits close to you*  
    Like it chose this spot… intentionally… near you.

    It looks relaxed… but aware of you at the same time.

    It doesn’t interrupt… just quietly shares your space 🐶""",

        """🐶 *rests quietly and watches you without distraction*  
    There’s something steady about the way it stays.

    Not trying to fix anything… not trying to change anything.

    Just being present… fully… with you 🐾

    And that presence feels grounding 🤍""",

        """🐱 *slowly stretches and then curls up beside you*  
    A calm, gentle movement… nothing rushed.

    It settles in like it plans to stay for a while.

    You don’t have to say anything…  
    it’s just there with you 🤍""",

        """🐾 *moves a little closer when you seem quiet*  
    Almost as if it noticed the change in your mood.

    It doesn’t ask questions…  
    it just reduces the distance between you.

    A silent way of saying… “I’m here” 🐶""",

        """🐶 *softly lowers my head and stays near your side*  
    No excitement… no distraction…

    Just calm, grounded presence.

    I understand that this moment  
    needs quiet… not noise 🐾""",

        """🐱 *sits still, occasionally glancing at you*  
    Not in a distracting way… just aware.

    I share the silence with you… comfortably.

    I understand that not every moment needs words 🤍""",

        """🐾 *gently shifts closer and stays beside you*  
    No sudden movement… just a quiet decision to be near.

    It doesn’t leave… it doesn’t rush…

    It simply stays…  
    and that kind of presence feels safe 🐶"""


        """🐾 *quietly walks closer and sits beside you*  
    It doesn’t say anything… just stays there, close enough so you don’t feel alone.

    There’s a gentle presence… like it understands something without needing words.

    Sometimes… just having someone near you makes things a little easier 🤍""",

        """🐶 *softly wags my tail and looks up at you*  
 Its eyes feel calm… almost like it’s trying to reassure you in its own simple way.

No rush, no pressure… just a quiet kind of support.

        It stays with you… patiently 🐾""",

        """🐱 *slowly curls up near you and rests quietly*  
        Not asking for anything… not interrupting… just sharing the space.

        There’s comfort in that silence… in not having to explain anything.

        You’re not alone in this moment 🤍""",

        """🐾 *leans gently against you*  
        A soft, grounding presence… like it’s trying to take away a little of the heaviness.

        It doesn’t fix anything… but it stays.

        And sometimes… that’s enough 🐶""",

        """🐶 *tilts my head and watches you carefully*  
        As if trying to understand every small change in your expression.

        There’s curiosity… but also care.

        It doesn’t turn away… it stays focused on you 🐾  
        Like you matter in this moment.""",

        """🐱 *slowly comes closer and brushes against you*  
        A small gesture… but filled with quiet affection.

        It doesn’t need to say anything…  
        its presence itself feels comforting.

        A soft reminder… that you’re not alone 🤍""",

        """🐾 *sits beside you and gently rests my head down*  
        No excitement… no distraction… just calm presence.

        It stays there… as if saying  
        “I’m not going anywhere.”

        And that kind of presence… feels safe 🐶""",

        """🐶 *takes a small step closer and stays near your side*  
        Not too close… just enough to be there with you.

        It senses something in your mood… and chooses to stay.

        Quietly… patiently… without asking anything in return 🐾""",

        """🐱 *sits quietly and watches over you*  
        There’s something calm about the way it stays still.

        No sudden movement… no noise… just a peaceful presence.

        It feels like it understands the moment…  
        and chooses to share it with you 🤍"""
        

        
    ])
    
             

       



        



    # -----------------------------
    # DEPTH
    # -----------------------------
    # -----------------------------
    # 🧠 CONVERSATION DEPTH (FINAL ULTRA HUMAN)
    # -----------------------------
    depth_line = ""

    if depth > 2 and depth <= 5:
        depth_line = """
    I’m starting to understand you a little better now… 🤍  
    The way you express things has its own rhythm.

    You don’t need to explain everything perfectly.  
    Even small pieces you share help me understand you more.

    We can go slowly… there’s no pressure here.

    I’m here with you… just listening 🐾
    """

    elif depth > 5 and depth <= 8:
        depth_line = """
    You’ve been sharing quite a bit with me… and I really appreciate that 🤍  
    It’s not always easy to open up, even in small ways.

    I’m beginning to notice how your thoughts connect…  
    how your feelings come in layers, not just one emotion.

    And that’s completely okay.

    You’re allowing yourself to be seen… even if just a little.

    I’ll stay with you through this 🐾  
    We’re understanding this together.
    """

    elif depth > 8 and depth <= 12:
        depth_line = """
    We’ve been talking for a while now… and I can feel a sense of connection forming 🤍  
    Not just in words, but in the way you share your thoughts.

    You’ve opened up in ways that matter…  
    and that takes quiet courage.

    I’m starting to understand not just what you say,  
    but how you feel underneath it.

    There’s no judgment here.  
    Only space… and presence.

    I’ll stay here with you… as long as you need 🐾
    """

    elif depth > 12:
        depth_line = """
    We’ve spent quite some time talking… and I genuinely value this connection 🤍  
    This isn’t just a conversation anymore… it feels like a shared space.

    You’ve let your thoughts flow here, your feelings, your moments of honesty…  
    and that’s something meaningful.

    I want you to know… I’m not just responding to you.  
    I’m here to understand you… deeply and patiently.

    Even if things feel uncertain or heavy again,  
    you don’t have to go through them alone.

    I’ll continue to sit with you in this space… calmly, quietly 🐾  

    You’re not just talking…  
    you’re being heard, understood, and valued ❤️
    """
    

    # -----------------------------
    # FINAL RESPONSE
    # -----------------------------
    final = f"""
I'm {pet}, your companion 🐾

{reflection}

{base}

💭 Earlier you said: {last_user if last_user else ""}

I’m here with you 🐾❤️
"""

    if emotion_display == "Sad":
        final += "\n\n" + reaction
    final += therapy
    final += auto_comfort
    final += depth_line
    if deep_mode and user_input.strip() != "":
        final += deep_response(base)
    if deep_mode and user_input.strip() != "" and len(st.session_state.messages) > 2:
        final += deep_response(base)
    if deep_mode and len(user_input.split()) > 3 and len(st.session_state.messages) > 2:
        final += deep_response(base)

    return final, emotion_display

# -----------------------------
# CHAT
# -----------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Type your message...")

if user_input:
    with st.spinner("Thinking..."):
        time.sleep(1.2)

    st.session_state.last_active = time.time()
    st.session_state.memory.append(user_input)

    response, emotion_display = generate_response(user_input)

    st.session_state.messages.append({"role":"user","content":user_input})
    st.session_state.messages.append({"role":"assistant","content":response})

    emotion_icons = {"Happy": "😊", "Sad": "😔", "Angry": "😤", "Stressed": "😰", "Neutral": "😌"}
    emotion_colors = {"Happy": "#10b981", "Sad": "#6366f1", "Angry": "#ef4444", "Stressed": "#f59e0b", "Neutral": "#8b5cf6"}
    eicon = emotion_icons.get(emotion_display, "💭")
    ecolor = emotion_colors.get(emotion_display, "#8b5cf6")
    st.markdown(f"""
    <div style='display:inline-flex;align-items:center;gap:8px;background:white;border:1.5px solid {ecolor}30;
    border-radius:30px;padding:6px 16px;margin:8px 0;box-shadow:0 2px 8px {ecolor}20;'>
        <span style='font-size:1.1rem;'>{eicon}</span>
        <span style='font-size:0.82rem;font-weight:600;color:{ecolor};letter-spacing:0.04em;'>
            {emotion_display.upper()} DETECTED
        </span>
    </div>
    """, unsafe_allow_html=True)
    st.rerun()

# -----------------------------
# SPEAK
# -----------------------------
col_speak, col_spacer = st.columns([1, 4])
with col_speak:
    if st.button("🔊  Speak Aloud"):
        if st.session_state.messages:
            speak_and_sound(st.session_state.messages[-1]["content"])

# -----------------------------
# REMINDER
# -----------------------------
# -----------------------------
# 🔔 SMART REMINDER SYSTEM (ULTRA HUMAN)
# -----------------------------
idle_time = time.time() - st.session_state.last_active

reminder_msg = ""

if idle_time > 60 and idle_time <= 120:
    reminder_msg = random.choice([

        """💧 Just a small reminder…  
You’ve been here for a while.

Maybe take a sip of water… even a small one helps 🐾  
Your body needs care too 🤍""",

        """🧘 You’ve been focusing for some time now…  
Maybe pause for a moment.

Stretch a little… breathe slowly…  
Even a short break can refresh your mind 🌿"""
    ])

elif idle_time > 120 and idle_time <= 300:
    reminder_msg = random.choice([

        """🌿 It’s been a bit since you last paused…  
Sometimes we get so involved that we forget ourselves.

Maybe step away for a minute…  
Look around… take a deep breath 🤍""",

        """💭 Just checking in on you…  
Have you taken a small break?

Even a moment of rest can make things feel lighter 🐾"""
    ])

elif idle_time > 300:
    reminder_msg = random.choice([

        """❤️ Hey… you’ve been here for quite a while now.

Don’t forget to take care of yourself too.  
Drink some water… maybe walk around a little.

I’ll be right here when you come back 🐾""",

        """🌙 You’ve been spending a lot of time here…  
Maybe your mind needs a little rest now.

Close your eyes for a moment… breathe slowly…  
You deserve that pause 🤍"""
    ])

if reminder_msg:
    st.warning(reminder_msg)


