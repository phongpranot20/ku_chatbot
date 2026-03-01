import streamlit as st
import google.generativeai as genai
import os
import base64
import re

# --- 1. ตั้งค่าหน้าจอ (Page Config) ---
st.set_page_config(page_title="AI KUSRC", page_icon="🦖", layout="wide")

# --- 2. ระบบจัดการภาษา (Language Management) ---
if "lang" not in st.session_state:
    st.session_state.lang = "TH"

def toggle_language():
    st.session_state.lang = "EN" if st.session_state.lang == "TH" else "TH"

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
        "ai_identity": "คุณคือรุ่นพี่ มก.ศรช. ใจดี ตอบเป็นภาษาไทยเป็นหลัก"
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
        "ai_identity": "You are a friendly KU Sriracha senior. Please respond in English."
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

# --- 4. CSS (Updated UI Modern/Minimal) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Montserrat:wght@300;400;700&display=swap');

    /* พื้นหลังหลัก */
    .stApp { 
        background: #0a0a0a !important;
        color: #ffffff;
    }

    /* Sidebar แบบ Private Concierge */
    [data-testid="stSidebar"] { 
        background: #000 !important;
        border-right: 1px solid #333 !important;
    }

    /* กล่อง Brand Card แบบหรูหรา */
    .brand-card {
        background: rgba(255, 255, 255, 0.03);
        padding: 25px;
        border-radius: 30px;
        text-align: center;
        border: 1px solid rgba(191, 149, 63, 0.3);
        margin-bottom: 30px;
        backdrop-filter: blur(10px);
    }
    
    .univ-name { 
        font-family: 'Playfair Display', serif;
        color: #fcf6ba; 
        font-size: 20px; 
        margin-top: 15px; 
        letter-spacing: 2px;
    }

    /* ปุ่มเมนูสไตล์ Gold */
    div.stButton > button { 
        width: 100% !important;
        border-radius: 50px !important; 
        background: transparent !important;
        border: 1px solid rgba(191, 149, 63, 0.5) !important;
        color: #ffffff !important;
        transition: 0.4s !important;
        text-transform: uppercase;
        font-size: 11px !important;
        letter-spacing: 2px !important;
    }
    
    div.stButton > button:hover { 
        background: linear-gradient(135deg, #bf953f, #b38728) !important;
        color: #000 !important;
        border-color: #fcf6ba !important;
    }

    /* Chat Messages */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 20px !important;
    }

    /* Sidebar Title */
    .sidebar-title { 
        color: #bf953f !important; 
        font-family: 'Montserrat', sans-serif;
        font-size: 10px !important; 
        text-transform: uppercase;
        letter-spacing: 3px !important;
        margin: 20px 0 10px 5px !important;
    }

    /* Expander แบบโปร่งใส */
    div[data-testid="stExpander"] { 
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 15px !important;
        background: rgba(255,255,255,0.02) !important;
    }
</style>
""", unsafe_allow_html=True)
# --- 5. จัดการ API (คงโมเดลเดิมไว้) ---
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

with st.sidebar:
    # 1. ส่วน Header (ใช้คลาส brand-card ที่เราสร้างไว้ใน CSS)
    st.markdown('<div class="brand-card">', unsafe_allow_html=True)
    if os.path.exists("logo_ku.png"):
        img_data = get_image_base64("logo_ku.png")
        st.markdown(f'<img src="data:image/png;base64,{img_data}" class="header-logo-img">', unsafe_allow_html=True)
    st.markdown(f'<div class="univ-name">{curr["univ_name"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 2. ปุ่มสลับภาษา (ย้ายมาไว้ใต้โลโก้เพื่อให้บาลานซ์)
    st.button(f"🌐 {st.session_state.lang}", on_click=toggle_language, use_container_width=True)

    # 3. ปุ่มแชทใหม่
    if st.button(curr["new_chat"], key="new_chat_btn"):
        st.session_state.messages = []
        st.session_state.current_chat_id = None
        st.rerun()
    
    # 4. ประวัติแชท (ใช้ Container ควบคุมความสูงเพื่อไม่ให้หน้ายาวเกินไป)
    if st.session_state.all_chats:
        st.markdown(f'<p class="sidebar-title">{curr["chat_hist"]}</p>', unsafe_allow_html=True)
        with st.container(height=200): 
            for chat_id in list(st.session_state.all_chats.keys()):
                if st.button(f"📄 {chat_id[:18]}...", key=f"hist_{chat_id}"):
                    st.session_state.current_chat_id = chat_id
                    st.session_state.messages = st.session_state.all_chats[chat_id]
                    st.rerun()

    # 5. Quick Links (ใช้ Divider กั้นเพื่อความสมดุล)
    st.markdown("---")
    st.markdown(f'<p class="sidebar-title">Quick Links</p>', unsafe_allow_html=True)
    
    with st.expander(curr["exam_table"], expanded=False):
        st.markdown(f'<div class="form-row"><div class="form-label">KU Exam</div><a href="https://reg2.src.ku.ac.th/table_test/" target="_blank" class="btn-action">{curr["btn_find"]}</a></div>', unsafe_allow_html=True)
    
    with st.expander(curr["gpa_calc"], expanded=False):
        st.markdown(f'<div class="form-row"><div class="form-label">GPAX</div><a href="https://fna.csc.ku.ac.th/grade/" target="_blank" class="btn-action">{curr["btn_open"]}</a></div>', unsafe_allow_html=True)
    
    with st.expander(curr["forms"], expanded=False):
        forms = [("ใบคำร้องทั่วไป", "https://registrar.ku.ac.th/wp-content/uploads/2023/11/General-Request.pdf")]
        for name, link in forms:
            st.markdown(f'<div class="form-row"><div class="form-label">{name}</div><a href="{link}" target="_blank" class="btn-action">{curr["btn_download"]}</a></div>', unsafe_allow_html=True)
# --- 8. หน้า Chat หลัก ---
st.markdown(f"<h2 style='color: #004D40;'>🦖 AI KUSRC</h2>", unsafe_allow_html=True)
current_title = st.session_state.current_chat_id if st.session_state.current_chat_id else ( "แชทใหม่" if st.session_state.lang == "TH" else "New Chat")
st.caption(f"👤 {curr['welcome']} {st.session_state.global_user_nickname} | {curr['topic']}: {current_title}")

# แสดงข้อความ
for message in st.session_state.messages:
    avatar = "🧑‍🎓" if message["role"] == "user" else "🦖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# ส่วนรับ Input
if prompt := st.chat_input(curr["input_placeholder"]):
    if st.session_state.current_chat_id is None: st.session_state.current_chat_id = prompt[:20]

    st.chat_message("user", avatar="🧑‍🎓").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="🦖"):
        room_info = get_room_info(prompt)
        if room_info:
            full_response = room_info
            st.markdown(full_response)
        else:
            placeholder = st.empty()
            placeholder.markdown(curr["loading"])
            try:
                knowledge_base = ""
                if os.path.exists("ku_data.txt"):
                    with open("ku_data.txt", "r", encoding="utf-8") as f: knowledge_base = f.read()
                
                history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[-6:-1]]
                chat_session = model.start_chat(history=history)
                
                full_context = f"{curr['ai_identity']} คุยกับน้องชื่อ {st.session_state.global_user_nickname} ข้อมูลมหาลัย:\n{knowledge_base}\n\nคำถาม: {prompt}"
                
                response = chat_session.send_message(full_context, stream=True)
                full_response = ""
                for chunk in response:
                    full_response += chunk.text
                    placeholder.markdown(full_response + "▌")
                placeholder.markdown(full_response)
            except Exception as e:
                full_response = f"Error: {e}"
                st.error(full_response)
        
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.session_state.all_chats[st.session_state.current_chat_id] = st.session_state.messages
        st.rerun()
