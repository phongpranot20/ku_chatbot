import streamlit as st
import google.generativeai as genai
import os
import uuid

# --- 1. การตั้งค่าหน้าจอและ CSS (เน้นเฉพาะส่วนแถบสีปุ่ม) ---
st.set_page_config(page_title="AI TEST", layout="wide")

st.markdown("""
<style>
    /* สไตล์ปุ่มที่ถูกเลือกใน Sidebar (Active State) */
    div[data-testid="stSidebar"] button[kind="primary"] {
        background-color: #00594C !important; /* สีเขียวนนทรี */
        color: white !important;
        border: none;
        font-weight: bold;
    }
    
    /* สไตล์ปุ่มทั่วไปใน Sidebar */
    div[data-testid="stSidebar"] button[kind="secondary"] {
        background-color: transparent;
        border: 1px solid #e0e0e0;
        color: #333;
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
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if "flash" in m.name.lower():
                    return genai.GenerativeModel(model_name=m.name)
        return genai.GenerativeModel(model_name='gemini-1.5-flash')
    except: return None

model = load_model()

# --- 3. ระบบความจำกลางและ Session Management ---
if "user_name" not in st.session_state:
    st.session_state.user_name = None

if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

# ตรวจสอบว่ามีห้องแชทหรือยัง ถ้าไม่มีให้สร้างอันแรกขึ้นมา
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
    
    # ปุ่มเริ่มแชทใหม่ (จะสร้างใหม่เฉพาะเมื่อห้องปัจจุบันมีการคุยแล้วเท่านั้น)
    if st.button("+ เริ่มแชทใหม่", use_container_width=True):
        if len(messages) > 0:
            new_id = str(uuid.uuid4())
            st.session_state.chat_sessions[new_id] = {"title": "แชทใหม่", "messages": []}
            st.session_state.current_chat_id = new_id
            st.rerun()
    
    st.write("---")
    st.subheader("ประวัติการคุย")
    
    # แสดงเฉพาะห้องที่มีข้อความ (messages > 0)
    for chat_id, chat_data in reversed(list(st.session_state.chat_sessions.items())):
        if len(chat_data["messages"]) > 0:
            # เช็คว่าเป็นห้องปัจจุบันไหมเพื่อเปลี่ยนสีแถบ
            is_active = (chat_id == current_chat_id)
            
            if st.button(
                chat_data["title"], 
                key=chat_id, 
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                st.session_state.current_chat_id = chat_id
                st.rerun()

# --- 5. ส่วนแสดงผลแชทและรับข้อมูล ---
for message in messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("พิมพ์ข้อความที่นี่..."):
    # ระบบจดจำชื่อแบบง่ายเข้า Global Memory
    if any(keyword in prompt for keyword in ["เราชื่อ", "ผมชื่อ", "ชื่อ"]):
        parts = prompt.split("ชื่อ")
        if len(parts) > 1:
            st.session_state.user_name = parts[1].strip().split()[0]

    with st.chat_message("user"):
        st.markdown(prompt)
    messages.append({"role": "user", "content": prompt})
    
    # ตั้งหัวข้อห้องแชทอัตโนมัติ
    if len(messages) == 1:
        current_chat["title"] = prompt[:20] + "..."

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.write("...")
        
        history = "\n".join([f"{m['role']}: {m['content']}" for m in messages[-10:]])
        user_info = f"คนคุยชื่อคุณ {st.session_state.user_name}" if st.session_state.user_name else "ยังไม่ทราบชื่อ"
        
        instruction = f"คุณคือ 'น้องนนทรี' AI รุ่นพี่ มก. ศรีราชา {user_info}. ตอบอย่างสุภาพ"
        full_prompt = f"{instruction}\n\nประวัติห้องนี้:\n{history}\n\nคำถาม: {prompt}"
        
        try:
            response = model.generate_content(full_prompt)
            res_text = response.text
            placeholder.markdown(res_text)
            messages.append({"role": "assistant", "content": res_text})
            st.rerun() 
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")
