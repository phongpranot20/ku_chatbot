import streamlit as st
import google.generativeai as genai
import os
import base64
import re

# --- 1. ตั้งค่าหน้าจอ ---
st.set_page_config(page_title="AI KUSRC", page_icon="🦖", layout="wide")

# --- 2. ฟังก์ชันจัดการข้อมูล ---
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

def get_room_info(room_code):
    code = re.sub(r'\D', '', str(room_code))
    if len(code) == 5:
        building = code[:2]; floor = code[2]; room = code[3:]
        return f"อ๋อ ห้องนี้อยู่ **ตึก {building} ชั้น {floor} ห้อง {room}** ครับน้อง"
    elif len(code) == 4:
        building = code[0]; floor = code[1]; room = code[2:]
        return f"ห้องนี้คือ **ตึก {building} ชั้น {floor} ห้อง {room}** ครับผม"
    return None

# --- 3. CSS (ใสถาวร ยาวเท่ากล่องขาว) ---
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; color: black; }
    [data-testid="stSidebar"] { background-color: #006861 !important; }
    [data-testid="stSidebarContent"] { padding-top: 0rem !important; }
    
    .custom-header {
        display: flex; flex-direction: column; align-items: center; text-align: center;
        padding: 5px 5px 15px 5px; margin-top: -35px; border-bottom: 2px solid rgba(255,255,255,0.2);
    }
    .header-logo-img { width: 90px; height: auto; margin-bottom: 10px; }
    .univ-name { color: white !important; font-size: 22px; font-weight: bold; line-height: 1.2; }
    .sidebar-title { color: white !important; font-size: 14px; font-weight: bold; margin-bottom: 5px; }
    
    div.stButton > button {
        width: 225% !important;
        border-radius: 12px !important;
        background-color: transparent !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        padding: 10px 15px !important;
        text-align: left !important;
        margin-bottom: 10px !important;
        display: flex !important;
        justify-content: flex-start !important;
    }
    div.stButton > button:hover {
        background-color: rgba(255, 255, 255, 0.2) !important;
        border-color: #FFD700 !important;
    }

    div[data-testid="stExpander"] { background-color: #FFFFFF !important; border-radius: 12px !important; margin-bottom: 10px !important; border: none !important; }
    div[data-testid="stExpander"] p { color: #000000 !important; font-weight: bold !important; }
    .white-card-content { background-color: #FFFFFF; border-radius: 0px 0px 12px 12px; }
    .form-row { display: flex; justify-content: space-between; align-items: center; padding: 10px 8px; border-bottom: 1px solid #f0f0f0; }
    .btn-action { background-color: #006861; color: white !important; padding: 4px 10px; border-radius: 6px; text-decoration: none; font-size: 10px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 4. จัดการ API ---
api_key = st.secrets.get("GEMINI_API_KEY")
if api_key: genai.configure(api_key=api_key)

@st.cache_resource
def load_model():
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        selected = next((m for m in available_models if "1.5-flash" in m), available_models[0])
        return genai.GenerativeModel(model_name=selected)
    except: return None
model = load_model()

# --- 5. จัดการ State ---
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {} 
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None
if "global_user_nickname" not in st.session_state:
    st.session_state.global_user_nickname = "นิสิต"

# --- 6. Sidebar ---
with st.sidebar:
    if os.path.exists("logo_ku.png"):
        img_data = get_image_base64("logo_ku.png")
        st.markdown(f'<div class="custom-header"><img src="data:image/png;base64,{img_data}" class="header-logo-img"><div class="univ-name">มหาวิทยาลัย<br>เกษตรศาสตร์</div></div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ปุ่มแชทใหม่: ล้างค่าทันที
    if st.button("➕ แชทใหม่", key="new_chat_btn"):
        st.session_state.messages = []
        st.session_state.current_chat_id = None
        st.rerun()
    
    # แสดงประวัติแชทเฉพาะที่มีข้อมูลจริง
    if st.session_state.all_chats:
        st.markdown('<p class="sidebar-title">💬 ประวัติการแชท</p>', unsafe_allow_html=True)
        for chat_id in list(st.session_state.all_chats.keys()):
            if st.button(f"📄 {chat_id[:18]}...", key=f"hist_{chat_id}"):
                st.session_state.current_chat_id = chat_id
                st.session_state.messages = st.session_state.all_chats[chat_id]
                st.rerun()

    st.markdown("---")
    with st.expander("📅 ค้นหาตารางสอบ", expanded=False):
        st.markdown('<div class="white-card-content"><div class="form-row"><div class="form-label">เช็กวัน-เวลาสอบ</div><a href="https://reg2.src.ku.ac.th/table_test/" target="_blank" class="btn-action">ค้นหา</a></div></div>', unsafe_allow_html=True)
    with st.expander("🧮 คำนวณเกรด (GPA)", expanded=False):
        st.markdown('<div class="white-card-content"><div class="form-row"><div class="form-label">ระบบจำลองการตัดเกรด</div><a href="https://fna.csc.ku.ac.th/grade/" target="_blank" class="btn-action">เปิดระบบ</a></div></div>', unsafe_allow_html=True)
    with st.expander("📄 ลิงก์แบบฟอร์มต่างๆ", expanded=False):
        forms = [("ใบขอลงทะเบียนเรียน ", "https://registrar.ku.ac.th/wp-content/uploads/2024/11/Request-for-Registration.pdf"),
            ("ใบคำร้องทั่วไป ", "https://registrar.ku.ac.th/wp-content/uploads/2023/11/General-Request.pdf"),
            ("ใบผ่อนผันค่าเทอม ", "https://registrar.ku.ac.th/wp-content/uploads/2024/11/Postpone-tuition-and-fee-payments.pdf"),
            ("ใบลาพักการศึกษา ", "https://registrar.ku.ac.th/wp-content/uploads/2023/11/Request-for-Leave-of-Absence-Request.pdf"),
            ("ใบลาออก ", "https://registrar.ku.ac.th/wp-content/uploads/2023/11/Resignation-Form.pdf"),
            ("ใบลงทะเบียนเรียน ", "https://registrar.ku.ac.th/wp-content/uploads/2023/11/KU1-Registration-Form.pdf"),
            ("ใบเพิ่ม-ถอน ", "https://registrar.ku.ac.th/wp-content/uploads/2023/11/KU3-Add-Drop-Form.pdf")]
        for name, link in forms:
            st.markdown(f'<div class="form-row"><div class="form-label">{name}</div><a href="{link}" target="_blank" class="btn-action">โหลด</a></div>', unsafe_allow_html=True)

# --- 7. หน้า Chat หลัก ---
st.markdown(f"## 🦖 AI TEST")
current_title = st.session_state.current_chat_id if st.session_state.current_chat_id else "แชทใหม่"
st.caption(f"👤 สวัสดีคุณ {st.session_state.global_user_nickname} | หัวข้อ: {current_title}")

for message in st.session_state.messages:
    avatar = "🧑‍🎓" if message["role"] == "user" else "🦖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

if prompt := st.chat_input("พิมพ์ถามพี่นนทรีได้เลย..."):
    # ถ้าเป็นแชทใหม่ ให้ตั้งชื่อตามข้อความแรก
    if st.session_state.current_chat_id is None:
        st.session_state.current_chat_id = prompt[:20]

    # จำชื่อผู้ใช้
    name_match = re.search(r"(?:ผม|หนู|เรา|พี่|ชื่อ)\s*ชื่อว่า?\s*(\w+)", prompt)
    if name_match: st.session_state.global_user_nickname = name_match.group(1)

    st.chat_message("user", avatar="🧑‍🎓").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

   with st.chat_message("assistant", avatar="🦖"):
        room_info = get_room_info(prompt)
        if room_info:
            full_response = room_info
            st.markdown(full_response)
        else:
            placeholder = st.empty()
            placeholder.markdown("*(พี่กำลังหาคำตอบให้...)*")
            try:
                knowledge_base = ""
                if os.path.exists("ku_data.txt"):
                    with open("ku_data.txt", "r", encoding="utf-8") as f: knowledge_base = f.read()
                
                history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[-6:-1]]
                chat_session = model.start_chat(history=history)
                full_context = f"คุณคือรุ่นพี่ มก.ศรช. ใจดี คุยกับน้องชื่อ {st.session_state.global_user_nickname} ข้อมูลมหาลัย:\n{knowledge_base}\n\nคำถาม: {prompt}"
                response = chat_session.send_message(full_context, stream=True)
                full_response = ""
                for chunk in response:
                    full_response += chunk.text
                    placeholder.markdown(full_response + "▌")
                placeholder.markdown(full_response)
            except Exception as e:
                full_response = f"เกิดข้อผิดพลาด: {e}"
                st.error(full_response)
        
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        # บันทึกลงประวัติ
        st.session_state.all_chats[st.session_state.current_chat_id] = st.session_state.messages
        st.rerun()
      
     
