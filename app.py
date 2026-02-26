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

# --- 3. CSS ปรับแต่ง UI (แยกคุม 2 กล่องให้ยาวเท่าอันล่าง) ---
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

    /* --- ส่วนที่ 1: ปรับแยกกล่อง "แชทใหม่" --- */
    div.stButton > button[key*="new_chat"] {
        width: 170% !important;
        border-radius: 12px !important;
        background-color: rgba(255, 255, 255, 0.15) !important; /* ปรับความใส/สี แยกตรงนี้ */
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
        padding: 12px 15px !important;
        font-weight: bold !important;
        margin-bottom: 15px !important;
    }

    /* --- ส่วนที่ 2: ปรับแยกกล่อง "ประวัติการแชท" --- */
    div.stButton > button[key*="hist_"] {
        width: 160% !important;
        border-radius: 12px !important;
        background-color: rgba(255, 255, 255, 0.1) !important; /* ปรับความใส/สี แยกตรงนี้ */
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        padding: 10px 15px !important;
        text-align: left !important;
        margin-bottom: 8px !important;
    }
    
    .stButton > button:hover {
        background-color: rgba(255, 255, 255, 0.25) !important;
        border-color: #FFD700 !important;
    }

    /* กล่องข้อมูลสีขาว (Expander) ด้านล่าง */
    div[data-testid="stExpander"] { 
        background-color: #FFFFFF !important; 
        border-radius: 12px !important; 
        margin-bottom: 10px !important; 
    }
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

# --- 5. จัดการ State ความจำ ---
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {"แชทเริ่มต้น": []}
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = "แชทเริ่มต้น"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "global_user_nickname" not in st.session_state:
    st.session_state.global_user_nickname = "นิสิต"

def switch_chat(chat_id):
    st.session_state.all_chats[st.session_state.current_chat_id] = st.session_state.messages
    st.session_state.current_chat_id = chat_id
    st.session_state.messages = st.session_state.all_chats.get(chat_id, [])

# --- 6. Sidebar ---
with st.sidebar:
    if os.path.exists("logo_ku.png"):
        img_data = get_image_base64("logo_ku.png")
        st.markdown(f'<div class="custom-header"><img src="data:image/png;base64,{img_data}" class="header-logo-img"><div class="univ-name">มหาวิทยาลัย<br>เกษตรศาสตร์</div></div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ปุ่มแชทใหม่
    if st.button("➕ แชทใหม่", key="new_chat_btn"):
        new_id = f"แชท {len(st.session_state.all_chats) + 1}"
        st.session_state.all_chats[new_id] = []
        switch_chat(new_id)
        st.rerun()
    
    st.markdown('<p style="color:white; font-size:14px; font-weight:bold;">💬 ประวัติการแชท</p>', unsafe_allow_html=True)
    # รายการประวัติแชท
    for chat_id in list(st.session_state.all_chats.keys()):
        if st.button(f"📄 {chat_id[:18]}...", key=f"hist_{chat_id}"):
            switch_chat(chat_id)
            st.rerun()

    st.markdown("---")
    with st.expander("📅 ค้นหาตารางสอบ", expanded=False):
        st.markdown('<div class="white-card-content"><div class="form-row"><div class="form-label">เช็กวัน-เวลาสอบ</div><a href="https://reg2.src.ku.ac.th/table_test/" target="_blank" class="btn-action">ค้นหา</a></div></div>', unsafe_allow_html=True)
    with st.expander("🧮 คำนวณเกรด (GPA)", expanded=False):
        st.markdown('<div class="white-card-content"><div class="form-row"><div class="form-label">ระบบจำลองการตัดเกรด</div><a href="https://fna.csc.ku.ac.th/grade/" target="_blank" class="btn-action">เปิดระบบ</a></div></div>', unsafe_allow_html=True)
    
    # คืนค่าใบเอกสารครบ 7 รายการ
    with st.expander("📄 ลิงก์แบบฟอร์มต่างๆ", expanded=False):
        forms = [
            ("ใบขอลงทะเบียนเรียน ", "https://registrar.ku.ac.th/wp-content/uploads/2024/11/Request-for-Registration.pdf"),
            ("ใบคำร้องทั่วไป ", "https://registrar.ku.ac.th/wp-content/uploads/2023/11/General-Request.pdf"),
            ("ใบผ่อนผันค่าเทอม ", "https://registrar.ku.ac.th/wp-content/uploads/2024/11/Postpone-tuition-and-fee-payments.pdf"),
            ("ใบลาพักการศึกษา ", "https://registrar.ku.ac.th/wp-content/uploads/2023/11/Request-for-Leave-of-Absence-Request.pdf"),
            ("ใบลาออก ", "https://registrar.ku.ac.th/wp-content/uploads/2023/11/Resignation-Form.pdf"),
            ("ใบลงทะเบียนเรียน (KU1) ", "https://registrar.ku.ac.th/wp-content/uploads/2023/11/KU1-Registration-Form.pdf"),
            ("ใบเพิ่ม-ถอน (KU3) ", "https://registrar.ku.ac.th/wp-content/uploads/2023/11/KU3-Add-Drop-Form.pdf")
        ]
        st.markdown('<div class="white-card-content">', unsafe_allow_html=True)
        for name, link in forms:
            st.markdown(f'<div class="form-row"><div class="form-label">{name}</div><a href="{link}" target="_blank" class="btn-action">โหลด</a></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# --- 7. หน้า Chat หลัก ---
st.markdown(f"## 🦖 AI TEST")
st.caption(f"👤 สวัสดีคุณ {st.session_state.global_user_nickname} | หัวข้อ: {st.session_state.current_chat_id}")

for message in st.session_state.messages:
    avatar = "🧑‍🎓" if message["role"] == "user" else "🦖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

if prompt := st.chat_input("พิมพ์ถามพี่นนทรีได้เลย..."):
    if (st.session_state.current_chat_id.startswith("แชท") or st.session_state.current_chat_id == "แชทเริ่มต้น") and not st.session_state.messages:
        new_title = prompt[:20]
        st.session_state.all_chats[new_title] = []
        if st.session_state.current_chat_id in st.session_state.all_chats:
            del st.session_state.all_chats[st.session_state.current_chat_id]
        st.session_state.current_chat_id = new_title

    # จำชื่อข้าม Session
    name_match = re.search(r"(?:ผม|หนู|เรา|พี่|ชื่อ)\s*ชื่อว่า?\s*(\w+)", prompt)
    if name_match: st.session_state.global_user_nickname = name_match.group(1)

    st.chat_message("user", avatar="🧑‍🎓").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="🦖"):
        room_info = get_room_info(prompt)
        if room_info:
            st.markdown(room_info)
            st.session_state.messages.append({"role": "assistant", "content": room_info})
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
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                st.session_state.all_chats[st.session_state.current_chat_id] = st.session_state.messages
                st.rerun()
            except Exception as e:
                if "429" in str(e):
                    st.warning("⚠️ **ขออภัยครับ!** (Quota เต็ม) รอกดส่งใหม่ในอีก 1 นาทีนะ")
                else: st.error(f"Error: {e}")
