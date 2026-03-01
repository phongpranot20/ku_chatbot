import streamlit as st
import google.generativeai as genai
import os
import base64
import re

# --- 1. ตั้งค่าหน้าจอ (Page Config) ---
st.set_page_config(page_title="AI KUSRC", page_icon="🦖", layout="wide")

# --- 2. ระบบจัดการภาษา ---
if "lang" not in st.session_state:
    st.session_state.lang = "TH"

def toggle_language():
    st.session_state.lang = "EN" if st.session_state.lang == "TH" else "TH"

translation = {
    "TH": {
        "univ_name": "Kasetsart University<br><small>Sriracha Campus</small>",
        "new_chat": "➕ เริ่มแชทใหม่",
        "chat_hist": "ประวัติการสนทนา",
        "input_placeholder": "พิมพ์คำถามของคุณที่นี่...",
        "welcome_main": "มีอะไรให้พี่ช่วยไหม?",
        "loading": "กำลังประมวลผล...",
        "ai_identity": "คุณคือรุ่นพี่ มก.ศรช. ใจดี ตอบเป็นภาษาไทยเป็นหลัก",
        "quick_1": "📅 ตารางสอบ", "quick_2": "🧮 คำนวณเกรด", "quick_3": "📄 แบบฟอร์ม", "quick_4": "🔍 ข้อมูลหอพัก"
    },
    "EN": {
        "univ_name": "Kasetsart University<br><small>Sriracha Campus</small>",
        "new_chat": "➕ New Chat",
        "chat_hist": "Recent Chats",
        "input_placeholder": "Message Nontri AI...",
        "welcome_main": "How can I help you?",
        "loading": "Thinking...",
        "ai_identity": "You are a friendly KU Sriracha senior. Please respond in English.",
        "quick_1": "📅 Exam", "quick_2": "🧮 GPA", "quick_3": "📄 Forms", "quick_4": "🔍 Dorm"
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
        # Simple logic preserved as requested
        return f"📍 ห้อง {code} อยู่ที่อาคารเรียนรวมครับน้อง" if st.session_state.lang == "TH" else f"📍 Room {code} is located in the main building."
    return None

# --- 4. CSS (Modern & Clean UI) ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    
    html, body, [class*="st-"] {{ font-family: 'Inter', sans-serif; }}
    
    /* Main Background */
    .stApp {{ background-color: #FFFFFF; }}

    /* Sidebar Styling */
    [data-testid="stSidebar"] {{
        background-color: #f9f9f9 !important;
        border-right: 1px solid #eee;
    }}
    
    /* Sidebar Header */
    .sidebar-brand {{
        padding: 1.5rem;
        text-align: center;
        border-bottom: 1px solid #eee;
        margin-bottom: 1rem;
    }}
    .univ-name {{ color: #006861; font-weight: 700; font-size: 1.1rem; line-height: 1.1; }}

    /* Chat Input Styling */
    .stChatInputContainer {{
        padding-bottom: 2rem !important;
        background-color: transparent !important;
    }}
    
    div[data-testid="stChatInput"] {{
        border-radius: 20px !important;
        border: 1px solid #e5e5e5 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
    }}

    /* Hero Text */
    .hero-container {{
        text-align: center;
        margin-top: 10vh;
        margin-bottom: 2rem;
    }}
    .hero-title {{
        font-size: 2.5rem;
        font-weight: 600;
        color: #212121;
        margin-bottom: 2rem;
    }}

    /* Quick Action Buttons */
    .quick-action-container {{
        display: flex;
        justify-content: center;
        gap: 10px;
        flex-wrap: wrap;
        max-width: 800px;
        margin: 0 auto;
    }}
    .quick-btn {{
        padding: 10px 20px;
        border: 1px solid #e5e5e5;
        border-radius: 15px;
        background: white;
        cursor: pointer;
        font-size: 0.9rem;
        transition: 0.3s;
    }}
    .quick-btn:hover {{ background: #f0f0f0; }}

    /* Message Bubbles */
    .stChatMessage {{ background-color: transparent !important; border: none !important; }}
    [data-testid="chatAvatarIcon-user"], [data-testid="chatAvatarIcon-assistant"] {{ background-color: #006861 !important; }}
</style>
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

# --- 7. Sidebar ---
with st.sidebar:
    st.markdown(f'<div class="sidebar-brand"><div class="univ-name">{curr["univ_name"]}</div></div>', unsafe_allow_html=True)
    
    st.button(f"🌐 Language: {st.session_state.lang}", on_click=toggle_language, use_container_width=True)
    
    if st.button(curr["new_chat"], key="new_chat_btn", use_container_width=True, type="primary"):
        st.session_state.messages = []
        st.session_state.current_chat_id = None
        st.rerun()

    st.markdown(f"### {curr['chat_hist']}")
    for chat_id in list(st.session_state.all_chats.keys()):
        if st.button(f"💬 {chat_id[:20]}...", key=f"hist_{chat_id}", use_container_width=True):
            st.session_state.current_chat_id = chat_id
            st.session_state.messages = st.session_state.all_chats[chat_id]
            st.rerun()

# --- 8. หน้า Chat หลัก ---

# แสดง Hero UI เฉพาะตอนที่ยังไม่มีการคุย
if not st.session_state.messages:
    st.markdown(f"""
    <div class="hero-container">
        <div class="hero-title">{curr['welcome_main']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick Actions (ปุ่มทางลัด)
    cols = st.columns(4)
    with cols[0]: 
        if st.button(curr["quick_1"], use_container_width=True): prompt_pre = "ตารางสอบ"
    with cols[1]: 
        if st.button(curr["quick_2"], use_container_width=True): prompt_pre = "คำนวณเกรด"
    with cols[2]: 
        if st.button(curr["quick_3"], use_container_width=True): prompt_pre = "แบบฟอร์ม"
    with cols[3]: 
        if st.button(curr["quick_4"], use_container_width=True): prompt_pre = "หอพัก"

# แสดงประวัติแชท
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ส่วนรับ Input
if prompt := st.chat_input(curr["input_placeholder"]):
    if st.session_state.current_chat_id is None: 
        st.session_state.current_chat_id = prompt[:30]

    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        room_info = get_room_info(prompt)
        if room_info:
            full_response = room_info
            st.markdown(full_response)
        else:
            placeholder = st.empty()
            placeholder.markdown(f"*{curr['loading']}*")
            try:
                knowledge_base = ""
                if os.path.exists("ku_data.txt"):
                    with open("ku_data.txt", "r", encoding="utf-8") as f: knowledge_base = f.read()
                
                history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[-6:-1]]
                chat_session = model.start_chat(history=history)
                
                full_context = f"{curr['ai_identity']} คุยกับน้อง {st.session_state.global_user_nickname} ข้อมูลมหาลัย:\n{knowledge_base}\nคำถาม: {prompt}"
                
                response = chat_session.send_message(full_context, stream=True)
                full_response = ""
                for chunk in response:
                    full_response += chunk.text
                    placeholder.markdown(full_response + "▌")
                placeholder.markdown(full_response)
            except Exception as e:
                full_response = f"ขออภัยครับ เกิดข้อผิดพลาด: {e}"
                st.error(full_response)
        
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.session_state.all_chats[st.session_state.current_chat_id] = st.session_state.messages
        st.rerun()
