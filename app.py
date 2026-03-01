import streamlit as st
import google.generativeai as genai
import os
import base64
import re

# --- 1. ตั้งค่าหน้าจอ ---
st.set_page_config(page_title="AI KUSRC", page_icon="🦖", layout="wide")

# --- 2. ระบบจัดการภาษา (คงเดิม) ---
if "lang" not in st.session_state:
    st.session_state.lang = "TH"

def toggle_language():
    st.session_state.lang = "EN" if st.session_state.lang == "TH" else "TH"

translation = {
    "TH": {
        "univ_name": "มหาวิทยาลัย<br>เกษตรศาสตร์",
        "new_chat": "➕ แชทใหม่",
        "chat_hist": "💬 ประวัติการแชท",
        "exam_table": "📅 ค้นหาตารางสอบ",
        "gpa_calc": "🧮 คำนวณเกรด (GPA)",
        "forms": "📄 ลิงก์แบบฟอร์มต่างๆ",
        "input_placeholder": "พิมพ์ถามพี่นนทรีได้เลย...",
        "welcome": "สวัสดีครับ มีอะไรให้พี่ช่วยไหม?",
        "loading": "*(กำลังประมวลผล...)*",
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
        return f"📍 ข้อมูลสถานที่: **ตึก {code[:2]} ชั้น {code[2]} ห้อง {code[3:]}**" if st.session_state.lang == "TH" else f"📍 Location: **Building {code[:2]}, Floor {code[2]}, Room {code[3:]}**"
    return None

# --- 4. CSS (Professional & No Colored Icons) ---
st.markdown(f"""
<style>
    .stApp {{ background-color: #FFFFFF; color: #1f1f1f; }}
    [data-testid="stSidebar"] {{ background-color: #f8f9fa !important; border-right: 1px solid #e0e0e0; }}
    
    /* จัดการขนาด Logo ให้คงที่ */
    .sidebar-header {{ text-align: center; padding: 20px 0; }}
    .logo-img {{ width: 100px !important; height: auto; margin-bottom: 10px; }}
    .univ-name {{ color: #006861 !important; font-size: 18px; font-weight: bold; line-height: 1.2; }}

    /* ปุ่มใน Sidebar */
    div.stButton > button {{
        width: 100% !important; border-radius: 12px !important; border: 1px solid #e0e0e0 !important;
        background-color: white !important; color: #444746 !important;
        text-align: left !important; padding: 10px 15px !important;
    }}
    div.stButton > button:hover {{ background-color: #f1f3f4 !important; border-color: #006861 !important; }}
    .st-key-new_chat_btn button {{ background-color: #c2e7ff !important; color: #001d35 !important; font-weight: bold !important; border: none !important; }}

    /* หน้าตาแชทแบบ Professional (No Red/Yellow Icons) */
    .stChatMessage {{ 
        background-color: transparent !important; 
        max-width: 850px !important; 
        margin: 0 auto !important; 
        border: none !important;
    }}
    
    /* ซ่อน Avatar icon เดิมที่ Streamlit ใส่มาให้ เพื่อลบสีแดง/เหลือง */
    [data-testid="chatAvatarIcon-user"], [data-testid="chatAvatarIcon-assistant"] {{
        display: none !important;
    }}
    
    /* ปรับแต่งกล่อง Assistant ให้ดูแพงแบบ Gemini */
    [data-testid="stChatMessageAssistant"] {{
        background-color: #f0f4f9 !important;
        border-radius: 24px !important;
        padding: 20px !important;
    }}
    
    /* ปรับแต่งช่อง Input */
    div[data-testid="stChatInput"] {{
        border: none !important;
        background-color: #f0f4f9 !important;
        border-radius: 30px !important;
        max-width: 850px !important;
        margin: 0 auto !important;
    }}
    
    /* Expander เมนูเสริม */
    .form-row {{ display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #f0f0f0; }}
    .btn-action {{ background-color: #006861; color: white !important; padding: 4px 12px; border-radius: 8px; text-decoration: none; font-size: 12px; }}
</style>
""", unsafe_allow_html=True)

# --- 5. จัดการ API (แก้ Logic ให้คุยได้ปกติ) ---
api_key = st.secrets.get("GEMINI_API_KEY")
if api_key: genai.configure(api_key=api_key)

@st.cache_resource
def load_model():
    try:
        # ดึงโมเดล 1.5-flash มาใช้งาน
        return genai.GenerativeModel(model_name="gemini-1.5-flash")
    except: return None
model = load_model()

# --- 6. จัดการ State ---
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

    if st.session_state.all_chats:
        st.caption(curr["chat_hist"])
        for chat_id in list(st.session_state.all_chats.keys()):
            if st.button(f"💬 {chat_id[:18]}...", key=f"hist_{chat_id}"):
                st.session_state.current_chat_id = chat_id
                st.session_state.messages = st.session_state.all_chats[chat_id]
                st.rerun()

    st.markdown("---")
    with st.expander(curr["exam_table"]):
        st.markdown(f'<div class="form-row"><span>KU Exam</span><a href="https://reg2.src.ku.ac.th/table_test/" target="_blank" class="btn-action">{curr["btn_find"]}</a></div>', unsafe_allow_html=True)
    with st.expander(curr["gpa_calc"]):
        st.markdown(f'<div class="form-row"><span>GPAX</span><a href="https://fna.csc.ku.ac.th/grade/" target="_blank" class="btn-action">{curr["btn_open"]}</a></div>', unsafe_allow_html=True)
    with st.expander(curr["forms"]):
        forms = [("ใบคำร้องทั่วไป", "https://registrar.ku.ac.th/wp-content/uploads/2023/11/General-Request.pdf")]
        for name, link in forms:
            st.markdown(f'<div class="form-row"><span>{name}</span><a href="{link}" target="_blank" class="btn-action">{curr["btn_download"]}</a></div>', unsafe_allow_html=True)

# --- 8. หน้า Chat หลัก ---
if not st.session_state.messages:
    st.markdown(f"<h1 style='text-align: center; color: #006861; margin-top: 15vh;'>{curr['welcome']}</h1>", unsafe_allow_html=True)
else:
    for message in st.session_state.messages:
        # แสดงแชทโดยไม่มี Avatar สีแดง/เหลือง
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if prompt := st.chat_input(curr["input_placeholder"]):
    if st.session_state.current_chat_id is None: st.session_state.current_chat_id = prompt[:20]
    
    # แสดงข้อความฝั่ง User
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # ส่วนตอบกลับของ AI
    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown(curr["loading"])
        
        room_info = get_room_info(prompt)
        if room_info:
            full_response = room_info
            placeholder.markdown(full_response)
        else:
            try:
                kb = ""
                if os.path.exists("ku_data.txt"):
                    with open("ku_data.txt", "r", encoding="utf-8") as f: kb = f.read()
                
                # แก้ไข Logic การสร้าง History ให้ Gemini เข้าใจ
                history = []
                for m in st.session_state.messages[:-1]:
                    role = "user" if m["role"] == "user" else "model"
                    history.append({"role": role, "parts": [m["content"]]})
                
                chat_session = model.start_chat(history=history)
                full_context = f"{curr['ai_identity']}\nข้อมูลมหาลัย: {kb}\nคำถาม: {prompt}"
                
                response = chat_session.send_message(full_context, stream=True)
                full_response = ""
                for chunk in response:
                    if chunk.text:
                        full_response += chunk.text
                        placeholder.markdown(full_response + "▌")
                placeholder.markdown(full_response)
            except Exception as e:
                full_response = f"ขออภัยครับ เกิดข้อผิดพลาดทางเทคนิค: {e}"
                st.error(full_response)
        
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.session_state.all_chats[st.session_state.current_chat_id] = st.session_state.messages
        st.rerun()
