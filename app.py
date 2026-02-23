import streamlit as st
import google.generativeai as genai
import os
import uuid

# --- 1. การตั้งค่าหน้าจอและ CSS (ปรับปรุงตามรีเควสฮอน) ---
st.set_page_config(page_title="AI TEST", layout="wide")

st.markdown("""
<style>
    /* ล้างค่าสีส้มของ Streamlit ออกให้หมด */
    div[data-testid="stSidebar"] button {
        border: none !important;
        background-color: transparent !important; /* ทำให้พื้นหลังใส ไม่ส้ม */
        text-align: left !important;
        padding-left: 20px !important;
        color: #555 !important;
        width: 100%;
        display: block;
    }

    /* ปุ่มที่เลือกอยู่ (Active) - ให้มีแค่ขีดเขียวด้านซ้ายนิดเดียว */
    div[data-testid="stSidebar"] button[kind="primary"] {
        border-left: 5px solid #00594C !important; /* ขีดสีเขียวนนทรี */
        background-color: rgba(0, 89, 76, 0.05) !important; /* พื้นหลังเขียวจางๆ */
        color: #00594C !important;
        font-weight: 600 !important;
        border-radius: 0px !important;
    }
    
    /* ปุ่มเริ่มแชทใหม่ (ทำให้ดูเป็นปุ่มแยก) */
    div[data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:nth-child(2) button {
        background-color: #f0f2f6 !important;
        border-radius: 10px !important;
        text-align: center !important;
        padding-left: 0px !important;
        margin-bottom: 15px;
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

# --- 3. ระบบจัดการ Session ---
if "user_name" not in st.session_state:
    st.session_state.user_name = None

if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

if st.session_state.current_chat_id is None:
    first_id = str(uuid.uuid4())
    st.session_state.chat_sessions[first_id] = {"title": "แชทใหม่", "messages": []}
    st.session_state.current_chat_id = first_id

current_chat_id = st.session_state.current_chat_id
current_chat = st.session_state.chat_sessions[current_chat_id]
messages = current_chat["messages"]

# --- 4. Sidebar ---
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
            is_active = (chat_id == current_chat_id)
            if st.button(
                chat_data["title"], 
                key=chat_id, 
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                st.session_state.current_chat_id = chat_id
                st.rerun()

# --- 5. การแสดงผล (เปลี่ยน Avatar ตามสั่ง) ---
for message in messages:
    # ผู้ใช้เป็น บัณฑิต (🧑‍🎓), AI เป็น ไดโนเสาร์ (🦖)
    avatar = "🧑‍🎓" if message["role"] == "user" else "🦖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

if prompt := st.chat_input("พิมพ์ข้อความที่นี่..."):
    if any(k in prompt for k in ["ชื่อ", "ผมชื่อ", "เราชื่อ"]):
        parts = prompt.split("ชื่อ")
        if len(parts) > 1:
            st.session_state.user_name = parts[1].strip().split()[0]

    with st.chat_message("user", avatar="🧑‍🎓"):
        st.markdown(prompt)
    messages.append({"role": "user", "content": prompt})
    
    if len(messages) == 1:
        current_chat["title"] = prompt[:20] + "..."

    with st.chat_message("assistant", avatar="🦖"):
        placeholder = st.empty()
        placeholder.write("...")
        
        history = "\n".join([f"{m['role']}: {m['content']}" for m in messages[-10:]])
        user_info = f"คนคุยชื่อคุณ {st.session_state.user_name}" if st.session_state.user_name else "ยังไม่รู้ชื่อ"
        
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
