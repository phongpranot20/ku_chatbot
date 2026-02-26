import streamlit as st
import google.generativeai as genai
import os
import base64
import re

# --- 1. ตั้งค่าหน้าจอ (Page Config) ---
st.set_page_config(page_title="AI KUSRC", page_icon="🦖", layout="wide")

# --- 2. ฟังก์ชันจัดการข้อมูล ---
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

def get_room_info(room_code):
    # ฟังก์ชันอ่านเลขห้องแบบธรรมชาติ
    code = re.sub(r'\D', '', str(room_code))
    if len(code) == 5:
        building = code[:2]; floor = code[2]; room = code[3:]
        return f"อ๋อ ห้องนี้อยู่ **ตึก {building} ชั้น {floor} ห้อง {room}** ครับน้อง"
    elif len(code) == 4:
        building = code[0]; floor = code[1]; room = code[2:]
        return f"ห้องนี้คือ **ตึก {building} ชั้น {floor} ห้อง {room}** ครับผม"
    return None

# --- 3. CSS ปรับแต่ง UI (ธีมมหาลัย พร้อมระบบ Sidebar History) ---
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
    .sidebar-title { color: #FFFFFF !important; font-size: 1.1rem; font-weight: bold; margin: 15px 0px 10px 0px; text-align: center; }
    
    /* ปุ่ม Sidebar */
    .stButton > button {
        width: 100%; border-radius: 10px; background-color: rgba(255,255,255,0.1);
        color: white; border: 1px solid rgba(255,255,255,0.3); transition: 0.3s;
    }
    .stButton > button:hover {
        background-color: rgba(255,255,255,0.2); border: 1px solid #FFD700; color: #FFD700;
    }

    /* Expander และตารางข้อมูล */
    div[data-testid="stExpander"] { background-color: #FFFFFF !important; border-radius: 12px !important; margin-bottom: 10px; border: none !important; }
    div[data-testid="stExpander"] p { color: #000000 !important; font-weight: bold !important; }
    .white-card-content { background-color: #FFFFFF; border-radius: 0px 0px 12px 12px; }
    .form-row { display: flex; justify-content: space-between; align-items: center; padding: 10px 8px; border-bottom: 1px solid #f0f0f0; }
    .btn-action { background-color: #006861; color: white !important; padding: 4px 10px; border-radius: 6px; text-decoration: none; font-size: 10px; font-weight: bold; white-space: nowrap; }
</style>
""", unsafe_allow_html=True)

# --- 4. จัดการ API และ Model ---
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

# --- 5. จัดการ State และความจำข้ามแชท ---
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {"แชทเริ่มต้น": []}
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = "แชทเริ่มต้น"
if "messages" not in st.session_state:
    st.session_state.messages = []
# ระบบจดจำชื่อทุกคนข้าม Session
if "global_user_nickname" not in st.session_state:
    st.session_state.global_user_nickname = "Hon" # ตั้งค่าเริ่มต้นเป็น Hon

def switch_chat(chat_id):
    # บันทึกแชทปัจจุบันก่อนสลับหัวข้อ
    st.session_state.all_chats[st.session_state.current_chat_id] = st.session_state.messages
    st.session_state.current_chat_id = chat_id
    st.session_state.messages = st.session_state.all_chats.get(chat_id, [])

# --- 6. Sidebar (Dashboard & History) ---
with st.sidebar:
    if os.path.exists("logo_ku.png"):
        img_data = get_image_base64("logo_ku.png")
        st.markdown(f'<div class="custom-header"><img src="data:image/png;base64,{img_data}" class="header-logo-img"><div class="univ-name">มหาวิทยาลัย<br>เกษตรศาสตร์</div></div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ปุ่มแชทใหม่
    if st.button("➕ แชทใหม่"):
        new_id = f"แชทใหม่ {len(st.session_state.all_chats) + 1}"
        st.session_state.all_chats[new_id] = []
        switch_chat(new_id)
        st.rerun()
    
    st.markdown('<p class="sidebar-title">💬 ประวัติการแชท</p>', unsafe_allow_html=True)
    # แสดงรายการแชทที่สามารถกดสลับไปมาได้
    for chat_id in list(st.session_state.all_chats.keys()):
        if st.button(f"📄 {chat_id[:18]}...", key=f"btn_{chat_id}"):
            switch_chat(chat_id)
            st.rerun()

    st.markdown("---")
    # แดชบอร์ดคำนวณและค้นหา
    with st.expander("📅 ค้นหาตารางสอบ", expanded=False):
        st.markdown('<div class="white-card-content"><div class="form-row"><div class="form-label">เช็กวัน-เวลาสอบ</div><a href="https://reg2.src.ku.ac.th/table_test/" target="_blank" class="btn-action">ค้นหา</a></div></div>', unsafe_allow_html=True)
    with st.expander("🧮 คำนวณเกรด (GPA)", expanded=False):
        st.markdown('<div class="white-card-content"><div class="form-row"><div class="form-label">ระบบจำลองการตัดเกรด</div><a href="https://fna.csc.ku.ac.th/grade/" target="_blank" class="btn-action">เปิดระบบ</a></div></div>', unsafe_allow_html=True)
    
    # แบบฟอร์มครบ 7 รายการ (ไม่ลบแน่นอน)
    with st.expander("📄 ลิงก์แบบฟอร์มต่างๆ", expanded=False):
        forms = [
            ("ขอลงทะเบียนเรียน (Reg-2)", "https://registrar.ku.ac.th/wp-content/uploads/2024/11/Request-for-Registration.pdf"),
            ("คำร้องทั่วไป (Reg-1)", "https://registrar.ku.ac.th/wp-content/uploads/2023/11/General-Request.pdf"),
            ("ผ่อนผันค่าเทอม (Reg-3)", "https://registrar.ku.ac.th/wp-content/uploads/2024/11/Postpone-tuition-and-fee-payments.pdf"),
            ("ใบลาพักการศึกษา (Reg-10)", "https://registrar.ku.ac.th/wp-content/uploads/2023/11/Request-for-Leave-of-Absence-Request.pdf"),
            ("ใบลาออก (Reg-16)", "https://registrar.ku.ac.th/wp-content/uploads/2023/11/Resignation-Form.pdf"),
            ("ลงทะเบียนเรียน (KU1)", "https://registrar.ku.ac.th/wp-content/uploads/2023/11/KU1-Registration-Form.pdf"),
            ("เพิ่ม-ถอน (KU3)", "https://registrar.ku.ac.th/wp-content/uploads/2023/11/KU3-Add-Drop-Form.pdf")
        ]
        st.markdown('<div class="white-card-content">', unsafe_allow_html=True)
        for name, link in forms:
            st.markdown(f'<div class="form-row"><div class="form-label">{name}</div><a href="{link}" target="_blank" class="btn-action">โหลด</a></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# --- 7. หน้า Chat หลัก ---
st.markdown(f"## 🦖 AI TEST")
st.caption(f"👤 สวัสดีครับคุณ {st.session_state.global_user_nickname} | หัวข้อแชท: {st.session_state.current_chat_id}")

for message in st.session_state.messages:
    avatar = "🧑‍🎓" if message["role"] == "user" else "🦖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

if prompt := st.chat_input("พิมพ์ถามพี่นนทรีได้เลย..."):
    # เปลี่ยนชื่อหัวข้อแชทอัตโนมัติ (แก้ไขบั๊ก KeyError)
    if st.session_state.current_chat_id.startswith("แชทใหม่") and not st.session_state.messages:
        new_title = prompt[:20]
        st.session_state.all_chats[new_title] = []
        if st.session_state.current_chat_id in st.session_state.all_chats:
            del st.session_state.all_chats[st.session_state.current_chat_id]
        st.session_state.current_chat_id = new_title

    # ตรวจจับชื่อผู้ใช้ (จดจำทุกคนที่มาใช้งาน)
    name_match = re.search(r"(?:ผม|หนู|เรา|พี่|ชื่อ)\s*ชื่อว่า?\s*(\w+)", prompt)
    if name_match:
        st.session_state.global_user_nickname = name_match.group(1)

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
                
                # ดึงประวัติการคุยเพื่อให้ AI จำบริบทได้
                history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[-6:-1]]
                chat_session = model.start_chat(history=history)
                
                # ใช้ Global Nickname เพื่อให้จำได้ข้ามแชทใหม่
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
            except Exception as e: st.error(f"Error: {e}")
