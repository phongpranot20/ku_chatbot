import streamlit as st
import google.generativeai as genai
import os
import uuid # ใช้สำหรับสร้าง ID ให้แต่ละแชท

st.set_page_config(page_title="KU Sriracha Bot", page_icon="🐢", layout="wide")

# --- CSS เดิมของคุณ ---
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF !important; color: black !important; }
    [data-testid="stSidebar"] { background-color: #f2f9f6 !important; }
    h1, h2, h3, p, span, div { color: #00594C; }
    [data-testid="stChatMessage"] { background-color: #f0f2f6; border-radius: 10px; }
    .stMarkdown p { color: #333333 !important; }
</style>
""", unsafe_allow_html=True)

# --- ตั้งค่า Gemini API ---
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("❌ ไม่พบ API Key")
    st.stop()

genai.configure(api_key=api_key)

@st.cache_resource
def load_model():
    try:
        return genai.GenerativeModel(model_name="gemini-1.5-flash")
    except:
        return None

model = load_model()

# --- ส่วนจัดการ Session State สำหรับ Multi-Chat ---
# 1. เก็บรายการแชททั้งหมด
if "chat_history_dict" not in st.session_state:
    st.session_state.chat_history_dict = {} # {chat_id: {"title": str, "messages": list}}

# 2. เก็บ ID ของแชทที่กำลังเปิดอยู่
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

# ฟังก์ชันสำหรับเริ่มแชทใหม่
def start_new_chat():
    new_id = str(uuid.uuid4())
    st.session_state.chat_history_dict[new_id] = {"title": "แชทใหม่", "messages": []}
    st.session_state.current_chat_id = new_id

# ถ้าเปิดมาครั้งแรกแล้วยังไม่มีแชท ให้สร้างแ chat ใหม่ทันที
if st.session_state.current_chat_id is None:
    start_new_chat()

# --- Sidebar: รายการแชทเก่า ---
with st.sidebar:
    st.title("KU Sriracha Bot")
    
    # ปุ่มแชทใหม่
    if st.button("➕ แชทใหม่", use_container_width=True):
        start_new_chat()
        st.rerun()
    
    st.divider()
    st.subheader("แชทล่าสุด")
    
    # แสดงรายการแชทที่มีอยู่
    for chat_id in reversed(list(st.session_state.chat_history_dict.keys())):
        title = st.session_state.chat_history_dict[chat_id]["title"]
        # ปุ่มเลือกแชท
        if st.button(title, key=chat_id, use_container_width=True):
            st.session_state.current_chat_id = chat_id
            st.rerun()

# --- หน้าจอแชทหลัก ---
current_chat = st.session_state.chat_history_dict[st.session_state.current_chat_id]

st.title(current_chat["title"])

# โหลด Knowledge Base
if os.path.exists("ku_data.txt"):
    with open("ku_data.txt", "r", encoding="utf-8") as f:
        knowledge_base = f.read()
else:
    knowledge_base = "ข้อมูล มก. ศรีราชา"

# แสดงข้อความในแชทปัจจุบัน
for message in current_chat["messages"]:
    with st.chat_message(message["role"], avatar="🧑‍🎓" if message["role"] == "user" else "🦖"):
        st.markdown(message["content"])

# ส่วนรับ Input
if prompt := st.chat_input("พิมพ์คำถามที่นี่..."):
    # เพิ่มข้อความ user
    current_chat["messages"].append({"role": "user", "content": prompt})
    
    # ถ้าเป็นประโยคแรก ให้ตั้งชื่อแชทตามคำถามแรก
    if current_chat["title"] == "แชทใหม่":
        current_chat["title"] = prompt[:20] + "..." if len(prompt) > 20 else prompt
        st.rerun()

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
            st.error(f"Error: {str(e)}")
