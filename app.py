import streamlit as st
import google.generativeai as genai
import os
import base64
import re

# --- 1. ตั้งค่าหน้าจอ ---
st.set_page_config(page_title="AI KUSRC", page_icon="🦖", layout="wide")

# --- 2. ระบบจัดการภาษา ---
if "lang" not in st.session_state:
    st.session_state.lang = "TH"

def toggle_language():
    st.session_state.lang = "EN" if st.session_state.lang == "TH" else "TH"

translation = {
    "TH": {
        "univ_name": "Kasetsart University<br>Sriracha Campus",
        "new_chat": "เริ่มแชทใหม่",
        "chat_hist": "ประวัติการสนทนา",
        "input_placeholder": "พิมพ์คำถามของคุณที่นี่...",
        "welcome_main": "สวัสดีครับ มีอะไรให้พี่ช่วยไหม?",
        "loading": "รอสักครู่นะครับ...",
        "ai_identity": "คุณคือรุ่นพี่ มก.ศรช. ใจดี ตอบเป็นภาษาไทยเป็นหลัก"
    },
    "EN": {
        "univ_name": "Kasetsart University<br>Sriracha Campus",
        "new_chat": "New Chat",
        "chat_hist": "Recent Chats",
        "input_placeholder": "Message Nontri AI...",
        "welcome_main": "How can I help you?",
        "loading": "Thinking...",
        "ai_identity": "You are a friendly KU Sriracha senior. Please respond in English."
    }
}
curr = translation[st.session_state.lang]

# --- 3. ฟังก์ชันดึงโลโก้ (แก้ให้ดึงจากไฟล์ logo_ku.png ในโฟลเดอร์หลัก) ---
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

logo_base64 = get_image_base64("logo_ku.png")

# --- 4. CSS ใหม่ (สีเขียว KU มินิมอล ไม่แดงแน่นอน!) ---
st.markdown(f"""
<style>
    /* ปรับพื้นหลังหลัก */
    .stApp {{ background-color: #FFFFFF; }}
    
    /* Sidebar: สีเทาอ่อนมินิมอล */
    [data-testid="stSidebar"] {{
        background-color: #F8F9FA !important;
        border-right: 1px solid #E0E0E0;
    }}

    /* จัดวางโลโก้และชื่อมหาลัยใน Sidebar */
    .sidebar-header {{
        text-align: center;
        padding: 20px 10px;
    }}
    .logo-img {{
        width: 80px;
        margin-bottom: 10px;
    }}
    .univ-title {{
        color: #006861;
        font-weight: bold;
        font-size: 16px;
        line-height: 1.2;
    }}

    /* ปุ่มใน Sidebar: แก้จากสีแดงเป็นสีเขียวมินิมอล */
    div.stButton > button {{
        background-color: white !important;
        color: #006861 !important;
        border: 1px solid #006861 !important;
        border-radius: 10px !important;
        transition: 0.3s;
    }}
    div.stButton > button:hover {{
        background-color: #006861 !important;
        color: white !important;
    }}

    /* ปุ่มเริ่มแชทใหม่ (ทำให้เด่นแต่ยังคุมโทนเขียว) */
    .st-key-new_chat_btn button {{
        background-color: #006861 !important;
        color: white !important;
        font-weight: bold !important;
    }}

    /* ปรับแต่งกล่องแชท */
    .stChatMessage {{ border-radius: 15px; }}
</style>
""", unsafe_allow_html=True)

# --- 5. จัดการ API (คงเดิม) ---
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

# --- 6. State Management ---
if "all_chats" not in st.session_state: st.session_state.all_chats = {} 
if "messages" not in st.session_state: st.session_state.messages = []
if "current_chat_id" not in st.session_state: st.session_state.current_chat_id = None

# --- 7. Sidebar ---
with st.sidebar:
    # ส่วนหัวโลโก้
    st.markdown('<div class="sidebar-header">', unsafe_allow_html=True)
    if logo_base64:
        st.markdown(f'<img src="data:image/png;base64,{logo_base64}" class="logo-img">', unsafe_allow_html=True)
    st.markdown(f'<div class="univ-title">{curr["univ_name"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.button(f"🌐 {st.session_state.lang}", on_click=toggle_language, use_container_width=True)
    
    if st.button(curr["new_chat"], key="new_chat_btn", use_container_width=True):
        st.session_state.messages = []
        st.session_state.current_chat_id = None
        st.rerun()

    st.markdown(f"**{curr['chat_hist']}**")
    for chat_id in list(st.session_state.all_chats.keys()):
        if st.button(f"📄 {chat_id[:15]}...", key=f"hist_{chat_id}", use_container_width=True):
            st.session_state.current_chat_id = chat_id
            st.session_state.messages = st.session_state.all_chats[chat_id]
            st.rerun()

# --- 8. Main Chat Logic ---
if not st.session_state.messages:
    st.markdown(f"<h1 style='text-align: center; color: #006861; margin-top: 50px;'>{curr['welcome_main']}</h1>", unsafe_allow_html=True)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input(curr["input_placeholder"]):
    if st.session_state.current_chat_id is None: st.session_state.current_chat_id = prompt[:30]
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown(f"*{curr['loading']}*")
        try:
            # ดึงข้อมูลจาก ku_data.txt ถ้ามี
            kb = ""
            if os.path.exists("ku_data.txt"):
                with open("ku_data.txt", "r", encoding="utf-8") as f: kb = f.read()
            
            history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[-6:-1]]
            chat_session = model.start_chat(history=history)
            
            full_context = f"{curr['ai_identity']}\nข้อมูลมหาลัย: {kb}\nคำถาม: {prompt}"
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
