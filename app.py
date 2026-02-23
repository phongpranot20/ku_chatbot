import streamlit as st
import google.generativeai as genai
import os
import uuid

# --- 1. CSS ปรับแต่งแบบเจาะจง (ลบสีส้ม/แดง ออกให้เกลี้ยง) ---
st.set_page_config(page_title="AI TEST", layout="wide")

st.markdown("""
<style>
    /* ล้างค่าสีพื้นฐานของปุ่มใน Sidebar ทุกชนิด */
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

    /* บังคับลบสีส้ม/แดง จากปุ่มที่เลือกอยู่ (Active) และใส่ขีดเขียวซ้ายมือ */
    div[data-testid="stSidebar"] button[kind="primary"] {
        background-color: rgba(0, 89, 76, 0.05) !important; /* เขียวจางๆ มากๆ */
        border-left: 6px solid #00594C !important; /* ขีดสีเขียวนนทรี */
        color: #00594C !important;
        font-weight: bold !important;
        border-radius: 0px !important;
    }

    /* เมื่อเมาส์ไปวาง ให้สีเปลี่ยนนิดเดียวพอ */
    div[data-testid="stSidebar"] button:hover {
        background-color: rgba(0, 0, 0, 0.02) !important;
        color: #00594C !important;
    }

    /* สไตล์ปุ่มเริ่มแชทใหม่ให้ดูแยกสัดส่วนชัดเจน */
    div[data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:nth-child(2) button {
        background-color: #f0f2f6 !important;
        border-radius: 10px !important;
        text-align: center !important;
        padding-left: 0px !important;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

st.title("AI TEST")

# --- 2. การตั้งค่าโมเดล ---
api_key = st.secrets.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)

@st.cache_resource
def get_model():
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        selected = next((m for m in models if "flash" in m), models[0])
        return genai.GenerativeModel(selected)
    except:
        return None

model = get_model()

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

# --- 4. Sidebar (เช็ค Syntax ปิดวงเล็บให้แล้ว) ---
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
            is_active = (chat_id == st.session_state.current_chat_id)
            # ใช้ type="primary" เพื่อให้ CSS จับไปทำขีดสีเขียว
            if st.button(chat_data["title"], key=chat_id, use_container_width=True, 
                         type="primary" if is_active else "secondary"):
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
        current_chat["title"] = prompt[:20] + "..."

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
