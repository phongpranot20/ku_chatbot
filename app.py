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

# พจนานุกรมสำหรับข้อความบน UI
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
        "ai_identity": "คุณคือรุ่นพี่ มก.ศรช. ใจดี ตอบเป็นภาษาไทยเป็นหลัก"
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
        "ai_identity": "You are a friendly KU Sriracha senior. Please respond in English."
    }
}
curr = translation[st.session_state.lang]

# --- 3. ฟังก์ชันจัดการข้อมูล ---
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

def get_room_info(room_code):
    code = re.sub(r'\D', '', str(room_code))
    if len(code) == 5:
        building = code[:2]; floor = code[2]; room = code[3:]
        return f"อ๋อ ห้องนี้อยู่ **ตึก {building} ชั้น {floor} ห้อง {room}** ครับน้อง" if st.session_state.lang == "TH" else f"This room is in **Building {building}, Floor {floor}, Room {room}**."
    elif len(code) == 4:
        building = code[0]; floor = code[1]; room = code[2:]
        return f"ห้องนี้คือ **ตึก {building} ชั้น {floor} ห้อง {room}** ครับผม" if st.session_state.lang == "TH" else f"It is **Building {building}, Floor {floor}, Room {room}**."
    return None

# --- 4. CSS (Updated UI Modern/Minimal) ---
# --- 4. CSS (Updated UI Modern/Glassmorphism) ---
st.markdown("""
<style>
/* เปลี่ยนจาก Kanit เป็น Sarabun หรือ Prompt ที่ดูชัดเจนกว่า */
@import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Sarabun', sans-serif !important;
}

/* เพิ่มความคมชัดของข้อความทั่วไป */
.stMarkdown, .stText, p {
    color: #2D3436 !important; /* เปลี่ยนเป็นสีเทาเข้มเกือบดำเพื่อให้สบายตาแต่คมชัด */
    font-weight: 400;
}

/* เพิ่มความชัดเจนให้ข้อความใน Chat */
.stChatMessageContent {
    font-size: 1.1rem !important;
    line-height: 1.7 !important;
    font-weight: 400 !important;
}
   /* ปรับแต่ง Sidebar ให้มีมิติชัดเจน */
[data-testid="stSidebar"] { 
    background: rgba(248, 249, 250, 0.8) !important; /* ปรับสีให้ทึบขึ้นเล็กน้อย */
    backdrop-filter: blur(15px);
    border-right: 1px solid rgba(0,0,0,0.1); /* เส้นขอบที่ชัดขึ้น */
    box-shadow: 5px 0 15px rgba(0,0,0,0.05); /* เพิ่มเงาด้านขวาเพื่อให้ลอยเด่นขึ้นมา */
    z-index: 100;
}

/* เพิ่มส่วนแบ่ง Visual ให้ชัดเจนขึ้นด้วยเงาที่ขอบ */
[data-testid="stSidebar"] > div:first-child {
    padding-right: 10px;
}
    
/* แก้ไข Header ให้รองรับ Flexbox เพื่อวางโลโก้และชื่อบรรทัดเดียวกัน */
.custom-header { 
    display: flex;
    align-items: center; /* จัดให้อยู่กึ่งกลางในแนวตั้ง */
    gap: 15px; /* ระยะห่างระหว่างรูปกับตัวอักษร */
    padding: 10px !important;
    background: rgba(255, 255, 255, 0.9); /* เปลี่ยนพื้นหลังเป็นขาวแบบโปร่งแสง */
    border-radius: 15px !important;
    box-shadow: 0 4px 10px rgba(0,0,0,0.1); /* เพิ่มเงาให้มีมิติ */
}

/* ปรับขนาดโลโก้ให้ใหญ่ขึ้นเล็กน้อย */
.header-logo-img {
    max-width: 60px !important; /* ปรับจาก 80px เป็น 60px เพื่อให้ไม่เบียดชื่อจนเกินไป */
    height: auto !important;
}

/* ชื่อมหาลัยสีดำ มีมิติ (Text Shadow) */
.univ-name { 
    color: #333333 !important; /* สีดำเข้ม */
    font-size: 1.1rem !important; 
    font-weight: 700;
    line-height: 1.2;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.1); /* เพิ่มเงาให้ตัวอักษรมีมิติ */
    margin-top: 0 !important;
}
    /* ปุ่มแบบ Modern */
    div.stButton > button { 
        border-radius: 50px !important; 
        border: none !important;
        background: white !important;
        color: #004D40 !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    div.stButton > button:hover { 
        background: #004D40 !important; 
        color: white !important;
        transform: scale(1.02);
    }

    /* Chat Messages Glassmorphism */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.8) !important;
        backdrop-filter: blur(5px);
        border-radius: 20px !important;
        border: 1px solid rgba(255,255,255,0.3) !important;
    }

    /* Expander สวยงาม */
    div[data-testid="stExpander"] { 
        background: white !important;
        border-radius: 15px !important; 
        border: none !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
    }

    /* ปุ่ม Action สีสดใส */
    .btn-action { 
        background: #FFD700; 
        color: #004D40 !important; 
        padding: 5px 15px; 
        border-radius: 20px; 
        text-decoration: none; 
        font-size: 0.8rem;
        font-weight: 700;
        transition: 0.3s;
    }
    
    .btn-action:hover { background: #FFC107; transform: translateY(-2px); }

    /* การ์ตูนน่ารักๆ (Decorations) */
    .stApp::before {
        content: "🦖";
        position: fixed;
        bottom: 20px;
        right: 20px;
        font-size: 80px;
        opacity: 0.1;
        z-index: 0;
        pointer-events: none;
    }
    /* เพิ่มในส่วนสไตล์ของคุณ */
.main {
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}

/* ทำให้ช่อง Chat กว้างและดูสะอาดขึ้น */
.stChatMessageContent {
    font-size: 1.05rem;
    line-height: 1.6;
}

/* เพิ่มความโค้งมนให้ container ของแชท */
[data-testid="stChatMessage"] {
    border-radius: 15px !important;
    padding: 15px !important;
    margin-bottom: 10px !important;
    box-shadow: 0 4px 10px rgba(0,0,0,0.03);
}
@keyframes wave-dance {
        0%, 100% { transform: rotate(0deg); }
        50% { transform: rotate(25deg); }
    }
    .dino-head {
        display: inline-block;
        animation: wave-dance 2s infinite ease-in-out;
        margin-right: 10px;
    }

</style>
""", unsafe_allow_html=True)
# --- 5. จัดการ API (คงโมเดลเดิมไว้) ---
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

# --- 6. จัดการ State ---
if "all_chats" not in st.session_state: st.session_state.all_chats = {} 
if "messages" not in st.session_state: st.session_state.messages = []
if "current_chat_id" not in st.session_state: st.session_state.current_chat_id = None
if "global_user_nickname" not in st.session_state: st.session_state.global_user_nickname = "นิสิต"

# --- 7. Sidebar (เพิ่มปุ่มสลับภาษา) ---
with st.sidebar:
    # ปุ่มสลับภาษาบนสุด
    col_lang, _ = st.columns([1, 2])
    with col_lang:
        st.button(f"🌐 {st.session_state.lang}", on_click=toggle_language)

    # เช็คเงื่อนไขให้ตรงระดับย่อหน้า
    if os.path.exists("logo_ku.png"):
        img_data = get_image_base64("logo_ku.png")
        st.markdown(f'<div class="custom-header"><img src="data:image/png;base64,{img_data}" class="header-logo-img"><div class="univ-name">{curr["univ_name"]}</div></div>', unsafe_allow_html=True)
    
    st.markdown("", unsafe_allow_html=True)
    
    # บรรทัดถัดไปต้องเคาะย่อหน้าให้ตรงกับบรรทัด if หรือคำสั่งด้านบน
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
    st.markdown(f'<p class="sidebar-title">Quick Links</p>', unsafe_allow_html=True)
    with st.expander(curr["exam_table"], expanded=False):
        st.markdown(f'<div class="form-row"><div class="form-label">KU Exam</div><a href="https://reg2.src.ku.ac.th/table_test/" target="_blank" class="btn-action">{curr["btn_find"]}</a></div>', unsafe_allow_html=True)
    with st.expander(curr["gpa_calc"], expanded=False):
        st.markdown(f'<div class="form-row"><div class="form-label">GPAX</div><a href="https://fna.csc.ku.ac.th/grade/" target="_blank" class="btn-action">{curr["btn_open"]}</a></div>', unsafe_allow_html=True)
    with st.expander(curr["forms"], expanded=False):
        forms = [("ใบคำร้องทั่วไป", "https://registrar.ku.ac.th/wp-content/uploads/2023/11/General-Request.pdf")]
        for name, link in forms:
            st.markdown(f'<div class="form-row"><div class="form-label">{name}</div><a href="{link}" target="_blank" class="btn-action">{curr["btn_download"]}</a></div>', unsafe_allow_html=True)

# แก้ไขบรรทัดที่แสดงหัวข้อ AI KUSRC
current_title = st.session_state.current_chat_id if st.session_state.current_chat_id else ( "แชทใหม่" if st.session_state.lang == "TH" else "New Chat")

st.markdown(f"<h2 style='color: #004D40;'><span class='dino-head'>🦖</span> AI KUSRC</h2>", unsafe_allow_html=True)
st.caption(f"👤 {curr['welcome']} {st.session_state.global_user_nickname} | {curr['topic']}: {current_title}")

# แสดงข้อความ
for message in st.session_state.messages:
    avatar = "🧑‍🎓" if message["role"] == "user" else "🦖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# ส่วนรับ Input
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
                
                history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[-6:-1]]
                chat_session = model.start_chat(history=history)
                
                full_context = f"{curr['ai_identity']} คุยกับน้องชื่อ {st.session_state.global_user_nickname} ข้อมูลมหาลัย:\n{knowledge_base}\n\nคำถาม: {prompt}"
                
                response = chat_session.send_message(full_context, stream=True)
                full_response = ""
                for chunk in response:
                    full_response += chunk.text
                    placeholder.markdown(full_response + "▌")
                placeholder.markdown(full_response)
            except Exception as e:
                full_response = f"Error: {e}"
                st.error(full_response)
        
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.session_state.all_chats[st.session_state.current_chat_id] = st.session_state.messages
        st.rerun()
