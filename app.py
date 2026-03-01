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
# --- 4. CSS (Updated UI Modern/Luxury) ---
st.markdown("""
<style>
    /* ตั้งค่า Font */
    @import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;600&display=swap');
    
    [data-testid="stSidebar"] { 
        background: linear-gradient(180deg, #004D40 0%, #00251A 100%) !important;
        padding: 20px !important;
    }

    /* กล่อง Logo และชื่อมหาวิทยาลัย */
    .brand-card {
        background: rgba(255,255,255,0.05);
        padding: 20px;
        border-radius: 16px;
        text-align: center;
        border: 1px solid rgba(255,215,0,0.2);
        margin-bottom: 20px;
    }

    /* ปุ่มเมนูแบบเรียบหรู */
    div.stButton > button { 
        width: 100% !important;
        border-radius: 12px !important; 
        background: rgba(255,255,255,0.03) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        color: #E0E0E0 !important;
        transition: all 0.3s ease !important;
        justify-content: flex-start !important;
        padding: 12px 15px !important;
    }
    
    div.stButton > button:hover { 
        background: rgba(255,215,0,0.15) !important; 
        border-color: #FFD700 !important;
        color: #FFD700 !important;
    }

    /* หัวข้อ Quick Links */
    .sidebar-title { 
        color: #FFD700 !important; 
        font-size: 11px !important; 
        letter-spacing: 2px !important;
        margin: 30px 0 10px 5px !important;
        font-weight: 600 !important;
    }
    
    /* ปรับแต่ง Expander */
    .stExpander {
        border: none !important;
        background: transparent !important;
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

# --- 7. Sidebar (เพิ่มปุ่มสลับภาษา) ---
with st.sidebar:
    # 1. ส่วนหัว (Brand Card)
    st.markdown('<div class="brand-card">', unsafe_allow_html=True)
    if os.path.exists("logo_ku.png"):
        st.image("logo_ku.png", width=80)
    st.markdown('<div class="univ-name">มหาวิทยาลัย<br>เกษตรศาสตร์</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 2. ปุ่มจัดการหลัก
    if st.button("➕ แชทใหม่"):
        st.session_state.messages = []
        st.rerun()

    # 3. ส่วนประวัติแชท (ใช้ Container)
    st.markdown('<p class="sidebar-title">CHAT HISTORY</p>', unsafe_allow_html=True)
    with st.container(height=250): # กำหนดความสูงเพื่อให้ดูเป็นสัดส่วน
        # ใส่โค้ด loop แสดงประวัติแชทของคุณที่นี่
        pass 

    # 4. ส่วน Quick Links
    st.markdown('<p class="sidebar-title">QUICK LINKS</p>', unsafe_allow_html=True)
    with st.expander("📅 ค้นหาตารางสอบ"):
        st.link_button("เปิดระบบ", "https://reg2.src.ku.ac.th/table_test/", use_container_width=True)
    with st.expander("🧮 คำนวณเกรด (GPA)"):
        st.link_button("เข้าสู่หน้า GPA", "https://fna.csc.ku.ac.th/grade/", use_container_width=True)
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
