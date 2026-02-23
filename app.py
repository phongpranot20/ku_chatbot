import streamlit as st
import google.generativeai as genai
import os
import uuid
import json

# --- 1. CSS ปรับปรุง: New Chat เขียวอ่อน + ขีดน้ำเงินค้างที่ประวัติ ---
st.set_page_config(page_title="AI TEST", layout="wide")

st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #f8f9fa !important; }
    
    /* สไตล์ปุ่มประวัติทรงเหลี่ยม */
    div.stButton > button {
        width: 100% !important;
        border: none !important;
        background-color: transparent !important;
        padding: 15px 10px !important;
        text-align: left !important;
        border-radius: 0px !important;
        border-bottom: 1px solid #eee !important;
        color: #444 !important;
        display: block !important;
    }

    /* บังคับขีดน้ำเงินด้านซ้ายสำหรับห้องที่เลือก (Active) */
    div[data-testid="stSidebar"] button[kind="primary"] {
        background-color: #e9ecef !important;
        border-left: 6px solid #007bff !important; /* ขีดน้ำเงินตามรูปที่ฮอนอยากได้ */
        color: #111 !important;
        font-weight: 600 !important;
    }

    /* ปุ่ม New Chat: สีเขียวอ่อนที่สุด */
    .stSidebar [data-testid="stVerticalBlock"] > div:nth-child(2) button {
        background-color: #e8f5e9 !important; /* เขียวอ่อนที่สุด */
        color: #2e7d32 !important;
        border-radius: 10px !important;
        text-align: center !important;
        border: 1px solid #c8e6c9 !important;
        margin-bottom: 20px !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("AI TEST")

# --- 2. ระบบ Database (JSON) ---
DB_FILE = "chat_history_db.json"

def save_to_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_from_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# --- 3. Setup Model ---
api_key = st.secrets.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 4. Initialization ---
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = load_from_db()

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

if st.session_state.current_chat_id is None:
    if st.session_state.chat_sessions:
        st.session_state.current_chat_id = list(st.session_state.chat_sessions.keys())[-1]
    else:
        new_id = str(uuid.uuid4())
        st.session_state.chat_sessions[new_id] = {"title": "New Chat", "messages": []}
        st.session_state.current_chat_id = new_id

current_id = st.session_state.current_chat_id
current_chat = st.session_state.chat_sessions[current_id]

# --- 5. Sidebar ---
with st.sidebar:
    st.header("เมนูควบคุม")
    # เปลี่ยนชื่อเป็น New Chat และสีเขียวอ่อน
    if st.button("New Chat", use_container_width=True):
        if len(current_chat["messages"]) > 0:
            new_id = str(uuid.uuid4())
            st.session_state.chat_sessions[new_id] = {"title": "New Chat", "messages": []}
            st.session_state.current_chat_id = new_id
            save_to_db(st.session_state.chat_sessions)
            st.rerun()
    
    st.write("---")
    st.subheader("ประวัติการคุย")
    
    for chat_id, chat_data in reversed(list(st.session_state.chat_sessions.items())):
        if len(chat_data["messages"]) > 0:
            is_active = (chat_id == current_id)
            
            # บังคับใช้ type="primary" เพื่อให้ CSS ขีดซ้ายทำงาน
            if st.button(
                chat_data["title"], 
                key=chat_id, 
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                st.session_state.current_chat_id = chat_id
                st.rerun()

# --- 6. แสดงผลแชท ---
for m in current_chat["messages"]:
    avatar = "🧑‍🎓" if m["role"] == "user" else "🦖"
    with st.chat_message(m["role"], avatar=avatar):
        st.markdown(m["content"])

if prompt := st.chat_input("พิมพ์ข้อความที่นี่..."):
    with st.chat_message("user", avatar="🧑‍🎓"):
        st.markdown(prompt)
    current_chat["messages"].append({"role": "user", "content": prompt})
    
    if len(current_chat["messages"]) == 1:
        current_chat["title"] = prompt[:25]
    
    save_to_db(st.session_state.chat_sessions)

    with st.chat_message("assistant", avatar="🦖"):
        placeholder = st.empty()
        history = "\n".join([f"{m['role']}: {m['content']}" for m in current_chat["messages"][-10:]])
        try:
            response = model.generate_content(f"คุณคือพี่นนทรี AI มก.ศรีราชา\n\nประวัติ:\n{history}\n\nคำถาม: {prompt}")
            placeholder.markdown(response.text)
            current_chat["messages"].append({"role": "assistant", "content": response.text})
            save_to_db(st.session_state.chat_sessions)
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")
