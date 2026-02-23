import streamlit as st
import google.generativeai as genai
import os
import uuid
from datetime import datetime

# --- 1. CSS ขั้นเทพ (เปลี่ยนปุ่มเป็นแถบสี่เหลี่ยมแบบในรูปเป๊ะๆ) ---
st.set_page_config(page_title="AI TEST", layout="wide")

st.markdown("""
<style>
    /* ล้างสไตล์ Sidebar เดิม */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa !important;
    }

    /* สไตล์ปุ่มประวัติ (ทำให้เป็นแถบสี่เหลี่ยม) */
    div.stButton > button {
        width: 100% !important;
        border: none !important;
        background-color: transparent !important;
        padding: 15px 10px !important;
        text-align: left !important;
        display: block !important;
        border-radius: 0px !important;
        border-bottom: 1px solid #eee !important;
        transition: 0.2s;
    }

    /* ปุ่มแชทที่เลือกอยู่ (Active) - ให้มีพื้นหลังสีฟ้าอ่อนและขีดน้ำเงินด้านซ้าย */
    div[data-testid="stSidebar"] button[kind="primary"] {
        background-color: #e9ecef !important; /* สีเทาฟ้าจางๆ แบบในรูป */
        border-left: 5px solid #007bff !important; /* ขีดสีน้ำเงินหนาๆ */
        color: #111 !important;
        font-weight: 600 !important;
    }

    /* ปุ่มแชทที่ไม่ได้เลือก */
    div[data-testid="stSidebar"] button[kind="secondary"] {
        color: #444 !important;
    }

    div[data-testid="stSidebar"] button:hover {
        background-color: #f1f3f5 !important;
    }

    /* ปุ่มแชทใหม่ (ทำให้ดูเด่น) */
    .stSidebar [data-testid="stVerticalBlock"] > div:nth-child(2) button {
        background-color: #00594C !important;
        color: white !important;
        border-radius: 10px !important;
        text-align: center !important;
        margin-bottom: 20px !important;
        border-left: none !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("AI TEST")

# --- 2. การตั้งค่า Model (ป้องกัน Syntax Error) ---
api_key = st.secrets.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)

@st.cache_resource
def get_model():
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        selected = next((m for m in models if "flash" in m), models[0])
        return genai.GenerativeModel(selected)
    except: return None

model = get_model()

# --- 3. ระบบจัดการ Session & Time ---
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

if st.session_state.current_chat_id is None:
    first_id = str(uuid.uuid4())
    st.session_state.chat_sessions[first_id] = {
        "title": "แชทใหม่", 
        "messages": [], 
        "time": datetime.now().strftime("%d/%m/%Y %H:%M")
    }
    st.session_state.current_chat_id = first_id

current_chat = st.session_state.chat_sessions[st.session_state.current_chat_id]
messages = current_chat["messages"]

# --- 4. Sidebar (แถบประวัติแบบในรูป image_c562fe.png) ---
with st.sidebar:
    st.header("เมนูควบคุม")
    if st.button("+ เริ่มแชทใหม่", use_container_width=True):
        if len(messages) > 0:
            new_id = str(uuid.uuid4())
            st.session_state.chat_sessions[new_id] = {
                "title": "แชทใหม่", 
                "messages": [], 
                "time": datetime.now().strftime("%d/%m/%Y %H:%M")
            }
            st.session_state.current_chat_id = new_id
            st.rerun()
    
    st.write("---")
    st.subheader("ประวัติการคุย")
    
    for chat_id, chat_data in reversed(list(st.session_state.chat_sessions.items())):
        if len(chat_data["messages"]) > 0:
            is_active = (chat_id == st.session_state.current_chat_id)
            
            # ตกแต่งชื่อปุ่มให้มี วันเวลา ต่อท้าย (เลียนแบบในรูป)
            
            
            if st.button(
                display_text, 
                key=chat_id, 
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                st.session_state.current_chat_id = chat_id
                st.rerun()

# --- 5. การแสดงผล (🧑‍🎓 บัณฑิต / 🦖 ไดโนเสาร์) ---
for m in messages:
    avatar = "🧑‍🎓" if m["role"] == "user" else "🦖"
    with st.chat_message(m["role"], avatar=avatar):
        st.markdown(m["content"])

if prompt := st.chat_input("พิมพ์ข้อความที่นี่..."):
    with st.chat_message("user", avatar="🧑‍🎓"):
        st.markdown(prompt)
    messages.append({"role": "user", "content": prompt})
    
    if len(messages) == 1:
        # ใช้ข้อความแรกเป็นชื่อ (ตัดให้สั้นลง)
        current_chat["title"] = (prompt[:25] + '...') if len(prompt) > 25 else prompt

    with st.chat_message("assistant", avatar="🦖"):
        placeholder = st.empty()
        placeholder.write("...")
        
        history = "\n".join([f"{m['role']}: {m['content']}" for m in messages[-10:]])
        full_p = f"คุณคือ 'น้องนนทรี' AI รุ่นพี่ มก. ศรีราชา\n\nประวัติ:\n{history}\n\nคำถาม: {prompt}"
        
        try:
            if model:
                response = model.generate_content(full_p)
                placeholder.markdown(response.text)
                messages.append({"role": "assistant", "content": response.text})
                st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")
