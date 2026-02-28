import streamlit as st
import google.generativeai as genai
import os
import base64
import re

# --- 1. ตั้งค่าหน้าจอ (Page Config) ---
st.set_page_config(page_title="AI KUSRC", page_icon="🦖", layout="wide")

# --- 2. ระบบจัดการภาษา (Language Settings) ---
if "lang" not in st.session_state:
    st.session_state.lang = "TH"

def toggle_language():
    st.session_state.lang = "EN" if st.session_state.lang == "TH" else "TH"

# พจนานุกรมแปลภาษาสำหรับ UI
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
        "quota_err": "⚠️ **ขออภัยครับ!** (Quota เต็ม)",
        "ai_intro": "คุณคือ 'น้องนนทรี' AI รุ่นพี่ มก.ศรช. ตอบเป็นภาษาไทยอย่างเป็นกันเอง"
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
        "loading": "*(Nontri is thinking...)*",
        "btn_find": "Search",
        "btn_open": "Open",
        "btn_download": "Get",
        "quota_err": "⚠️ **Sorry!** (Quota Full)",
        "ai_intro": "You are 'Nontri', a friendly senior student AI at KU Sriracha. Please respond in English."
    }
}
curr = translation[st.session_state.lang]

# --- 3. ฟังก์ชันจัดการข้อมูล (Helper Functions) ---
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

def get_room_info(room_code):
    code = re.sub(r'\D', '', str(room_code))
    if len(code) == 5:
        building = code[:2]; floor = code[2]; room = code[3:]
        return f"อ๋อ ห้องนี้อยู่ **ตึก {building} ชั้น {floor} ห้อง {room}** ครับน้อง" if st.session_state.lang == "TH" else f"This room is located in **Building {building}, Floor {floor}, Room {room}**."
    elif len(code) == 4:
        building = code[0]; floor = code[1]; room = code[2:]
        return f"ห้องนี้คือ **ตึก {building} ชั้น {floor} ห้อง {room}** ครับผม" if st.session_state.lang == "TH" else f"It is **Building {building}, Floor {floor}, Room {room}**."
    return None

# --- 4. CSS (UI เดิมที่สวยงาม) ---
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
    
    div.stButton > button {{
        width: 100% !important; border-radius: 12px !important;
        background-color: transparent !important; color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        padding: 10px 15px !important; text-align: left !important; margin-bottom: 10px !important;
    }}
    div.stButton > button:hover {{ background-color: rgba(255, 255, 255, 0.2) !important; border-color: #FFD700 !important; }}

    div[data-testid="stExpander"] {{ background-color: #FFFFFF !important; border-radius: 12px !important; margin-bottom: 10px !important; border: none !important; }}
    .form-row {{ display: flex; justify-content: space-between; align-items: center; padding: 10px 8px; border-bottom: 1px solid #f0f0f0; }}
    .form-label {{ color: #333 !important; font-size: 13px; font-weight: 500; }}
    .btn-action {{ background-color: #006861; color: white !important; padding: 4px 12px; border-radius: 6px; text-decoration: none; font-size: 11px; font-weight: bold; }}
</style>
""", unsafe_allow_html=True)

# --- 5. จัดการ API & List Model (Original Logic) ---
api_key = st.secrets.get("GEMINI_API_KEY")
if api_key: genai.configure(api_key=api_key)

@st.cache_resource
def load_model():
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                # ใช้ Google Search เป็น tool ตามโค้ดเดิม
                return genai.GenerativeModel(model_name=m.name, tools=[{"google_search": {}}])
    except Exception as e:
        st.error(f"Error loading models: {e}")
    return None

model = load_model()

# --- 6. จัดการ State ---
if "all_chats" not in st.session_state: st.session_state.all_chats = {} 
if "messages" not in st.session_state: st.session_state.messages = []
if "current_chat_id" not in st.session_state: st.session_state.current_chat_id = None
if "global_user_nickname" not in st.session_state: st.session_state.global_user_nickname = "นิสิต" if st.session_state.lang == "TH" else "Student"

# --- 7. Sidebar (เมนูเดิม + สลับภาษา) ---
with st.sidebar:
    st.button(f"🌐 {st.session_state.lang} / Change Language", on_click=toggle_language)

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
    with st.expander(curr["exam_table"], expanded=False):
        st.markdown(f'<div class="form-row"><div class="form-label">{curr["exam_table"]}</div><a href="https://reg2.src.ku.ac.th/table_test/" target="_blank" class="btn-action">{curr["btn_find"]}</a></div>', unsafe_allow_html=True)
    
    with st.expander(curr["gpa_calc"], expanded=False):
        st.markdown(f'<div class="form-row"><div class="form-label">GPAX</div><a href="https://fna.csc.ku.ac.th/grade/" target="_blank" class="btn-action">{curr["btn_open"]}</a></div>', unsafe_allow_html=True)
    
    with st.expander(curr["forms"], expanded=False):
        st.markdown(f'<div class="form-row"><div class="form-label">General Request</div><a href="https://registrar.ku.ac.th/wp-content/uploads/2023/11/General-Request.pdf" target="_blank" class="btn-action">{curr["btn_download"]}</a></div>', unsafe_allow_html=True)

# --- 8. หน้า Chat หลัก ---
st.markdown(f"## 🦖 AI TEST")
current_title = st.session_state.current_chat_id if st.session_state.current_chat_id else ( "แชทใหม่" if st.session_state.lang == "TH" else "New Chat")
st.caption(f"👤 {curr['welcome']} {st.session_state.global_user_nickname} | {curr['topic']}: {current_title}")

for message in st.session_state.messages:
    avatar = "🧑‍🎓" if message["role"] == "user" else "🦖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

if prompt := st.chat_input(curr["input_placeholder"]):
    if st.session_state.current_chat_id is None: st.session_state.current_chat_id = prompt[:20]

    # ตรวจจับชื่อเล่น (Nickname logic เดิม)
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
            placeholder.markdown(curr["loading"])
            try:
                knowledge_base = ""
                if os.path.exists("ku_data.txt"):
                    with open("ku_data.txt", "r", encoding="utf-8") as f: knowledge_base = f.read()
                
                # Chat logic เดิม
                history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[-6:-1]]
                chat_session = model.start_chat(history=history)
                
                full_context = f"{curr['ai_intro']}\nข้อมูลมหาลัย:\n{knowledge_base}\n\nคำถาม: {prompt}"
                response = chat_session.send_message(full_context, stream=True)
                
                full_response = ""
                for chunk in response:
                    full_response += chunk.text
                    placeholder.markdown(full_response + "▌")
                placeholder.markdown(full_response)
            except Exception as e:
                if "429" in str(e):
                    full_response = curr["quota_err"]
                    st.warning(full_response)
                else:
                    full_response = f"Error: {e}"
                    st.error(full_response)
        
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.session_state.all_chats[st.session_state.current_chat_id] = st.session_state.messages
        st.rerun()
