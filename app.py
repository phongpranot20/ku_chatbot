import streamlit as st
import google.generativeai as genai
import uuid # ใช้สำหรับสร้าง ID ให้แต่ละห้องแชท

st.set_page_config(page_title="AI TEST", layout="wide")

# --- 1. SETUP API & MODEL ---
api_key = st.secrets.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 2. INITIALIZE SESSION STATE ---
# เก็บทุกห้องแชทไว้ใน chat_sessions
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {} # {id: {"title": title, "messages": []}}

# เก็บ ID ของห้องแชทที่กำลังเปิดอยู่
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

# --- 3. SIDEBAR (NEW CHAT & HISTORY LIST) ---
with st.sidebar:
    st.title("AI TEST")
    
    # ปุ่มแชทใหม่ (New Chat) แบบ Gemini
    if st.button("+ แชทใหม่", use_container_width=True):
        new_id = str(uuid.uuid4())
        st.session_state.chat_sessions[new_id] = {"title": "แชทใหม่", "messages": []}
        st.session_state.current_chat_id = new_id
        st.rerun()

    st.write("---")
    st.subheader("ประวัติการแชท")
    
    # แสดงรายการแชทเก่าๆ ให้กดเลือกได้
    for chat_id, chat_data in reversed(list(st.session_state.chat_sessions.items())):
        if st.button(chat_data["title"], key=chat_id, use_container_width=True):
            st.session_state.current_chat_id = chat_id
            st.rerun()

# --- 4. MAIN CHAT AREA ---

# ถ้ายังไม่มีการเริ่มแชทเลย ให้สร้างแชทแรกอัตโนมัติ
if st.session_state.current_chat_id is None:
    first_id = str(uuid.uuid4())
    st.session_state.chat_sessions[first_id] = {"title": "แชทใหม่", "messages": []}
    st.session_state.current_chat_id = first_id

current_id = st.session_state.current_chat_id
current_messages = st.session_state.chat_sessions[current_id]["messages"]

# แสดงข้อความในแชทที่เลือกอยู่
for message in current_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 5. CHAT INPUT LOGIC ---
if prompt := st.chat_input("พิมพ์ข้อความที่นี่..."):
    # แสดงข้อความฝั่ง User
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # บันทึกข้อความลงใน session
    current_messages.append({"role": "user", "content": prompt})
    
    # ถ้าเป็นข้อความแรกของแชท ให้ใช้ข้อความนั้นเป็นชื่อ Title ใน Sidebar
    if len(current_messages) == 1:
        st.session_state.chat_sessions[current_id]["title"] = prompt[:20] + "..."

    # เรียก AI
    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.write("...")
        
        # ดึงประวัติในห้องแชทนั้นๆ ส่งให้ AI
        history = "\n".join([f"{m['role']}: {m['content']}" for m in current_messages[-10:]])
        full_prompt = f"คุณคือน้องนนทรี AI รุ่นพี่ มก. ศรีราชา\n\nประวัติ:\n{history}\n\nคำถาม: {prompt}"
        
        try:
            response = model.generate_content(full_prompt)
            placeholder.markdown(response.text)
            current_messages.append({"role": "assistant", "content": response.text})
            st.rerun() # เพื่ออัปเดตชื่อ Title ใน Sidebar ทันที
        except Exception as e:
            st.error(f"Error: {e}")
