import streamlit as st
import google.generativeai as genai
import os
import uuid

# --- 1. การตั้งค่าหน้าจอและ CSS (เน้นขีดสีเขียวเล็กๆ ด้านซ้าย) ---
st.set_page_config(page_title="AI TEST", layout="wide")

st.markdown("""
<style>
    /* สไตล์ปุ่มทั่วไปใน Sidebar (ทำให้ดูคลีนที่สุด) */
    div[data-testid="stSidebar"] button {
        border: none !important;
        background-color: transparent !important;
        text-align: left !important;
        padding-left: 15px !important;
        color: #555 !important;
        width: 100%;
    }

    /* สไตล์ปุ่มที่เลือกอยู่ (Active) - มีแค่ขีดสีเขียวด้านซ้ายนิดเดียว */
    div[data-testid="stSidebar"] button[kind="primary"] {
        border-left: 4px solid #00594C !important; /* ขีดสีเขียวนนทรี */
        background-color: rgba(0, 89, 76, 0.03) !important; /* สีจางๆ แทบไม่เห็น */
        color: #00594C !important;
        font-weight: 600 !important;
        border-radius: 0px !important;
    }
    
    /* ปุ่มเริ่มแชทใหม่ให้ดูแยกสัดส่วน */
    div[data-testid="stSidebar"] .stButton:first-child button {
        background-color: #f0f2f6 !important;
        border-radius: 10px !important;
        margin-bottom: 20px;
        text-align: center !important;
        padding-left: 0px !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("AI TEST")

# --- 2. การตั้งค่า API และ Model ---
api_key = st.secrets.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)

@st.cache_resource
def load_model():
    try:
        # ระบบค้นหา Model อัตโนมัติป้องกัน Error 404
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if "flash" in m.name.lower():
                    return genai.GenerativeModel(model_name=m.name)
        return genai.GenerativeModel(model_name='gemini-1.5-flash')
    except: return None

model = load_model()

# --- 3. ระบบจัดการ Session และความจำกลาง ---
if "user_name" not in st.session_state:
    st.session_state.user_name = None #

if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

# สร้างห้องแชทเริ่มต้นถ้ายังไม่มี
if st.session_state.current_chat_id is None:
    first_id = str(uuid.uuid4())
    st.session_state.chat_sessions[first_id] = {"title": "แชทใหม่", "messages": []}
    st.session_state.current_chat_id = first_id

current_chat_id = st.session_state.current_chat_id
current_chat = st.session_state.chat_sessions[current_chat_id]
messages = current_chat["messages"]

# --- 4. แถบด้านข้าง (Sidebar) ---
with st.sidebar:
    st.header("เมนูควบคุม")
    
    # ปุ่มเริ่มแชทใหม่ (จะสร้างใหม่เฉพาะเมื่อห้องปัจจุบันไม่ว่าง)
    if st.button("+ เริ่มแชทใหม่", use_container_width=True):
        if len(messages) > 0:
            new_id = str(uuid.uuid4())
            st.session_state.chat_sessions[new_id] = {"title": "แชทใหม่", "messages": []}
            st.session_state.current_chat_id = new_id
            st.rerun()
    
    st.write("---")
    st.subheader("ประวัติการคุย")
    
    # วนลูปโชว์แชทเก่า เฉพาะอันที่มีข้อความแล้ว (ตามโจทย์)
    for chat_id, chat_data in reversed(list(st.session_state.chat_sessions.items())):
        if len(chat_data["messages"]) > 0:
            is_active = (chat_id == current_chat_id)
            
            # ใช้ type="primary" เพื่อให้ CSS ใส่ขีดข้างซ้าย
            if st.button(
                chat_data["title"], 
                key=chat_id, 
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                st.session_state.current_chat_id = chat_id
                st.rerun()

# --- 5. ส่วนแสดงผลแชทและ Logic การตอบ ---
for message in messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("พิมพ์ข้อความที่นี่..."):
    # ระบบจำชื่อเบื้องต้น
    if any(k in prompt for k in ["ชื่อ", "ผมชื่อ", "เราชื่อ"]):
        parts = prompt.split("ชื่อ")
        if len(parts) > 1:
            st.session_state.user_name = parts[1].strip().split()[0]

    with st.chat_message("user"):
        st.markdown(prompt)
    messages.append({"role": "user", "content": prompt})
    
    # ตั้งหัวข้อแชทจากประโยคแรก
    if len(messages) == 1:
        current_chat["title"] = prompt[:20] + "..."

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.write("...")
        
        # ดึงประวัติ 10 ข้อความล่าสุดในห้องนั้น
        history = "\n".join([f"{m['role']}: {m['content']}" for m in messages[-10:]])
        user_info = f"คนคุยชื่อคุณ {st.session_state.user_name}" if st.session_state.user_name else "ยังไม่รู้ชื่อ"
        
        # คำสั่งพื้นฐานให้ AI
        instruction = f"คุณคือ 'น้องนนทรี' AI รุ่นพี่ มก. ศรีราชา {user_info}. ตอบอย่างสุภาพและจำชื่อน้องให้ได้ทุกห้องแชท"
        full_prompt = f"{instruction}\n\nประวัติห้องนี้:\n{history}\n\nคำถาม: {prompt}"
        
        try:
            response = model.generate_content(full_prompt)
            res_text = response.text
            placeholder.markdown(res_text)
            messages.append({"role": "assistant", "content": res_text})
            st.rerun() 
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")
