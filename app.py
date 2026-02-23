import streamlit as st
import google.generativeai as genai
import os
import uuid # ใช้สร้าง ID ให้แต่ละห้องแชท

st.set_page_config(page_title="AI TEST", layout="wide")

st.title("AI TEST")

# --- การตั้งค่า API และ Model ---
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("กรุณาใส่ API Key ใน Secrets")
    st.stop()

genai.configure(api_key=api_key)

@st.cache_resource
def load_model():
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if "flash" in m.name.lower():
                    return genai.GenerativeModel(model_name=m.name)
        return genai.GenerativeModel(model_name='gemini-1.5-flash')
    except:
        return None

model = load_model()

# --- ระบบจัดการหลายห้องแชท (Multi-session) ---
# 1. เก็บรวมทุกห้องแชทไว้ใน chat_sessions
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {} # โครงสร้าง {id: {"title": title, "messages": []}}

# 2. เก็บ ID ของห้องแชทที่กำลังเปิดดูอยู่
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

# --- แถบด้านข้าง (Sidebar) ---
with st.sidebar:
    st.header("เมนูควบคุม")
    
    # ปุ่มเริ่มแชทใหม่ (New Chat) - ไม่ได้ลบของเก่า แต่สร้างห้องใหม่
    if st.button("+ เริ่มแชทใหม่"):
        new_id = str(uuid.uuid4())
        st.session_state.chat_sessions[new_id] = {"title": "แชทใหม่", "messages": []}
        st.session_state.current_chat_id = new_id
        st.rerun()
    
    st.write("---")
    st.subheader("ประวัติการคุย")
    
    # แสดงรายการห้องแชทเก่าๆ เรียงจากใหม่ไปเก่า
    for chat_id, chat_data in reversed(list(st.session_state.chat_sessions.items())):
        # ปุ่มเลือกห้องแชท
        if st.button(chat_data["title"], key=chat_id, use_container_width=True):
            st.session_state.current_chat_id = chat_id
            st.rerun()

# --- ตรวจสอบสถานะแชทปัจจุบัน ---
# ถ้ายังไม่มีห้องแชทเลย ให้สร้างอันแรกขึ้นมาอัตโนมัติ
if st.session_state.current_chat_id is None:
    first_id = str(uuid.uuid4())
    st.session_state.chat_sessions[first_id] = {"title": "แชทแรก", "messages": []}
    st.session_state.current_chat_id = first_id

# ดึงข้อมูลของห้องแชทที่เลือกอยู่มาแสดง
current_chat = st.session_state.chat_sessions[st.session_state.current_chat_id]
messages = current_chat["messages"]

# --- ส่วนแสดงผลแชทในหน้าหลัก ---
for message in messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- ส่วนรับข้อมูลจากผู้ใช้ ---
if prompt := st.chat_input("พิมพ์ข้อความที่นี่..."):
    # 1. แสดงข้อความผู้ใช้
    with st.chat_message("user"):
        st.markdown(prompt)
    messages.append({"role": "user", "content": prompt})
    
    # ถ้าเป็นประโยคแรกของห้องนั้น ให้ตั้งเป็นชื่อหัวข้อแชทใน Sidebar
    if len(messages) == 1:
        current_chat["title"] = prompt[:20] + "..."

    # 2. เรียกใช้งาน AI
    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.write("...")
        
        # ดึงความจำย้อนหลัง (เฉพาะของห้องนี้)
        history = "\n".join([f"{m['role']}: {m['content']}" for m in messages[-10:]])
        
        instruction = "คุณคือ 'น้องนนทรี' AI รุ่นพี่ มก. ศรีราชา ตอบคำถามอย่างเป็นกันเองและจำชื่อผู้ใช้ได้เสมอ"
        full_prompt = f"{instruction}\n\nประวัติ:\n{history}\n\nคำถาม: {prompt}"
        
        try:
            response = model.generate_content(full_prompt)
            placeholder.markdown(response.text)
            messages.append({"role": "assistant", "content": response.text})
            # สั่งรีเฟรชเพื่อให้ Sidebar อัปเดตหัวข้อทันที
            st.rerun()
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")
