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

# --- 4. CSS ---
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; color: black; }
    [data-testid="stSidebar"] { background-color: #006861 !important; }
    [data-testid="stSidebarContent"] { padding-top: 0rem !important; }
    .custom-header { display: flex; flex-direction: column; align-items: center; text-align: center; padding: 5px; margin-top: -35px; border-bottom: 2px solid rgba(255,255,255,0.2); }
    .header-logo-img { width: 90px; height: auto; margin-bottom: 10px; }
    .univ-name { color: white !important; font-size: 22px; font-weight: bold; line-height: 1.2; }
    .sidebar-title { color: white !important; font-size: 14px; font-weight: bold; margin-bottom: 5px; }
    div.stButton > button { width: 100% !important; border-radius: 12px !important; background-color: transparent !important; color: white !important; border: 1px solid rgba(255, 255, 255, 0.3) !important; padding: 10px 15px !important; text-align: left !important; margin-bottom: 10px !important; }
    div.stButton > button:hover { background-color: rgba(255, 255, 255, 0.2) !important; border-color: #FFD700 !important; }
    div[data-testid="stExpander"] { background-color: #FFFFFF !important; border-radius: 12px !important; margin-bottom: 10px !important; border: none !important; }
    .btn-action { background-color: #006861; color: white !important; padding: 4px 10px; border-radius: 6px; text-decoration: none; font-size: 10px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 5. จัดการ API (คงโมเดลเดิมไว้) ---
api_key = st.secrets.get("GEMINI_API_KEY")
if api_key: genai.configure(api_key=api_key)

@st.cache_resource
def load_model():
    try:
        # ใช้การค้นหาโมเดลแบบเดิมที่คุณเขียนไว้
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
    # ปุ่มสลับภาษาบนสุด
    st.button(f"🌐 {st.session_state.lang}", on_click=toggle_language)

    if os.path.exists("logo_ku.png"):
        img_data = get_image_base64("logo_ku.png")
        st.markdown(f'<div class="custom-header"><img src="data:image/png;base64,{img_data}" class="header-logo-img"><div class="univ-name">{curr["univ_name"]}</div></div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button(curr["new_chat"], key="new_chat_btn"):
        st.session_state.messages = []
        st.session_state.current_chat_id = None
        st.rerun()
    
    if st.session_state.all_chats:
        st.markdown(f'<p class="sidebar-title">{curr["chat_hist"]}</p>', unsafe_allow_html=True)
        for chat_id in list(st.session_state.all_chats.keys()):
            if st.button(f"📄 {chat_id[:18]}...", key=f"hist_{chat_id}"):
                st.session_state.current_chat_id = chat_id
                st.session_state.messages = st.session_state.all_chats[chat_id]
                st.rerun()

    st.markdown("---")
    with st.expander(curr["exam_table"], expanded=False):
        st.markdown(f'<div class="white-card-content"><div class="form-row"><div class="form-label">KU Exam</div><a href="https://reg2.src.ku.ac.th/table_test/" target="_blank" class="btn-action">{curr["btn_find"]}</a></div></div>', unsafe_allow_html=True)
    with st.expander(curr["gpa_calc"], expanded=False):
        st.markdown(f'<div class="white-card-content"><div class="form-row"><div class="form-label">GPAX</div><a href="https://fna.csc.ku.ac.th/grade/" target="_blank" class="btn-action">{curr["btn_open"]}</a></div></div>', unsafe_allow_html=True)
    with st.expander(curr["forms"], expanded=False):
        forms = [("ใบคำร้องทั่วไป", "https://registrar.ku.ac.th/wp-content/uploads/2023/11/General-Request.pdf")]
        for name, link in forms:
            st.markdown(f'<div class="form-row"><div class="form-label">{name}</div><a href="{link}" target="_blank" class="btn-action">{curr["btn_download"]}</a></div>', unsafe_allow_html=True)

# --- 8. หน้า Chat หลัก ---
st.markdown(f"## 🦖 AI TEST")
current_title = st.session_state.current_chat_id if st.session_state.current_chat_id else ( "แชทใหม่" if st.session_state.lang == "TH" else "New Chat")
st.caption(f"👤 {curr['welcome']} {st.session_state.global_user_nickname} | {curr['topic']}: {current_title}")

for message in st.session_state.messages:
    avatar = "🧑‍🎓" if message["role"] == "user" else "🦖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

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
                
                # ปรับแต่งคำสั่ง (Instruction) ตามภาษาที่เลือก
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
