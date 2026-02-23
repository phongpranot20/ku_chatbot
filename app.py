import streamlit as st
import google.generativeai as genai
import os
import uuid

st.set_page_config(page_title="AI TEST", layout="wide")

st.title("AI TEST")

# --- การตั้งค่า API และ Model ---
api_key = st.secrets.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)

@st.cache_resource
def load_model():
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if "flash" in m.name.lower():
                    return genai.GenerativeModel(model_name=m.name)
        return genai.GenerativeModel(model_name='gemini-1.5-flash')
    except: return None

model = load_model()

# --- ระบบความจำกลางและ Session ---
if "user_name" not in st.session_state:
    st.session_state.user_name = None

if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

# ตรวจสอบสถานะแชทปัจจุบัน (ถ้าไม่มีให้สร้างห้องชั่วคราวขึ้นมา)
if st.session_state.current_chat_id is None:
    first_id = str(uuid.uuid4())
    st.session_state.chat_sessions[first_id] = {"title": "แชทใหม่", "messages": []}
    st.session_state.current_chat_id = first_id

current_chat_id = st.session_state.current_chat_id
current_chat = st.session_state.chat_sessions[current_chat_id]
messages = current_chat["messages"]

# --- แถบด้านข้าง (Sidebar) ---
with st.sidebar:
    st.header("เมนูควบคุม")
    
    # ปุ่มเริ่มแชทใหม่ กดได้ตลอดเวลา
    if st.button("+ เริ่มแชทใหม่"):
        # เช็คก่อนว่าห้องปัจจุบันว่างไหม ถ้าว่างอยู่แล้วก็ไม่ต้องสร้างใหม่ ให้ใช้ห้องเดิม
        if len(messages) > 0:
            new_id = str(uuid.uuid4())
            st.session_state.chat_sessions[new_id] = {"title": "แชทใหม่", "messages": []}
            st.session_state.current_chat_id = new_id
            st.rerun()
    
    st.write("---")
    st.subheader("ประวัติการคุย")
    
    # [ปรับ Logic] แสดงเฉพาะห้องที่มีข้อความ (messages > 0) เท่านั้น
    for chat_id, chat_data in reversed(list(st.session_state.chat_sessions.items())):
        if len(chat_data["messages"]) > 0:
            is_current = (chat_id == current_chat_id)
            btn_label = f"📍 {chat_data['title']}" if is_current else chat_data['title']
            
            if st.button(btn_label, key=chat_id, use_container_width=True):
                st.session_state.current_chat_id = chat_id
                st.rerun()

# --- ส่วนแสดงผลแชท ---
for message in messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- ส่วนรับข้อมูล ---
if prompt := st.chat_input("พิมพ์ข้อความที่นี่..."):
    # บันทึกชื่อผู้ใช้เข้า Global Memory (Simple Logic)
    if any(keyword in prompt for keyword in ["เราชื่อ", "ผมชื่อ", "ชื่อ"]):
        parts = prompt.split("ชื่อ")
        if len(parts) > 1:
            st.session_state.user_name = parts[1].strip().split()[0]

    with st.chat_message("user"):
        st.markdown(prompt)
    messages.append({"role": "user", "content": prompt})
    
    # เมื่อมีการพิมพ์ครั้งแรก ชื่อห้องจะถูกตั้งค่า และจะเริ่มปรากฏใน Sidebar
    if len(messages) == 1:
        current_chat["title"] = prompt[:20] + "..."

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.write("...")
        
        history = "\n".join([f"{m['role']}: {m['content']}" for m in messages[-10:]])
        user_info = f"คนคุยด้วยชื่อคุณ {st.session_state.user_name}" if st.session_state.user_name else "คุณยังไม่ทราบชื่อผู้ใช้"
        
        instruction = f"คุณคือ 'น้องนนทรี' AI รุ่นพี่ มก. ศรีราชา {user_info}. ตอบอย่างสุภาพและเป็นกันเอง"
        full_prompt = f"{instruction}\n\nประวัติห้องนี้:\n{history}\n\nคำถาม: {prompt}"
        
        try:
            response = model.generate_content(full_prompt)
            res_text = response.text
            placeholder.markdown(res_text)
            messages.append({"role": "assistant", "content": res_text})
            st.rerun() # เพื่อให้ Sidebar อัปเดตรายชื่อห้องทันทีที่มีการตอบ
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")
