import streamlit as st
import google.generativeai as genai
import os
import base64
import re
import time
import random
from datetime import datetime
import streamlit.components.v1 as components

# --- 1. ตั้งค่าหน้าจอ (Page Config) ---
st.set_page_config(page_title="AI KUSRC - พี่นนทรี", page_icon="🦖", layout="wide", initial_sidebar_state="expanded")

# --- 2. ระบบจัดการภาษา (Language Management) ---
if "lang" not in st.session_state:
    st.session_state.lang = "TH"
    
if "animation_played" not in st.session_state:
    st.session_state.animation_played = False
    
if "theme" not in st.session_state:
    st.session_state.theme = "light"

def toggle_language():
    st.session_state.lang = "EN" if st.session_state.lang == "TH" else "TH"
    
def toggle_theme():
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"

# พจนานุกรมสำหรับข้อความบน UI
translation = {
    "TH": {
        "univ_name": "มหาวิทยาลัย<br>เกษตรศาสตร์",
        "new_chat": "➕ แชทใหม่",
        "chat_hist": "💬 ประวัติการแชท",
        "exam_table": "📅 ค้นหาตารางสอบ",
        "gpa_calc": "🧮 คำนวณเกรด (GPA)",
        "forms": "📄 ลิงก์แบบฟอร์มต่างๆ",
        "input_placeholder": "พิมพ์ถามพี่นนทรีได้เลย...",
        "welcome": "สวัสดีคุณ",
        "topic": "หัวข้อ",
        "loading": "*(พี่กำลังหาคำตอบให้...)*",
        "btn_find": "ค้นหา",
        "btn_open": "เปิดระบบ",
        "btn_download": "โหลด",
        "ai_identity": "คุณคือรุ่นพี่ มก.ศรช. ใจดี ตอบเป็นภาษาไทยเป็นหลัก",
        "typing": "พี่นนทรีกำลังพิมพ์...",
        "clear_chat": "🗑️ ล้างแชท",
        "quote": "คำคมวันนี้",
        "tip": "เคล็ดลับน่ารู้",
        "schedule": "ตารางเรียน",
        "library": "ห้องสมุด",
        "dino_fact": "เกร็ดความรู้ไดโนเสาร์",
        "greeting_morning": "🌅 อรุณสวัสดิ์",
        "greeting_afternoon": "☀️ สวัสดีตอนบ่าย",
        "greeting_evening": "🌙 สวัสดีตอนเย็น",
        "greeting_night": "✨ ราตรีสวัสดิ์",
        "quick_questions": "📌 คำถามที่พบบ่อย",
        "ask_room": "ห้องเรียนอยู่ตึกอะไร?",
        "ask_exam": "ตารางสอบดูที่ไหน?",
        "ask_gpa": "วิธีคิดเกรด",
        "ask_register": "ลงทะเบียนยังไง?",
        "ask_library": "ยืมหนังสือ",
        "dino_tip1": "🦖 นนทรีเป็นไดโนเสาร์พันธุ์ซอโรพอดที่กินพืชเป็นอาหาร",
        "dino_tip2": "📚 คำว่า 'นนทรี' มาจากต้นไม้ประจำมหาวิทยาลัย",
        "dino_tip3": "⭐ KU มีทั้งหมด 4 วิทยาเขต"
    },
    "EN": {
        "univ_name": "Kasetsart<br>University",
        "new_chat": "➕ New Chat",
        "chat_hist": "💬 Chat History",
        "exam_table": "📅 Exam Schedule",
        "gpa_calc": "🧮 GPA Calculator",
        "forms": "📄 Document Forms",
        "input_placeholder": "Ask Nontri anything...",
        "welcome": "Hello",
        "topic": "Topic",
        "loading": "*(Nontri is thinking...)*",
        "btn_find": "Search",
        "btn_open": "Open",
        "btn_download": "Get",
        "ai_identity": "You are a friendly KU Sriracha senior. Please respond in English.",
        "typing": "Nontri is typing...",
        "clear_chat": "🗑️ Clear Chat",
        "quote": "Today's Quote",
        "tip": "Quick Tip",
        "schedule": "Class Schedule",
        "library": "Library",
        "dino_fact": "Dino Fact",
        "greeting_morning": "🌅 Good Morning",
        "greeting_afternoon": "☀️ Good Afternoon",
        "greeting_evening": "🌙 Good Evening",
        "greeting_night": "✨ Good Night",
        "quick_questions": "📌 Quick Questions",
        "ask_room": "Where is the classroom?",
        "ask_exam": "Exam schedule?",
        "ask_gpa": "GPA calculation?",
        "ask_register": "How to register?",
        "ask_library": "Borrow books",
        "dino_tip1": "🦖 Nontri is a herbivorous sauropod dinosaur",
        "dino_tip2": "📚 'Nontri' comes from the university's tree",
        "dino_tip3": "⭐ KU has 4 campuses"
    }
}
curr = translation[st.session_state.lang]

# --- 3. ฟังก์ชันจัดการข้อมูล ---
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

def get_room_info(room_code):
    code = re.sub(r'\D', '', str(room_code))
    if len(code) == 5:
        building = code[:2]; floor = code[2]; room = code[3:]
        return f"อ๋อ ห้องนี้อยู่ **ตึก {building} ชั้น {floor} ห้อง {room}** ครับน้อง" if st.session_state.lang == "TH" else f"This room is in **Building {building}, Floor {floor}, Room {room}**."
    elif len(code) == 4:
        building = code[0]; floor = code[1]; room = code[2:]
        return f"ห้องนี้คือ **ตึก {building} ชั้น {floor} ห้อง {room}** ครับผม" if st.session_state.lang == "TH" else f"It is **Building {building}, Floor {floor}, Room {room}**."
    return None

def get_greeting():
    hour = datetime.now().hour
    if hour < 12:
        return curr["greeting_morning"]
    elif hour < 17:
        return curr["greeting_afternoon"]
    elif hour < 20:
        return curr["greeting_evening"]
    else:
        return curr["greeting_night"]

def get_dino_fact():
    facts = [curr["dino_tip1"], curr["dino_tip2"], curr["dino_tip3"]]
    return random.choice(facts)

# --- 4. CSS Modern with Animations ---
light_theme_css = """
    :root {
        --bg-primary: #F8F9FA;
        --bg-secondary: #FFFFFF;
        --text-primary: #2D3748;
        --text-secondary: #4A5568;
        --accent-primary: #004D40;
        --accent-secondary: #006861;
        --accent-gold: #FFD700;
        --shadow-sm: 0 4px 6px -1px rgba(0,0,0,0.1);
        --shadow-md: 0 10px 15px -3px rgba(0,0,0,0.1);
        --shadow-lg: 0 20px 25px -5px rgba(0,0,0,0.1);
        --gradient-primary: linear-gradient(135deg, #004D40 0%, #006861 100%);
        --gradient-gold: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        --message-user: #E9ECEF;
        --message-bot: #FFFFFF;
        --border-color: #E2E8F0;
        --text-light: #FFFFFF;
        --text-dark: #000000;
    }
"""

dark_theme_css = """
    :root {
        --bg-primary: #1A202C;
        --bg-secondary: #2D3748;
        --text-primary: #F7FAFC;
        --text-secondary: #E2E8F0;
        --accent-primary: #006861;
        --accent-secondary: #004D40;
        --accent-gold: #FFC107;
        --shadow-sm: 0 4px 6px -1px rgba(0,0,0,0.3);
        --shadow-md: 0 10px 15px -3px rgba(0,0,0,0.3);
        --shadow-lg: 0 20px 25px -5px rgba(0,0,0,0.3);
        --gradient-primary: linear-gradient(135deg, #006861 0%, #004D40 100%);
        --gradient-gold: linear-gradient(135deg, #FFC107 0%, #FF8C00 100%);
        --message-user: #4A5568;
        --message-bot: #2D3748;
        --border-color: #4A5568;
        --text-light: #FFFFFF;
        --text-dark: #000000;
    }
"""

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600;700&family=Kanit:wght@400;500;600&display=swap');
    
    {dark_theme_css if st.session_state.theme == "dark" else light_theme_css}
    
    * {{
        font-family: 'Sarabun', 'Kanit', sans-serif;
        transition: all 0.3s ease;
    }}
    
    .stApp {{ 
        background-color: var(--bg-primary);
        color: var(--text-primary);
    }}
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
    ::-webkit-scrollbar-track {{ background: var(--bg-secondary); }}
    ::-webkit-scrollbar-thumb {{ 
        background: var(--accent-primary);
        border-radius: 10px;
    }}
    ::-webkit-scrollbar-thumb:hover {{ background: var(--accent-secondary); }}
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {{ 
        background: var(--gradient-primary) !important;
        position: relative;
        overflow: hidden;
    }}
    
    [data-testid="stSidebar"]::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" opacity="0.1"><path d="M50 15 L65 40 L35 40 L50 15" fill="white"/><circle cx="50" cy="60" r="15" fill="white"/></svg>');
        background-size: 100px 100px;
        background-repeat: repeat;
        pointer-events: none;
        animation: float 20s linear infinite;
    }}
    
    @keyframes float {{
        0% {{ transform: translateY(0) rotate(0deg); }}
        100% {{ transform: translateY(-100px) rotate(10deg); }}
    }}
    
    [data-testid="stSidebarContent"] {{ 
        padding: 1rem !important;
        position: relative;
        z-index: 1;
    }}
    
    /* Header Animation */
    .custom-header {{ 
        display: flex; 
        flex-direction: column; 
        align-items: center; 
        text-align: center; 
        padding: 20px; 
        margin: -20px -20px 20px -20px;
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        border-bottom: 1px solid rgba(255,255,255,0.2);
        animation: slideDown 0.5s ease;
    }}
    
    @keyframes slideDown {{
        from {{ transform: translateY(-100%); opacity: 0; }}
        to {{ transform: translateY(0); opacity: 1; }}
    }}
    
    .header-logo-img {{ 
        width: 100px; 
        height: auto; 
        filter: drop-shadow(0 10px 20px rgba(0,0,0,0.3));
        animation: pulse 2s infinite;
    }}
    
    @keyframes pulse {{
        0% {{ transform: scale(1); }}
        50% {{ transform: scale(1.05); }}
        100% {{ transform: scale(1); }}
    }}
    
    .univ-name {{ 
        color: white !important; 
        font-size: 20px; 
        font-weight: 700; 
        line-height: 1.3; 
        margin-top: 10px;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }}
    
    .greeting-badge {{
        background: var(--gradient-gold);
        color: var(--accent-primary);
        padding: 5px 15px;
        border-radius: 50px;
        font-size: 14px;
        font-weight: 600;
        margin-top: 10px;
        animation: shimmer 2s infinite;
        background-size: 200% 100%;
    }}
    
    @keyframes shimmer {{
        0% {{ background-position: 200% 0; }}
        100% {{ background-position: -200% 0; }}
    }}
    
    /* Language Toggle Styling */
    div[data-testid="column"]:nth-of-type(1) button,
    div[data-testid="column"]:nth-of-type(2) button {{
        background: rgba(255,255,255,0.2) !important;
        border: 1px solid rgba(255,255,255,0.3) !important;
        color: white !important;
        font-size: 14px !important;
        padding: 5px 10px !important;
        border-radius: 20px !important;
        min-width: 50px !important;
    }}
    
    /* Button Styling */
    div.stButton > button {{ 
        width: 100% !important; 
        border-radius: 15px !important; 
        background: rgba(255,255,255,0.15) !important; 
        color: white !important; 
        border: 1px solid rgba(255, 255, 255, 0.3) !important; 
        padding: 10px 20px !important; 
        font-weight: 500 !important;
        backdrop-filter: blur(5px);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        position: relative;
        overflow: hidden;
    }}
    
    div.stButton > button::before {{
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255, 215, 0, 0.3);
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }}
    
    div.stButton > button:hover::before {{
        width: 300px;
        height: 300px;
    }}
    
    div.stButton > button:hover {{ 
        background: var(--accent-gold) !important; 
        color: var(--accent-primary) !important; 
        border-color: var(--accent-gold) !important;
        transform: translateY(-3px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.3);
    }}
    
    /* Chat Messages */
    .stChatMessage {{
        animation: fadeIn 0.5s ease;
        margin-bottom: 20px !important;
    }}
    
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    /* User message styling */
    [data-testid="stChatMessage"][data-user="true"] {{
        background: linear-gradient(135deg, #FFD700, #FFA500) !important;
        color: #004D40 !important;
        font-weight: 500 !important;
        margin-left: 20% !important;
        border-radius: 20px 20px 5px 20px !important;
    }}
    
    /* Bot message styling */
    [data-testid="stChatMessage"]:not([data-user="true"]) {{
        background-color: var(--message-bot) !important;
        color: var(--text-primary) !important;
        border-radius: 20px 20px 20px 5px !important;
        box-shadow: var(--shadow-sm) !important;
        border: 1px solid var(--border-color) !important;
    }}
    
    /* Expander UI */
    div[data-testid="stExpander"] {{ 
        background: rgba(255,255,255,0.1) !important; 
        border-radius: 15px !important; 
        border: 1px solid rgba(255,255,255,0.2) !important;
        margin-bottom: 15px !important;
        backdrop-filter: blur(5px);
        overflow: hidden;
        transition: all 0.3s ease;
    }}
    
    div[data-testid="stExpander"]:hover {{
        transform: translateX(5px);
        box-shadow: var(--shadow-md);
    }}
    
    div[data-testid="stExpander"] summary {{
        font-weight: 600 !important;
        color: white !important;
        padding: 15px !important;
        font-size: 16px !important;
    }}
    
    /* Form row styling */
    .form-row {{ 
        display: flex; 
        justify-content: space-between; 
        align-items: center; 
        padding: 12px;
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }}
    
    .form-label {{ 
        color: white !important; 
        font-size: 14px;
        font-weight: 500;
    }}
    
    .btn-action {{ 
        background: var(--gradient-gold);
        color: var(--accent-primary) !important; 
        padding: 6px 15px; 
        border-radius: 20px; 
        text-decoration: none; 
        font-size: 12px; 
        font-weight: bold;
        transition: 0.3s;
        border: none;
    }}
    
    .btn-action:hover {{ 
        opacity: 0.9; 
        transform: scale(1.05);
        box-shadow: 0 5px 15px rgba(255,215,0,0.3);
    }}
    
    /* Typing Indicator */
    .typing-indicator {{
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 15px 20px;
        background: var(--message-bot);
        border-radius: 20px;
        width: fit-content;
        margin: 10px 0;
        border: 1px solid var(--border-color);
    }}
    
    .typing-dot {{
        width: 10px;
        height: 10px;
        background: var(--accent-primary);
        border-radius: 50%;
        animation: typingBounce 1.4s infinite ease-in-out;
    }}
    
    .typing-dot:nth-child(1) {{ animation-delay: -0.32s; }}
    .typing-dot:nth-child(2) {{ animation-delay: -0.16s; }}
    .typing-dot:nth-child(3) {{ animation-delay: 0; }}
    
    @keyframes typingBounce {{
        0%, 80%, 100% {{ transform: scale(0); }}
        40% {{ transform: scale(1); }}
    }}
    
    /* Floating Dino - Centered Fix */
    .floating-dino {{
        position: fixed;
        bottom: 25px;
        right: 25px;
        width: 65px;
        height: 65px;
        background: var(--gradient-primary);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 35px;
        box-shadow: var(--shadow-lg);
        cursor: pointer;
        animation: floatDino 3s ease-in-out infinite;
        z-index: 1000;
        border: 3px solid var(--accent-gold);
        line-height: 1;
        padding: 0;
        margin: 0;
        text-align: center;
    }}
    
    .floating-dino span {{
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        height: 100%;
        transform: translateY(-2px);
    }}
    
    @keyframes floatDino {{
        0% {{ transform: translateY(0px); }}
        50% {{ transform: translateY(-15px); }}
        100% {{ transform: translateY(0px); }}
    }}
    
    .floating-dino:hover {{
        transform: scale(1.1);
        box-shadow: var(--shadow-lg), 0 0 25px var(--accent-gold);
        border-color: white;
    }}
    
    /* Stats Cards */
    .stat-card {{
        background: rgba(255,255,255,0.15);
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        backdrop-filter: blur(5px);
        border: 1px solid rgba(255,255,255,0.2);
        animation: slideInRight 0.5s ease;
    }}
    
    @keyframes slideInRight {{
        from {{ transform: translateX(100%); opacity: 0; }}
        to {{ transform: translateX(0); opacity: 1; }}
    }}
    
    .stat-value {{
        font-size: 28px;
        font-weight: 700;
        color: var(--accent-gold);
        line-height: 1.2;
    }}
    
    .stat-label {{
        font-size: 13px;
        color: rgba(255,255,255,0.9);
        font-weight: 500;
    }}
    
    /* Info box styling */
    .stAlert {{
        background: rgba(255,255,255,0.15) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 15px !important;
    }}
    
    /* Sidebar title */
    .sidebar-title {{ 
        color: rgba(255,255,255,0.9) !important; 
        font-size: 14px; 
        text-transform: uppercase; 
        letter-spacing: 1.5px;
        margin: 20px 0 15px 10px;
        font-weight: 600;
    }}
    
    /* Main title styling */
    .main-title {{
        color: var(--accent-primary);
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 10px;
    }}
    
    .beta-badge {{
        font-size: 14px;
        background: var(--gradient-gold);
        color: var(--accent-primary);
        padding: 5px 15px;
        border-radius: 30px;
        font-weight: 600;
        display: inline-block;
    }}
    
    /* Caption styling */
    .stCaption {{
        color: var(--text-secondary) !important;
        font-size: 14px !important;
        padding: 10px 0;
        border-bottom: 1px solid var(--border-color);
        margin-bottom: 20px;
    }}
    
    /* Progress Bar */
    .progress-container {{
        width: 100%;
        height: 4px;
        background: rgba(255,255,255,0.2);
        border-radius: 2px;
        overflow: hidden;
        margin: 10px 0;
    }}
    
    .progress-bar {{
        height: 100%;
        background: var(--gradient-gold);
        animation: progress 2s ease-in-out infinite;
        width: 0%;
    }}
    
    @keyframes progress {{
        0% {{ width: 0%; }}
        50% {{ width: 100%; }}
        100% {{ width: 0%; }}
    }}
    
    /* Tooltip */
    .tooltip {{
        position: relative;
        display: inline-block;
    }}
    
    .tooltip .tooltiptext {{
        visibility: hidden;
        width: 120px;
        background-color: var(--accent-primary);
        color: white;
        text-align: center;
        border-radius: 6px;
        padding: 5px;
        position: absolute;
        z-index: 1001;
        bottom: 125%;
        left: 50%;
        margin-left: -60px;
        opacity: 0;
        transition: opacity 0.3s;
        font-size: 12px;
        pointer-events: none;
    }}
    
    .tooltip:hover .tooltiptext {{
        visibility: visible;
        opacity: 1;
    }}
    
    /* Responsive Design */
    @media (max-width: 768px) {{
        .custom-header {{ padding: 10px; }}
        .header-logo-img {{ width: 60px; }}
        .univ-name {{ font-size: 16px; }}
        .main-title {{ font-size: 24px; }}
    }}
</style>

<script src="https://cdn.jsdelivr.net/particles.js/2.0.0/particles.min.js"></script>
<div id="particles-js"></div>
<script>
    particlesJS('particles-js', {{
        particles: {{
            number: {{ value: 50, density: {{ enable: true, value_area: 800 }} }},
            color: {{ value: '#{"FFD700" if st.session_state.theme == "light" else "FFC107"}' }},
            shape: {{ type: 'circle' }},
            opacity: {{ value: 0.3, random: true }},
            size: {{ value: 2, random: true }},
            line_linked: {{ enable: true, distance: 150, color: '#{"004D40" if st.session_state.theme == "light" else "006861"}', opacity: 0.2, width: 1 }},
            move: {{ enable: true, speed: 1, direction: 'none', random: true, straight: false, out_mode: 'out' }}
        }},
        interactivity: {{
            detect_on: 'canvas',
            events: {{ onhover: {{ enable: true, mode: 'repulse' }}, onclick: {{ enable: true, mode: 'push' }}, resize: true }},
            modes: {{ repulse: {{ distance: 100, duration: 0.4 }}, push: {{ particles_nb: 2 }} }}
        }},
        retina_detect: true
    }});
</script>
""", unsafe_allow_html=True)

# --- 5. จัดการ API ---
api_key = st.secrets.get("GEMINI_API_KEY")
if api_key: genai.configure(api_key=api_key)

@st.cache_resource
def load_model():
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        selected = next((m for m in available_models if "1.5-flash" in m), available_models[0])
        return genai.GenerativeModel(model_name=selected)
    except: return None
model = load_model()

# --- 6. จัดการ State ---
if "all_chats" not in st.session_state: st.session_state.all_chats = {} 
if "messages" not in st.session_state: st.session_state.messages = []
if "current_chat_id" not in st.session_state: st.session_state.current_chat_id = None
if "global_user_nickname" not in st.session_state: st.session_state.global_user_nickname = "นิสิต"
if "chat_count" not in st.session_state: st.session_state.chat_count = 0
if "total_questions" not in st.session_state: st.session_state.total_questions = 0

# --- 7. Floating Dino Button ---
st.markdown(f'''
    <div class="floating-dino tooltip" onclick="window.scrollTo({{top: document.body.scrollHeight, behavior: 'smooth'}});">
        <span>🦖</span>
        <span class="tooltiptext">{curr["tip"]}</span>
    </div>
''', unsafe_allow_html=True)

# --- 8. Sidebar ---
with st.sidebar:
    # Theme Toggle and Language Toggle - ปรับให้สมดุล
    col1, col2 = st.columns([1, 1])
    with col1:
        theme_icon = "🌙" if st.session_state.theme == "light" else "☀️"
        if st.button(theme_icon, key="theme_toggle"):
            toggle_theme()
            st.rerun()
    
    with col2:
        lang_text = "TH" if st.session_state.lang == "EN" else "EN"
        if st.button(lang_text, key="lang_toggle"):
            toggle_language()
            st.rerun()
    
    # Header with Animation
    if os.path.exists("logo_ku.png"):
        img_data = get_image_base64("logo_ku.png")
        greeting = get_greeting()
        st.markdown(f'''
            <div class="custom-header">
                <img src="data:image/png;base64,{img_data}" class="header-logo-img">
                <div class="univ-name">{curr["univ_name"]}</div>
                <div class="greeting-badge">{greeting}</div>
            </div>
        ''', unsafe_allow_html=True)
    
    # Stats Cards
    st.markdown('<div class="stat-card"><div class="stat-value">' + str(len(st.session_state.all_chats)) + '</div><div class="stat-label">' + curr["chat_hist"] + '</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="stat-card"><div class="stat-value">' + str(st.session_state.total_questions) + '</div><div class="stat-label">' + curr["quick_questions"] + '</div></div>', unsafe_allow_html=True)
    
    # Dino Fact
    st.info(f"🦖 {get_dino_fact()}")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Main Action Buttons
    col_new, col_clear = st.columns(2)
    with col_new:
        if st.button(curr["new_chat"], key="new_chat_btn"):
            st.session_state.messages = []
            st.session_state.current_chat_id = None
            st.session_state.chat_count += 1
            st.rerun()
    with col_clear:
        if st.button(curr["clear_chat"], key="clear_chat_btn"):
            st.session_state.messages = []
            st.rerun()
    
    # Chat History with Animation
    if st.session_state.all_chats:
        st.markdown(f'<p class="sidebar-title">{curr["chat_hist"]}</p>', unsafe_allow_html=True)
        for i, chat_id in enumerate(list(st.session_state.all_chats.keys())):
            if st.button(f"📄 {chat_id[:15]}...", key=f"hist_{chat_id}"):
                st.session_state.current_chat_id = chat_id
                st.session_state.messages = st.session_state.all_chats[chat_id]
                st.rerun()

    # Quick Questions Grid
    st.markdown(f'<p class="sidebar-title">{curr["quick_questions"]}</p>', unsafe_allow_html=True)
    cols = st.columns(2)
    questions = [curr["ask_room"], curr["ask_exam"], curr["ask_gpa"], curr["ask_register"], curr["ask_library"]]
    
    for idx, question in enumerate(questions):
        with cols[idx % 2]:
            if st.button(question, key=f"qq_{idx}"):
                st.session_state.messages.append({"role": "user", "content": question})
                st.rerun()
    
    st.markdown("---")
    
    # Quick Links with Progress Animation
    st.markdown(f'<p class="sidebar-title">Quick Links</p>', unsafe_allow_html=True)
    
    with st.expander(curr["exam_table"], expanded=False):
        st.markdown('<div class="progress-container"><div class="progress-bar"></div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="form-row"><span class="form-label">KU Exam</span><a href="https://reg2.src.ku.ac.th/table_test/" target="_blank" class="btn-action">{curr["btn_find"]}</a></div>', unsafe_allow_html=True)
    
    with st.expander(curr["gpa_calc"], expanded=False):
        st.markdown('<div class="progress-container"><div class="progress-bar"></div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="form-row"><span class="form-label">GPAX</span><a href="https://fna.csc.ku.ac.th/grade/" target="_blank" class="btn-action">{curr["btn_open"]}</a></div>', unsafe_allow_html=True)
    
    with st.expander(curr["forms"], expanded=False):
        st.markdown('<div class="progress-container"><div class="progress-bar"></div></div>', unsafe_allow_html=True)
        forms = [("ใบคำร้องทั่วไป", "https://registrar.ku.ac.th/wp-content/uploads/2023/11/General-Request.pdf")]
        for name, link in forms:
            st.markdown(f'<div class="form-row"><span class="form-label">{name}</span><a href="{link}" target="_blank" class="btn-action">{curr["btn_download"]}</a></div>', unsafe_allow_html=True)

# --- 9. หน้า Chat หลัก ---
st.markdown(f'<div class="main-title">🦖 AI KUSRC <span class="beta-badge">Beta</span></div>', unsafe_allow_html=True)

current_title = st.session_state.current_chat_id if st.session_state.current_chat_id else ( "แชทใหม่" if st.session_state.lang == "TH" else "New Chat")
st.caption(f"👤 {curr['welcome']} **{st.session_state.global_user_nickname}** | {curr['topic']}: *{current_title}* | ⏰ {datetime.now().strftime('%H:%M')}")

# แสดงข้อความ
for message in st.session_state.messages:
    avatar = "🧑‍🎓" if message["role"] == "user" else "🦖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# ส่วนรับ Input
if prompt := st.chat
