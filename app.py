import streamlit as st
import google.generativeai as genai
import os
import uuid

st.set_page_config(page_title="KU Sriracha Bot", page_icon="🐢", layout="wide")

# --- CSS คงเดิม ---
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF !important; color: black !important; }
    [data-testid="stSidebar"] { background-color: #f2f9f6 !important; }
    h1, h2, h3, p, span, div { color: #00594C; }
    [data-testid="stChatMessage"] { background-color: #f0f2f6; border-radius: 10px; }
    .stMarkdown p { color: #333333 !important; }
</style>
""", unsafe_allow_html=True)

# --- ตั้งค่า API ---
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("❌ ไม่พบ API Key")
    st.stop()

genai.configure(api_key=api_key)

@st.cache_resource
def load_model():
    try:
        return genai.GenerativeModel(model_name="gemini-1.5-flash")
    except: return None

model = load_model()

# --- ส่วนจัดการ Session State (ปรับปรุงใหม่) ---
if "chat_history_dict" not in st.session_state:
    st.session_state.chat_history_dict = {}

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

# ฟังก์ชันสร้างแชทใหม่
def start_new_chat():
    new_id = str(uuid.uuid4())
    st.session_state.chat_history_dict[new_id] = {"title": "แชทใหม่", "messages": []}
    st.session_state.current_chat_id = new_id
    return new_id

# ตรวจสอบว่าถ้ายังไม่มีแชทเลย หรือ ID ปัจจุบันไม่มีในระบบ ให้สร้างใหม่
if not st.session_state.chat_history_dict or st.session_state.current_chat_id not in st.session_state.chat_history_dict:
    start_new_chat()

# --- Sidebar ---
with st.sidebar:
    st.title("KU Sriracha Bot")
    
    if st.button("➕ แชทใหม่", use_container_width=True):
        start_new_chat()
        st.rerun()
    
    st.divider()
    st.subheader("แชทล่าสุด")
    
    # แสดงรายการแชท
    for chat_id in reversed(list(st.session_state.chat_history_dict.keys())):
        chat_data = st.session_state.chat_history_dict[chat_id]
        # ไฮไลท์แชทที่เลือกอยู่
        is_current = (chat_id == st.session_state.current_chat_id)
        if st.button(chat_data["title"], key=chat_id, use_container_width=True, type="primary" if is_current else "secondary"):
            st.session_state.current_chat_id = chat_id
            st.rerun()

# --- หน้าจอหลัก (ดึงข้อมูลแชทปัจจุบันมาแสดง) ---
# ใช้ .get() เพื่อป้องกัน KeyError
current_chat = st.session_state.chat_history_dict.get(st.session_state.current_chat_id)

if current_chat:
    st.title(current_chat["title"])

    # โหลด Knowledge Base
    if os.path.exists("ku_data.txt"):
        with open("ku_data.txt", "r", encoding="utf-8") as f:
            knowledge_base = f.read()
    else:
        knowledge_base = "ข้อมูล มก. ศรีราชา"

    # แสดงข้อความ
    for message in current_chat["messages"]:
        with st.chat_message(message["role"], avatar="🧑‍🎓" if message["role"] == "user" else "🦖"):
            st.markdown(message["content"])

    # รับ Input
    if prompt := st.chat_input("พิมพ์คำถามที่นี่..."):
        # เพิ่มข้อความฝั่ง User
        current_chat["messages"].append({"role": "user", "content": prompt})
        
        # เปลี่ยนชื่อแชทถ้าเป็นคำถามแรก
        if current_chat["title"] == "แชทใหม่":
            current_chat["title"] = prompt[:25] + "..." if len(prompt) > 25 else prompt
            st.rerun() # Rerun เพื่อให้ชื่อใน Sidebar เปลี่ยนทันที

        with st.chat_message("user", avatar="🧑‍🎓"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="🦖"):
            placeholder = st.empty()
            instruction = "คุณคือ 'น้องนนทรี' ตอบคำถามตามข้อมูลที่ให้มาอย่างสุภาพ"
            history_text = "\n".join([f"{m['role']}: {m['content']}" for m in current_chat["messages"][-5:]])
            full_prompt = f"{instruction}\n\nข้อมูล: {knowledge_base}\n\nประวัติ:\n{history_text}\n\nคำถาม: {prompt}"
            
            try:
                response = model.generate_content(full_prompt, stream=True)
                full_response = ""
                for chunk in response:
                    full_response += chunk.text
                    placeholder.markdown(full_response + "▌")
                
                placeholder.markdown(full_response)
                current_chat["messages"].append({"role": "assistant", "content": full_response})
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาด: {str(e)}")
