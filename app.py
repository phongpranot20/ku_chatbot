import streamlit as st
import google.generativeai as genai
import os
import base64
import re

# --- 1. ตั้งค่าหน้าจอ (Page Config) ---
st.set_page_config(page_title="AI KUSRC", page_icon="🦖", layout="wide")

# --- 2. ระบบจัดการภาษา (Language Management) ---
if "lang" not in st.session_state:
    st.session_state.lang = "TH"

def toggle_language():
    st.session_state.lang = "EN" if st.session_state.lang == "TH" else "TH"

# พจนานุกรมแปลภาษา
translation = {
    "TH": {
        "univ_name": "มหาวิทยาลัย<br>เกษตรศาสตร์",
        "new_chat": "➕ แชทใหม่",
        "chat_hist": "💬 ประวัติการแชท",
        "exam_table": "📅 ค้นหาตารางสอบ",
        "gpa_calc": "🧮 คำนวณเกรด (GPA)",
        "forms": "📄 ลิงก์แบบฟอร์มต่างๆ",
        "input_placeholder": "พิมพ์ถามพี่นนทรีได้เลย...",
        "welcome": "สวัสดีคุณ",
        "topic": "หัวข้อ",
        "loading": "*(พี่กำลังหาคำตอบให้...)*",
        "btn_find": "ค้นหา",
        "btn_open": "เปิดระบบ",
        "btn_download": "โหลด",
        "ai_instruction": "คุณคือ 'น้องนนทรี' AI รุ่นพี่ มก.ศรช. ตอบเป็นภาษาไทยอย่างเป็นกันเอง"
    },
    "EN": {
        "univ_name": "Kasetsart<br>University",
        "new_chat": "➕ New Chat",
        "chat_hist": "💬 Chat History",
        "exam_table": "📅 Exam Schedule",
        "gpa_calc": "🧮 GPA Calculator",
        "forms": "📄 Document Forms",
        "input_placeholder": "Ask Nontri anything...",
        "welcome": "Hello",
        "topic": "Topic",
        "loading": "*(Processing answer...)*",
        "btn_find": "Search",
        "btn_open": "Open",
        "btn_download": "Get",
        "ai_instruction": "You are 'Nontri', a friendly senior student AI at KU Sriracha. Respond in English."
    }
}
curr = translation[st.session_state.lang]

# --- 3. ฟังก์ชันเสริม (Image & Room Info) ---
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

def get_room_info(room_code):
    code = re.sub(r'\D', '', str(room_code))
    if len(code) == 5:
        building = code[:2]; floor = code[2]; room = code[3:]
        return f"อ๋อ ห้องนี้อยู่ **ตึก {building} ชั้น {floor} ห้อง {room}** ครับ" if st.session_state.lang == "TH" else f"This room is in **Building {building}, Floor {floor}, Room {room}**."
    return None

# --- 4. CSS (จัดเต็ม UI เขียว-ขาว) ---
st.markdown(f"""
<style>
    .stApp {{ background-color: #FFFFFF; color: black; }}
    [data-testid="stSidebar"] {{ background-color: #006861 !important; }}
    [data-testid="stSidebarContent"] {{ padding-top: 0rem !important; }}
    
    .custom-header {{
        display: flex; flex-direction: column; align-items: center; text-align: center;
        padding: 5px 5px 15px 5px; margin-top: -35px; border-bottom: 2px solid rgba(255,255,255,0.2);
    }}
    .header-logo-img {{ width: 90px; height: auto; margin-bottom: 10px; }}
    .univ-name {{ color: white !important; font-size: 20px; font-weight: bold; line-height: 1.2; }}
    .sidebar-title {{ color: white !important; font-size: 14px; font-weight: bold; margin-top: 15px; }}
    
    /* ปุ่มใน Sidebar */
    div.stButton > button {{
        width: 100% !important; border-radius: 12px !important;
        background-color: transparent !important; color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        padding: 10px 15px !important; text-align: left !important; margin-bottom: 10px !important;
    }}
    div.stButton > button:hover {{ background-color: rgba(255, 255, 255, 0.2) !important; border-color: #FFD700 !important; }}

    /* Expander สีขาว */
    div[data-testid="stExpander"] {{ background-color: #FFFFFF !important; border-radius: 12px !important; margin-bottom: 10px !important; border: none !important; }}
    .form-row {{ display: flex; justify-content: space-between; align-items: center; padding: 10px 8px; border-bottom: 1px solid #f0f0f0; }}
    .form-label {{ color: #333 !important; font-size: 13px; font-weight: 500; }}
    .btn-action {{ background-color: #006861; color: white !important; padding: 4px 12px; border-radius: 6px; text-decoration: none; font-size: 11px; font-weight: bold; }}
</style>
""", unsafe_allow_html=True)

# --- 5. API & Model Setup ---
api_key = st.secrets.get("GEMINI_API_KEY")
if api_key: genai.configure(api_key=api_key)

@st.cache_resource
def load_model():
    try: return genai.GenerativeModel('gemini-1.5-flash')
    except: return None
model = load_model()

# --- 6. State Management ---
if "all_chats" not in st.session_state: st.session_state.all_chats = {} 
if "messages" not in st.session_state: st.session_state.messages = []
if "current_chat_id" not in st.session_state: st.session_state.current_chat_id = None
if "global_user_nickname" not in st.session_state: st.session_state.global_user_nickname = "Student"

# --- 7. Sidebar (Menu & Language Switch) ---
with st.sidebar:
    # ปุ่มสลับภาษาแบบเท่ๆ
    st.button(f"🌐 Language: {st.session_state.lang}", on_click=toggle_language)

    if os.path.exists("logo_ku.png"):
        img_data = get_image_base64("logo_ku.png")
        st.markdown(f'<div class="custom-header"><img src="data:image/png;base64,{img_data}" class="header-logo-img"><div class="univ-name">{curr["univ_name"]}</div></div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button(curr["new_chat"], key="new_chat_btn"):
        st.session_state.messages = []
        st.session_state.current_chat_id = None
        st.rerun()
    
    if st.session_state.all_chats:
        st.markdown(f'<p class="sidebar-title">{curr["chat_hist"]}</p>', unsafe_allow_html=True)
        for chat_id in list(st.session_state.all_chats.keys()):
            if st.button(f"📄 {chat_id[:18]}...", key=f"hist_{chat_id}"):
                st.session_state.current_chat_id = chat_id
                st.session_state.messages = st.session_state.all_chats[chat_id]
                st.rerun()

    st.markdown("---")
    # ส่วนของ Expander เมนูต่างๆ
    with st.expander(curr["exam_table"], expanded=False):
        st.markdown(f'<div class="form-row"><div class="form-label">KU SRC Exam</div><a href="https://reg2.src.ku.ac.th/table_test/" target="_blank" class="btn-action">{curr["btn_find"]}</a></div>', unsafe_allow_html=True)
    
    with st.expander(curr["gpa_calc"], expanded=False):
        st.markdown(f'<div class="form-row"><div class="form-label">GPAX Sim</div><a href="https://fna.csc.ku.ac.th/grade/" target="_blank" class="btn-action">{curr["btn_open"]}</a></div>', unsafe_allow_html=True)
    
    with st.expander(curr["forms"], expanded=False):
        forms = [("ใบคำร้องทั่วไป", "https://registrar.ku.ac.th/wp-content/uploads/2023/11/General-Request.pdf"), ("ใบลาออก", "https://registrar.ku.ac.th/wp-content/uploads/2023/11/Resignation-Form.pdf")]
        for name, link in forms:
            st.markdown(f'<div class="form-row"><div class="form-label">{name}</div><a href="{link}" target="_blank" class="btn-action">{curr["btn_download"]}</a></div>', unsafe_allow_html=True)

# --- 8. Main Chat Interface ---
st.markdown(f"## 🦖 AI TEST")
current_title = st.session_state.current_chat_id if st.session_state.current_chat_id else ( "แชทใหม่" if st.session_state.lang == "TH" else "New Chat")
st.caption(f"👤 {curr['welcome']} {st.session_state.global_user_nickname} | {curr['topic']}: {current_title}")

for message in st.session_state.messages:
    avatar = "🧑‍🎓" if message["role"] == "user" else "🦖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

if prompt := st.chat_input(curr["input_placeholder"]):
    if st.session_state.current_chat_id is None: st.session_state.current_chat_id = prompt[:20]
    
    st.chat_message("user", avatar="🧑‍🎓").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="🦖"):
        room_info = get_room_info(prompt)
        if room_info:
            full_response = room_info
            st.markdown(full_response)
        else:
            placeholder = st.empty()
            placeholder.markdown(curr["loading"])
            try:
                knowledge_base = ""
                if os.path.exists("ku_data.txt"):
                    with open("ku_data.txt", "r", encoding="utf-8") as f: knowledge_base = f.read()
                
                full_context = f"{curr['ai_instruction']}\nข้อมูลมหาลัย:\n{knowledge_base}\n\nคำถาม: {prompt}"
                response = model.generate_content(full_context)
                full_response = response.text
                placeholder.markdown(full_response)
            except Exception as e:
                full_response = f"Error: {e}"
                st.error(full_response)
        
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.session_state.all_chats[st.session_state.current_chat_id] = st.session_state.messages
