import streamlit as st
import google.generativeai as genai
import os
import base64
import re

# --- 1. ตั้งค่าหน้าจอ (คงเดิม) ---
st.set_page_config(page_title="AI KUSRC", page_icon="🦖", layout="wide")

# --- 2. ระบบจัดการภาษา (คงเดิม) ---
if "lang" not in st.session_state:
    st.session_state.lang = "TH"

def toggle_language():
    st.session_state.lang = "EN" if st.session_state.lang == "TH" else "TH"

translation = {
    "TH": {
        "univ_name": "มหาวิทยาลัย<br>เกษตรศาสตร์",
        "new_chat": "➕ เริ่มแชทใหม่",
        "chat_hist": "💬 ประวัติการแชท",
        "exam_table": "📅 ค้นหาตารางสอบ",
        "gpa_calc": "🧮 คำนวณเกรด (GPA)",
        "forms": "📄 ลิงก์แบบฟอร์มต่างๆ",
        "input_placeholder": "พิมพ์ถามพี่นนทรีได้เลย...",
        "welcome": "สวัสดีครับ มีอะไรให้พี่ช่วยไหม?",
        "loading": "*(กำลังหาคำตอบให้...)*",
        "btn_find": "ค้นหา", "btn_open": "เปิดระบบ", "btn_download": "โหลด",
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
        "welcome": "How can I help you today?",
        "loading": "*(Thinking...)*",
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
    if len(code) >= 4:
        return f"📍 ข้อมูลสถานที่: **ตึก {code[:2]} ชั้น {code[2]} ห้อง {code[3:]}**"
    return None

# --- 4. CSS (เจาะจงลบไอคอนแดง/ส้มทิ้ง 100%) ---
st.markdown(f"""
<style>
    /* ลบ Avatar (ไอคอนสีแดง/ส้ม) ออกทั้งหมด */
    div[data-testid="chatAvatarIcon-user"], 
    div[data-testid="chatAvatarIcon-assistant"],
    div[data-testid="stChatMessage"] figure {{
        display: none !important;
    }}
    
    /* จัดช่องว่างข้อความใหม่หลังลบไอคอน */
    div[data-testid="stChatMessage"] {{
        padding-left: 0px !important;
        margin-left: 0px !important;
    }}

    /* ปรับแต่งกล่องแชทให้ดู Pro แบบ Gemini */
    [data-testid="stChatMessageAssistant"] {{
        background-color: #f0f4f9 !important;
        border-radius: 20px !important;
        padding: 15px 20px !important;
        margin-bottom: 10px !important;
    }}
    
    /* Sidebar และ Logo */
    .sidebar-header {{ text-align: center; padding: 10px; }}
    .logo-img {{ width: 100px !important; height: auto; }}
    .univ-name {{ color: #006861 !important; font-size: 18px; font-weight: bold; }}

    /* ส่วนอื่นๆ คงความมินิมอล */
    div[data-testid="stChatInput"] {{
        border-radius: 30px !important;
        background-color: #f8f9fa !important;
    }}
</style>
""", unsafe_allow_html=True)

# --- 5. จัดการ API (ใช้ Logic เดิมเพื่อให้คุยได้ปกติ) ---
api_key = st.secrets.get("GEMINI_API_KEY")
if api_key: genai.configure(api_key=api_key)

@st.cache_resource
def load_model():
    try:
        # ใช้ Logic การดึงโมเดลแบบเดิมที่น้องเขียนไว้เพื่อป้องกัน 404
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        selected = next((m for m in available_models if "1.5-flash" in m), available_models[0])
        return genai.GenerativeModel(model_name=selected)
    except: return None
model = load_model()

# --- 6. State Management ---
if "all_chats" not in st.session_state: st.session_state.all_chats = {} 
if "messages" not in st.session_state: st.session_state.messages = []
if "current_chat_id" not in st.session_state: st.session_state.current_chat_id = None

# --- 7. Sidebar ---
with st.sidebar:
    st.markdown('<div class="sidebar-header">', unsafe_allow_html=True)
    logo_data = get_image_base64("logo_ku.png")
    if logo_data:
        st.markdown(f'<img src="data:image/png;base64,{logo_data}" class="logo-img">', unsafe_allow_html=True)
    st.markdown(f'<div class="univ-name">{curr["univ_name"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.button(f"🌐 {st.session_state.lang}", on_click=toggle_language, use_container_width=True)
    
    if st.button(curr["new_chat"], key="new_chat_btn"):
        st.session_state.messages = []
        st.session_state.current_chat_id = None
        st.rerun()

    st.markdown("---")
    with st.expander(curr["exam_table"]):
        st.markdown(f'<a href="https://reg2.src.ku.ac.th/table_test/" target="_blank">🔍 {curr["btn_find"]}</a>', unsafe_allow_html=True)
    with st.expander(curr["gpa_calc"]):
        st.markdown(f'<a href="https://fna.csc.ku.ac.th/grade/" target="_blank">🧮 {curr["btn_open"]}</a>', unsafe_allow_html=True)

# --- 8. Main Chat Logic ---
if not st.session_state.messages:
    st.markdown(f"<h1 style='text-align: center; color: #006861; margin-top: 15vh;'>{curr['welcome']}</h1>", unsafe_allow_html=True)
else:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if prompt := st.chat_input(curr["input_placeholder"]):
    if st.session_state.current_chat_id is None: st.session_state.current_chat_id = prompt[:20]
    
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown(curr["loading"])
        
        try:
            knowledge_base = ""
            if os.path.exists("ku_data.txt"):
                with open("ku_data.txt", "r", encoding="utf-8") as f: knowledge_base = f.read()
            
            # รักษา Logic ประวัติการแชทเดิม
            history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[-6:-1]]
            chat_session = model.start_chat(history=history)
            
            full_context = f"{curr['ai_identity']}\nข้อมูลมหาลัย: {knowledge_base}\nคำถาม: {prompt}"
            response = chat_session.send_message(full_context, stream=True)
            
            full_response = ""
            for chunk in response:
                full_response += chunk.text
                placeholder.markdown(full_response + "▌")
            placeholder.markdown(full_response)
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")
        
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.rerun()
