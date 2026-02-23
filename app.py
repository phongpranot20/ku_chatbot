import streamlit as st
import google.generativeai as genai
import os
import uuid

# --- 1. การตั้งค่าหน้าจอและ CSS (ล้างสีแดง/ส้มออก และทำขีดเขียวด้านซ้าย) ---
st.set_page_config(page_title="AI TEST", layout="wide")

st.markdown("""
<style>
    /* ล้างสีพื้นหลังและขอบของปุ่มทุกชนิดใน Sidebar */
    div[data-testid="stSidebar"] button {
        border: none !important;
        background-color: transparent !important;
        color: #555 !important;
        text-align: left !important;
        padding-left: 15px !important;
        width: 100% !important;
        display: block !important;
        box-shadow: none !important;
    }

    /* ปุ่มที่กำลังใช้งาน (Active) - บังคับให้พื้นหลังใสและมีขีดเขียวซ้ายมือ */
    div[data-testid="stSidebar"] button[kind="primary"] {
        background-color: rgba(0, 89, 76, 0.05) !important; /* พื้นหลังเขียวจางๆ มากๆ */
        border-left: 6px solid #00594C !important; /* ขีดสีเขียวนนทรีด้านซ้าย */
        color: #00594C !important;
        font-weight: bold !important;
        border-radius: 0px !important;
    }
    
    /* แก้ไขสีตัวหนังสือตอนเอาเมาส์ไปวาง (Hover) */
    div[data-testid="stSidebar"] button:hover {
        color: #00594C !important;
        background-color: rgba(0, 89, 76, 0.02) !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("AI TEST")

# --- 2. การตั้งค่า API (ใช้ข้อมูลจากคุณ ฮอน) ---
api_key = st.secrets.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 3. ระบบจัดการ Session ---
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None
if "user_name" not in st.session_state:
    st.session_state.user_name = None

if st.session_state.current_chat_id is None:
    first_id = str(uuid.uuid4())
    st.session_state.chat_sessions[first_id] = {"title": "แชทใหม่", "messages": []}
    st.session_state.current_chat_id = first_id

current_chat = st.session_state.chat_sessions[st.session_state.current_chat_id]
messages = current_chat["messages"]

# --- 4. Sidebar (ประวัติการคุย) ---
with st.sidebar:
    st.header("เมนูควบคุม")
    
    # ปุ่มเริ่มแชทใหม่
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
            # ใช้ type="primary" เพื่อให้ CSS จับไปทำขีดสีเขียว
            is_active = (chat_id == st.session_state.current_chat_id)
            if st.button(
                chat_data["title"], 
                key=chat_id, 
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                st.session_state.current_chat_id = chat_id
                st.rerun()

# --- 5. แสดงผลแชท (🧑‍🎓 บัณฑิต / 🦖 ไดโนเสาร์) ---
for m in messages:
    avatar = "🧑‍🎓" if m["role"] == "user" else "🦖"
    with st.chat_message(m["role"], avatar=avatar):
        st.markdown(m["content"])

if prompt := st.chat_input("พิมพ์ข้อความที่นี่..."):
    with st.chat_message("user", avatar="🧑‍🎓"):
        st.markdown(prompt)
    messages.append({"role": "user", "content": prompt})
    
    if len(messages) == 1:
        current_chat["title"] = prompt[:20] + "..."

    with st.chat_message("assistant", avatar="🦖"):
        placeholder = st.empty()
        placeholder.write("...")
        
        history = "\n".join([f"{m['role']}: {m['content']}" for m in messages[-10:]])
        full_p = f"คุณคือ 'น้องนนทรี' AI รุ่นพี่ มก. ศรีราชา\n\nประวัติ:\n{history}\n\nคำถาม: {prompt}"
        
        try:
            response = model.generate_content(full_p)
            placeholder.markdown(response.text)
            messages.append({"role": "assistant", "content": response.text})
            st.rerun() 
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")
