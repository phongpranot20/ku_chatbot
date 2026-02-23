import streamlit as st
import google.generativeai as genai
import os

# ตั้งค่าหน้าจอเบื้องต้น
st.set_page_config(page_title="AI TEST", layout="wide")

# ส่วนหัวข้อหลักตามที่ต้องการ
st.title("AI TEST")

# --- การตั้งค่า API และ Model ---
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("กรุณาใส่ API Key ใน Secrets")
    st.stop()

genai.configure(api_key=api_key)

@st.cache_resource
def load_model():
    # ระบบค้นหาชื่อโมเดลที่ใช้งานได้อัตโนมัติ (ป้องกัน Error 404)
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if "flash" in m.name.lower():
                    return genai.GenerativeModel(model_name=m.name)
        return genai.GenerativeModel(model_name='gemini-1.5-flash')
    except:
        return None

model = load_model()

# --- ระบบจัดการ Session State (ประวัติการแชท) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- แถบด้านข้าง (Sidebar) ---
with st.sidebar:
    st.header("เมนูควบคุม")
    
    # ฟังก์ชัน: กดคุยแชทใหม่ (เริ่มใหม่หมด)
    if st.button("คุยแชทใหม่ (Clear Chat)"):
        st.session_state.messages = []
        st.rerun()
    
    st.write("---")
    st.subheader("ประวัติการคุยล่าสุด")
    # แสดงหัวข้อคำถามย้อนหลังใน Sidebar
    if st.session_state.messages:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.caption(f"Q: {msg['content'][:20]}...")
    else:
        st.write("ยังไม่มีประวัติ")

# --- ส่วนแสดงผลแชทในหน้าหลัก ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- ส่วนรับข้อมูลจากผู้ใช้ ---
if prompt := st.chat_input("พิมพ์ข้อความที่นี่..."):
    # 1. แสดงข้อความผู้ใช้
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. เรียกใช้งาน AI
    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.write("กำลังประมวลผล...")
        
        # ดึงความจำย้อนหลัง (History)
        history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-10:]])
        
        # จัดเตรียมคำสั่งพื้นฐาน (Instruction)
        instruction = "คุณคือ 'น้องนนทรี' AI รุ่นพี่ มก. ศรีราชา ตอบคำถามอย่างเป็นกันเองและจำชื่อผู้ใช้ได้เสมอ"
        full_prompt = f"{instruction}\n\nประวัติ:\n{history}\n\nคำถาม: {prompt}"
        
        try:
            response = model.generate_content(full_prompt)
            placeholder.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            # สั่งรีเฟรชเพื่อให้ Sidebar อัปเดตประวัติทันที
            st.rerun()
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")
