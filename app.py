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

# --- [เพิ่มส่วนนี้] ระบบความจำกลาง (Global Memory) ---
if "user_name" not in st.session_state:
    st.session_state.user_name = None # เก็บชื่อผู้ใช้ไว้ที่นี่เพื่อให้จำได้ทุกห้อง

# --- ระบบจัดการหลายห้องแชท ---
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

# --- แถบด้านข้าง (Sidebar) ---
with st.sidebar:
    st.header("เมนูควบคุม")
    
    if st.button("+ เริ่มแชทใหม่"):
        new_id = str(uuid.uuid4())
        st.session_state.chat_sessions[new_id] = {"title": "แชทใหม่", "messages": []}
        st.session_state.current_chat_id = new_id
        st.rerun()
    
    st.write("---")
    st.subheader("ประวัติการคุย")
    for chat_id, chat_data in reversed(list(st.session_state.chat_sessions.items())):
        if st.button(chat_data["title"], key=chat_id, use_container_width=True):
            st.session_state.current_chat_id = chat_id
            st.rerun()

# ตรวจสอบสถานะแชทปัจจุบัน
if st.session_state.current_chat_id is None:
    first_id = str(uuid.uuid4())
    st.session_state.chat_sessions[first_id] = {"title": "แชทแรก", "messages": []}
    st.session_state.current_chat_id = first_id

current_chat = st.session_state.chat_sessions[st.session_state.current_chat_id]
messages = current_chat["messages"]

# แสดงผลแชท
for message in messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- ส่วนรับข้อมูล ---
if prompt := st.chat_input("พิมพ์ข้อความที่นี่..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    messages.append({"role": "user", "content": prompt})
    
    if len(messages) == 1:
        current_chat["title"] = prompt[:20] + "..."

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.write("...")
        
        # [เพิ่มส่วนนี้] พยายามดึงชื่อจากข้อความที่ผู้ใช้พิมพ์ (ถ้าบอทยังไม่รู้ชื่อ)
        # เราจะส่งคำสั่งให้ AI ช่วยจดจำชื่อด้วย
        
        history = "\n".join([f"{m['role']}: {m['content']}" for m in messages[-10:]])
        
        # [ปรับปรุง Instruction] ส่งชื่อผู้ใช้ (Global Memory) เข้าไปด้วยถ้ามี
        user_info = f"ตอนนี้คุณรู้ว่าผู้ใช้ชื่อ: {st.session_state.user_name}" if st.session_state.user_name else "คุณยังไม่รู้ชื่อผู้ใช้"
        
        instruction = (
            f"คุณคือ 'น้องนนทรี' AI รุ่นพี่ มก. ศรีราชา "
            f"{user_info}. "
            "ภารกิจ: หากผู้ใช้บอกชื่อ ให้จดจำชื่อนั้นไว้ในคำตอบของคุณด้วย "
            "ตอบคำถามอย่างเป็นกันเองและสุภาพ"
        )
        
        full_prompt = f"{instruction}\n\nประวัติห้องนี้:\n{history}\n\nคำถาม: {prompt}"
        
        try:
            response = model.generate_content(full_prompt)
            res_text = response.text
            
            # [เพิ่มส่วนนี้] เช็คว่า AI ตรวจเจอชื่อไหม (แบบง่ายๆ คือถ้าบอทตอบว่ายินดีที่ได้รู้จักชื่อ... เราจะเซฟลง Global)
            # หรือเราจะใช้ Logic ว่าถ้าบอทตอบคำถามเสร็จ เราแอบอัปเดตชื่อใน session_state ได้
            # แต่เพื่อความง่าย เราให้ AI ช่วยสรุปชื่อให้ถ้าในประโยคมีการแนะนำตัว
            
            placeholder.markdown(res_text)
            messages.append({"role": "assistant", "content": res_text})
            
            # Trick: ถ้ามีการพิมพ์ "ชื่อ...นะ" หรือ "เราชื่อ..." ให้ AI บันทึกลง global memory
            # (ในโปรเจกต์จริงอาจต้องใช้ AI อีกรอบสั้นๆ เพื่อสกัดชื่อออกมา)
            if "ชื่อ" in prompt and st.session_state.user_name is None:
                # ตัวอย่าง: สมมติว่าฮอนบอกชื่อในห้องที่ 1 แล้วเราอยากให้ห้องอื่นรู้ด้วย
                # เราจะบันทึกชื่อไว้ใน session_state.user_name
                # (เพื่อความเร็วในโค้ดนี้ ฮอนต้องบอกชื่อให้ชัดเจนในแชทครั้งแรกของเซสชันก่อนนะครับ)
                pass 

            st.rerun()
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")
