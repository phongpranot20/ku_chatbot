import streamlit as st
import google.generativeai as genai
import os
import uuid

# --- 1. CSS & UI (ขีดเขียวด้านซ้าย + Avatar บัณฑิต/ไดโนเสาร์) ---
st.set_page_config(page_title="AI TEST", layout="wide")

st.markdown("""
<style>
    div[data-testid="stSidebar"] button {
        border: none !important;
        background-color: transparent !important;
        color: #555 !important;
        text-align: left !important;
        padding-left: 20px !important;
        width: 100% !important;
        display: block !important;
        box-shadow: none !important;
    }
    div[data-testid="stSidebar"] button[kind="primary"] {
        background-color: rgba(0, 89, 76, 0.05) !important;
        border-left: 6px solid #00594C !important;
        color: #00594C !important;
        font-weight: bold !important;
        border-radius: 0px !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. ฟังก์ชันตรวจสอบและเลือกโมเดล (ป้องกัน Error) ---
api_key = st.secrets.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)

@st.cache_resource
def get_working_model():
    try:
        # วนลูปหาโมเดลที่ใช้งานได้จริงใน Key นี้
        available_models = [m.name for m in genai.list_models() 
                            if 'generateContent' in m.supported_generation_methods]
        
        # ลำดับความสำคัญ: ลองหา Flash ก่อน ถ้าไม่มีเอา Pro ถ้าไม่มีเอาตัวแรกที่เจอ
        selected = next((m for m in available_models if "flash" in m), 
                        next((m for m in available_models if "pro" in m), available_models[0]))
        
        return genai.GenerativeModel(selected)
    except Exception as e:
        st.error(f"ไม่สามารถโหลดโมเดลได้: {e}")
        return None

model = get_working_model()

# --- 3. ระบบจัดการ Session & Sidebar (ตามโครงเดิมที่ ฮอน วางไว้) ---
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

if st.session_state.current_chat_id is None:
    first_id = str(uuid.uuid4())
    st.session_state.chat_sessions[first_id] = {"title": "แชทใหม่", "messages": []}
    st.session_state.current_chat_id = first_id

current_chat = st.session_state.chat_sessions[st.session_state.current_chat_id]
messages = current_chat["messages"]

with st.sidebar:
    st.header("เมนูควบคุม")
    if st.button("+ เริ่มแชทใหม่", use_container_width=True):
        if len(messages) > 0:
            new_id = str(uuid.uuid4())
            st.session_state.chat_sessions[new_id] = {"title": "แชทใหม่", "messages": []}
            st.session_state.current_chat_id = new_id
            st.rerun()
    
    st.write("---")
    st.subheader("ประวัติการคุย")
    for chat_id, chat_data in reversed(list(st.session_state.chat_sessions.items())):
        if len(chat_data["messages"]) > 0:
            is_active = (chat_id == st.session_state.current_
