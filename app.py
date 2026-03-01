import streamlit as st
import google.generativeai as genai
import os
import base64
import re

# --- 1. ตั้งค่าหน้าจอ (คงเดิม) ---
st.set_page_config(page_title="AI KUSRC", page_icon="🦖", layout="wide")

# --- 2. ระบบจัดการภาษา (คงเดิมของคุณ 100%) ---
if "lang" not in st.session_state:
    st.session_state.lang = "TH"

def toggle_language():
    st.session_state.lang = "EN" if st.session_state.lang == "TH" else "TH"

translation = {
    "TH": {
        "univ_name": "มหาวิทยาลัย<br>เกษตรศาสตร์",
        "new_chat": "➕ เริ่มแชทใหม่",
        "chat_hist": "💬 ประวัติการแชท",
        "exam_table": "📅 ค้นหาตารางสอบ",
        "gpa_calc": "🧮 คำนวณเกรด (GPA)",
        "forms": "📄 ลิงก์แบบฟอร์มต่างๆ",
        "input_placeholder": "พิมพ์ถามพี่นนทรีได้เลย...",
        "welcome": "สวัสดีครับ มีอะไรให้พี่ช่วยไหม?",
        "loading": "*(กำลังหาคำตอบให้...)*",
        "btn_find": "ค้นหา", "btn_open": "เปิดระบบ", "btn_download": "โหลด",
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
        "welcome": "How can I help you today?",
        "loading": "*(Thinking...)*",
        "ai_identity": "You are a friendly KU Sriracha senior. Please respond in English."
    }
}
curr = translation[st.session_state.lang]

# --- 3. ฟังก์ชันจัดการข้อมูล (คงเดิม) ---
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

def get_room_info(room_code):
    code = re.sub(r'\D', '', str(room_code))
    if len(code) >= 4:
        return f"📍 ข้อมูลสถานที่: **ตึก {code[:2]} ชั้น {code[2]} ห้อง {code[3:]}**"
    return None

# --- 4. CSS แก้ไขใหม่ (ลบไอคอนแดง/ส้ม และปรับ UI ให้คลีน) ---
st.markdown(f"""
<style>
    /* 1. ลบไอคอนสีแดง (User) และสีส้ม (Assistant) ออกแบบถาวร */
    [data-testid="chatAvatarIcon-user"], 
    [data-testid="chatAvatarIcon-assistant"],
    div[data-testid="stChatMessage"] figure {{
        display: none !important;
    }}
    
    /* 2. จัดระเบียบช่องว่างหลังลบไอคอน */
    div[data-testid="stChatMessage"] {{
        padding-left: 0px !important;
        margin-left: 0px !important;
        max-width: 850px !important;
        margin: 0 auto !important;
    }}

    /* 3. ปรับแต่งกล่องข้อความ AI ให้ดู Pro แบบ Gemini (พื้นหลังเทาอ่อน) */
    [data-testid="stChatMessageAssistant"] {{
        background-color: #f0f4f9 !important;
        border-radius: 20px !important;
        padding: 1.5rem !important;
        border: none !important;
    }}

    /* 4. จัดการ Sidebar และ Logo ให้ขนาดคงที่ */
    .sidebar-header {{ text-align: center; padding: 20px 0; }}
    .logo-img {{ width: 100px !important; height: auto; }}
    .univ-name {{ color: #006861 !important; font-size: 18px; font-weight: bold; }}

    /* 5. ปรับแต่งช่อง Input ด้านล่าง */
    div[data-testid="stChatInput"] {{
        border: 1px solid #e0e0e0 !important;
        border-radius: 30px !important;
        background-color: #f8f9fa !important;
    }}
</style>
""", unsafe_allow_html=True)

# --- 5. จัดการ API (คืนค่า Logic เดิมที่คุณเขียนไว้เพื่อให้คุยได้ปกติ) ---
api_key = st.secrets.get("GEMINI_API_KEY")
if api_key: genai.configure(api_key=api_key)

@st.cache_resource
def load_model():
    try:
        # ใช้ Logic การดึงชื่อโมเดลแบบเดิมที่ทำงานได้ชัวร์
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        selected = next((m for m in available_models if "1.5-flash" in m), available_models[0])
        return genai.GenerativeModel(model_name=selected)
    except: return None
model = load_model()

# --- 6. จัดการ State ---
if "all_chats" not in st.session_state: st.session_state.all_chats = {} 
if "messages" not in st.session_state: st.session_state.messages = []
if "current_chat_id" not in st.session_state: st.session_state.current_chat_id = None

# --- 7. Sidebar (ฟีเจอร์ครบ 100% ไม่ลบโค้ดส่วนไหนออก) ---
with st.sidebar:
    st.markdown('<div class="sidebar-header">', unsafe_allow_html=True)
    logo_data = get_image_base64("logo_ku.png")
    if logo_data:
        st.markdown(f'<img src="data:image/png;base64,{logo_data}" class="logo-img">', unsafe_allow_html=True)
    st.markdown(f'<div class="univ-name">{curr["univ_name"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.button(f"🌐 {st.session_state.lang}", on_click=toggle_language, use_container_width=True)
    
    if st.button(curr["new_chat"], key="new_chat_btn"):
        st.session_state.messages = []
        st.session_state.current_chat_id = None
        st.rerun()

    st.markdown("---")
    # เมนูส่วนตัวที่คุณใส่ไว้ กลับมาครบแน่นอน
    with st.expander(curr["exam_table"]):
        st.markdown(f'<div class="form-row"><span>KU Exam</span><a href="https://reg2.src.ku.ac.th/table_test/" target="_blank" class="btn-action">{curr["btn_find"]}</a></div>', unsafe_allow_html=True)
    with st.expander(curr["gpa_calc"]):
        st.markdown(f'<div class="form-row"><span>GPAX</span><a href="https://fna.csc.ku.ac.th/grade/" target="_blank" class="btn-action">{curr["btn_open"]}</a></div>', unsafe_allow_html=True)
    with st.expander(curr["forms"]):
        forms = [("ใบคำร้องทั่วไป", "https://registrar.ku.ac.th/wp-content/uploads/2023/11/General-Request.pdf")]
        for name, link in forms:
            st.markdown(f'<div class="form-row"><span>{name}</span><a href="{link}" target="_blank" class="btn-action">{curr["btn_download"]}</a></div>', unsafe_allow_html=True)

# --- 8. หน้า Chat หลัก ---
if not st.session_state.messages:
    st.markdown(f"<h1 style='text-align: center; color: #006861; margin-top: 15vh;'>{curr['welcome']}</h1>", unsafe_allow_html=True)
else:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if prompt := st.chat_input(curr["input_placeholder"]):
    if st.session_state.current_chat_id is None: st.session_state.current_chat_id = prompt[:20]
    
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown(curr["loading"])
        
        try:
            knowledge_base = ""
            if os.path.exists("ku_data.txt"):
                with open("ku_data.txt", "r", encoding="utf-8") as f: knowledge_base = f.read()
            
            # คืนค่า Logic History เดิมที่คุณเขียนไว้ในชุดแรก
            history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[-6:-1]]
            chat_session = model.start_chat(history=history)
            
            full_context = f"{curr['ai_identity']}\nข้อมูลมหาลัย: {knowledge_base}\nคำถาม: {prompt}"
            response = chat_session.send_message(full_context, stream=True)
            
            full_response = ""
            for chunk in response:
                full_response += chunk.text
                placeholder.markdown(full_response + "▌")
            placeholder.markdown(full_response)
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")
        
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.rerun()
