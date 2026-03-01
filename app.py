import streamlit as st
import google.generativeai as genai
import os
import base64
import re

# --- 1. ตั้งค่าหน้าจอ ---
st.set_page_config(page_title="AI KUSRC", page_icon="🦖", layout="wide")

# --- 2. ระบบจัดการภาษา ---
if "lang" not in st.session_state:
    st.session_state.lang = "TH"

def toggle_language():
    st.session_state.lang = "EN" if st.session_state.lang == "TH" else "TH"

translation = {
    "TH": {
        "univ_name": "Kasetsart University<br><small>Sriracha Campus</small>",
        "new_chat": "➕ เริ่มแชทใหม่",
        "chat_hist": "💬 ประวัติการแชท",
        "exam_table": "📅 ค้นหาตารางสอบ",
        "gpa_calc": "🧮 คำนวณเกรด (GPA)",
        "forms": "📄 ลิงก์แบบฟอร์มต่างๆ",
        "btn_find": "ค้นหา", "btn_open": "เปิดระบบ", "btn_download": "โหลด",
        "input_placeholder": "พิมพ์ถามพี่นนทรีได้เลย...",
        "welcome_main": "สวัสดีครับ มีอะไรให้พี่ช่วยไหม?",
        "loading": "*(กำลังหาคำตอบให้...)*",
        "ai_identity": "คุณคือรุ่นพี่ มก.ศรช. ใจดี ตอบเป็นภาษาไทยเป็นหลัก"
    },
    "EN": {
        "univ_name": "Kasetsart University<br><small>Sriracha Campus</small>",
        "new_chat": "➕ New Chat",
        "chat_hist": "💬 Chat History",
        "exam_table": "📅 Exam Schedule",
        "gpa_calc": "🧮 GPA Calculator",
        "forms": "📄 Document Forms",
        "btn_find": "Search", "btn_open": "Open", "btn_download": "Get",
        "input_placeholder": "Ask Nontri anything...",
        "welcome_main": "How can I help you today?",
        "loading": "*(Thinking...)*",
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
    if len(code) >= 4:
        return f"📍 ห้อง {code} อยู่ที่อาคารเรียนรวมครับ" if st.session_state.lang == "TH" else f"📍 Room {code} is in the main building."
    return None

# --- 4. CSS (จัดเต็มความมินิมอล + สีเขียว KU) ---
st.markdown(f"""
<style>
    .stApp {{ background-color: #FFFFFF; }}
    [data-testid="stSidebar"] {{ background-color: #F8F9FA !important; border-right: 1px solid #EEE; }}
    
    /* หัวข้อ Sidebar และ Logo */
    .sidebar-header {{ text-align: center; padding: 10px; margin-bottom: 20px; }}
    .logo-img {{ width: 85px; margin-bottom: 10px; }}
    .univ-title {{ color: #006861; font-weight: bold; font-size: 16px; line-height: 1.2; }}

    /* ปุ่มหลักใน Sidebar */
    div.stButton > button {{
        width: 100% !important; border-radius: 10px !important;
        background-color: white !important; color: #006861 !important;
        border: 1px solid #E0E0E0 !important; transition: 0.2s;
        text-align: left !important; padding: 8px 15px !important;
    }}
    div.stButton > button:hover {{ border-color: #006861 !important; background-color: #F0F7F6 !important; }}
    
    /* ปุ่ม 'เริ่มแชทใหม่' ให้เด่นด้วยสีเขียว */
    .st-key-new_chat_btn button {{ background-color: #006861 !important; color: white !important; font-weight: bold !important; }}

    /* ปรับปรุงหน้าตา Expander (เมนูคำนวณเกรด/ตารางสอบ) */
    div[data-testid="stExpander"] {{ border: none !important; background: transparent !important; box-shadow: none !important; }}
    .form-row {{ display: flex; justify-content: space-between; align-items: center; padding: 5px 0; border-bottom: 1px solid #F0F0F0; }}
    .btn-action {{ background-color: #006861; color: white !important; padding: 3px 12px; border-radius: 6px; text-decoration: none; font-size: 12px; }}

    /* ปรับแต่งแชท */
    .stChatMessage {{ border: none !important; }}
</style>
""", unsafe_allow_html=True)

# --- 5. จัดการ API ---
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

# --- 6. State Management ---
if "all_chats" not in st.session_state: st.session_state.all_chats = {} 
if "messages" not in st.session_state: st.session_state.messages = []
if "current_chat_id" not in st.session_state: st.session_state.current_chat_id = None

# --- 7. Sidebar (ฟีเจอร์ครบถ้วน) ---
with st.sidebar:
    # 1. Logo & Name
    st.markdown('<div class="sidebar-header">', unsafe_allow_html=True)
    logo_data = get_image_base64("logo_ku.png")
    if logo_data:
        st.markdown(f'<img src="data:image/png;base64,{logo_data}" class="logo-img">', unsafe_allow_html=True)
    st.markdown(f'<div class="univ-title">{curr["univ_name"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 2. Language & New Chat
    st.button(f"🌐 {st.session_state.lang}", on_click=toggle_language, use_container_width=True)
    if st.button(curr["new_chat"], key="new_chat_btn", use_container_width=True):
        st.session_state.messages = []
        st.session_state.current_chat_id = None
        st.rerun()

    # 3. Chat History
    if st.session_state.all_chats:
        st.caption(curr["chat_hist"])
        for chat_id in list(st.session_state.all_chats.keys()):
            if st.button(f"📄 {chat_id[:18]}...", key=f"hist_{chat_id}"):
                st.session_state.current_chat_id = chat_id
                st.session_state.messages = st.session_state.all_chats[chat_id]
                st.rerun()

    st.markdown("---")
    
    # 4. เมนูคำนวณเกรด / ตารางสอบ (กลับมาแล้ว!)
    with st.expander(curr["exam_table"]):
        st.markdown(f'<div class="form-row"><span>KU Exam</span><a href="https://reg2.src.ku.ac.th/table_test/" target="_blank" class="btn-action">{curr["btn_find"]}</a></div>', unsafe_allow_html=True)
    
    with st.expander(curr["gpa_calc"]):
        st.markdown(f'<div class="form-row"><span>GPAX Calculator</span><a href="https://fna.csc.ku.ac.th/grade/" target="_blank" class="btn-action">{curr["btn_open"]}</a></div>', unsafe_allow_html=True)
    
    with st.expander(curr["forms"]):
        forms = [("ใบคำร้องทั่วไป", "https://registrar.ku.ac.th/wp-content/uploads/2023/11/General-Request.pdf")]
        for name, link in forms:
            st.markdown(f'<div class="form-row"><span style="font-size:12px;">{name}</span><a href="{link}" target="_blank" class="btn-action">{curr["btn_download"]}</a></div>', unsafe_allow_html=True)

# --- 8. Main Chat ---
if not st.session_state.messages:
    st.markdown(f"<h1 style='text-align: center; color: #006861; margin-top: 10vh; font-weight: 600;'>{curr['welcome_main']}</h1>", unsafe_allow_html=True)

for message in st.session_state.messages:
    avatar = "🧑‍🎓" if message["role"] == "user" else "🦖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

if prompt := st.chat_input(curr["input_placeholder"]):
    if st.session_state.current_chat_id is None: st.session_state.current_chat_id = prompt[:20]
    st.chat_message("user", avatar="🧑‍🎓").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="🦖"):
        placeholder = st.empty()
        placeholder.markdown(curr["loading"])
        
        # จัดการคำถามเรื่องห้องเรียน
        room_info = get_room_info(prompt)
        if room_info:
            full_response = room_info
            placeholder.markdown(full_response)
        else:
            try:
                kb = ""
                if os.path.exists("ku_data.txt"):
                    with open("ku_data.txt", "r", encoding="utf-8") as f: kb = f.read()
                
                history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[-6:-1]]
                chat_session = model.start_chat(history=history)
                
                full_context = f"{curr['ai_identity']}\nข้อมูลมหาลัย: {kb}\nคำถาม: {prompt}"
                response = chat_session.send_message(full_context, stream=True)
                
                full_response = ""
                for chunk in response:
                    full_response += chunk.text
                    placeholder.markdown(full_response + "▌")
                placeholder.markdown(full_response)
            except Exception as e:
                full_response = f"ขออภัยครับ เกิดข้อผิดพลาด: {e}"
                st.error(full_response)
        
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.session_state.all_chats[st.session_state.current_chat_id] = st.session_state.messages
        st.rerun()
