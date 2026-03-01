import streamlit as st
import google.generativeai as genai
import os
import base64
import re

# --- 1. ตั้งค่าหน้าจอ (Professional Config) ---
st.set_page_config(page_title="AI KUSRC", page_icon="🦖", layout="wide")

# --- 2. ระบบจัดการภาษา (คงเดิม 100%) ---
if "lang" not in st.session_state:
    st.session_state.lang = "TH"

def toggle_language():
    st.session_state.lang = "EN" if st.session_state.lang == "TH" else "TH"

translation = {
    "TH": {
        "univ_name": "Kasetsart University<br><small>Sriracha Campus</small>",
        "new_chat": "➕ เริ่มแชทใหม่",
        "chat_hist": "ประวัติการสนทนา",
        "exam_table": "📅 ตารางสอบ",
        "gpa_calc": "🧮 คำนวณเกรด (GPA)",
        "forms": "📄 แบบฟอร์มต่างๆ",
        "input_placeholder": "พิมพ์คำถามของคุณที่นี่...",
        "welcome": "สวัสดีครับ",
        "loading": "กำลังประมวลผล...",
        "btn_find": "ค้นหา", "btn_open": "เปิด", "btn_download": "ดาวน์โหลด",
        "ai_identity": "คุณคือรุ่นพี่ มก.ศรช. ผู้เชี่ยวชาญ ตอบเป็นภาษาไทยเป็นหลัก"
    },
    "EN": {
        "univ_name": "Kasetsart University<br><small>Sriracha Campus</small>",
        "new_chat": "➕ New Chat",
        "chat_hist": "Recent History",
        "exam_table": "📅 Exam Schedule",
        "gpa_calc": "🧮 GPA Calculator",
        "forms": "📄 Document Forms",
        "input_placeholder": "Message Nontri AI...",
        "welcome": "Welcome",
        "loading": "Thinking...",
        "btn_find": "Find", "btn_open": "Open", "btn_download": "Get",
        "ai_identity": "You are a professional KU Sriracha senior. Please respond in English."
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
        return f"📍 ข้อมูลสถานที่: **ตึก {code[:2]} ชั้น {code[2]} ห้อง {code[3:]}**" if st.session_state.lang == "TH" else f"📍 Location: **Building {code[:2]}, Floor {code[2]}, Room {code[3:]}**"
    return None

# --- 4. CSS (Professional Gemini Style) ---
st.markdown(f"""
<style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    html, body, [class*="st-"] {{ font-family: 'Inter', sans-serif; color: #1f1f1f; }}
    .stApp {{ background-color: #FFFFFF; }}

    /* Sidebar - Pro Design */
    [data-testid="stSidebar"] {{ 
        background-color: #f8fafd !important; 
        border-right: 1px solid #e3e3e3; 
        padding-top: 1rem;
    }}
    .sidebar-header {{ text-align: center; padding: 1.5rem 1rem; border-bottom: 1px solid #e3e3e3; margin-bottom: 1rem; }}
    .univ-name {{ color: #006861; font-weight: 600; font-size: 1.1rem; line-height: 1.2; }}
    
    /* Buttons in Sidebar */
    div.stButton > button {{
        width: 100% !important; border-radius: 12px !important; border: none !important;
        background-color: transparent !important; color: #444746 !important;
        text-align: left !important; padding: 12px 16px !important; font-weight: 500;
    }}
    div.stButton > button:hover {{ background-color: #eff1f3 !important; }}
    
    /* New Chat Button */
    .st-key-new_chat_btn button {{ 
        background-color: #d3e3fd !important; 
        color: #041e49 !important; 
        margin-bottom: 1rem !important;
    }}
    .st-key-new_chat_btn button:hover {{ background-color: #c2d7f7 !important; }}

    /* Chat Container */
    .stChatMessage {{ 
        max-width: 850px !important; 
        margin: 0 auto !important; 
        padding: 1.5rem 0 !important;
        border: none !important;
        background-color: transparent !important;
    }}
    
    /* Assistant Bubble (Gemini Style) */
    [data-testid="stChatMessageAssistant"] {{
        background-color: #f0f4f9 !important;
        border-radius: 24px !important;
        padding: 1.5rem 2rem !important;
        margin-top: 0.5rem;
    }}
    
    /* User Message - Clean (No Bubble) */
    [data-testid="stChatMessageUser"] {{
        background-color: transparent !important;
        font-weight: 500;
        font-size: 1.1rem;
    }}

    /* Input Field - Floating Gemini Style */
    div[data-testid="stChatInput"] {{
        border: none !important;
        background-color: #f0f4f9 !important;
        border-radius: 28px !important;
        padding: 8px 16px !important;
        max-width: 850px !important;
        margin: 0 auto !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05) !important;
    }}
    
    /* Expander - Clean */
    div[data-testid="stExpander"] {{ border: 1px solid #e3e3e3 !important; border-radius: 12px !important; background: white !important; }}
    .form-row {{ display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #f0f0f0; }}
    .btn-action {{ background-color: #006861; color: white !important; padding: 5px 14px; border-radius: 8px; text-decoration: none; font-size: 12px; font-weight: 500; }}
</style>
""", unsafe_allow_html=True)

# --- 5. จัดการ API (คงเดิม) ---
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
if "messages" not in st.session_state: st.session_state.messages = []
if "all_chats" not in st.session_state: st.session_state.all_chats = {} 
if "current_chat_id" not in st.session_state: st.session_state.current_chat_id = None

# --- 7. Sidebar ---
with st.sidebar:
    st.markdown('<div class="sidebar-header">', unsafe_allow_html=True)
    logo_data = get_image_base64("logo_ku.png")
    if logo_data:
        st.markdown(f'<img src="data:image/png;base64,{logo_data}" style="width:70px; margin-bottom:10px;">', unsafe_allow_html=True)
    st.markdown(f'<div class="univ-name">{curr["univ_name"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.button(f"🌐 {st.session_state.lang}", on_click=toggle_language, use_container_width=True)
    
    if st.button(curr["new_chat"], key="new_chat_btn"):
        st.session_state.messages = []
        st.session_state.current_chat_id = None
        st.rerun()
    
    if st.session_state.all_chats:
        st.caption(f"**{curr['chat_hist']}**")
        for cid in list(st.session_state.all_chats.keys()):
            if st.button(f"💬 {cid[:15]}...", key=f"h_{cid}"):
                st.session_state.current_chat_id = cid
                st.session_state.messages = st.session_state.all_chats[cid]
                st.rerun()

    st.markdown("---")
    with st.expander(curr["exam_table"]):
        st.markdown(f'<div class="form-row"><span>Exam Table</span><a href="https://reg2.src.ku.ac.th/table_test/" target="_blank" class="btn-action">{curr["btn_find"]}</a></div>', unsafe_allow_html=True)
    with st.expander(curr["gpa_calc"]):
        st.markdown(f'<div class="form-row"><span>GPAX Calc</span><a href="https://fna.csc.ku.ac.th/grade/" target="_blank" class="btn-action">{curr["btn_open"]}</a></div>', unsafe_allow_html=True)

# --- 8. Main Chat Logic ---
if not st.session_state.messages:
    st.markdown(f"<h1 style='text-align: center; color: #006861; margin-top: 20vh; font-weight: 500;'>{curr['welcome']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: #444746; font-size: 1.1rem;'>How can I help you with KUSRC information today?</p>", unsafe_allow_html=True)

# วนลูปแสดงข้อความ (No Avatars/Stickers)
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input(curr["input_placeholder"]):
    if st.session_state.current_chat_id is None: st.session_state.current_chat_id = prompt[:25]
    
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown(f"*{curr['loading']}*")
        
        room_info = get_room_info(prompt)
        if room_info:
            full_res = room_info
            placeholder.markdown(full_res)
        else:
            try:
                kb = ""
                if os.path.exists("ku_data.txt"):
                    with open("ku_data.txt", "r", encoding="utf-8") as f: kb = f.read()
                
                history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[-6:-1]]
                chat_session = model.start_chat(history=history)
                
                full_context = f"{curr['ai_identity']}\nKnowledge Base: {kb}\nQuestion: {prompt}"
                response = chat_session.send_message(full_context, stream=True)
                
                full_res = ""
                for chunk in response:
                    full_res += chunk.text
                    placeholder.markdown(full_res + "▌")
                placeholder.markdown(full_res)
            except Exception as e:
                full_res = f"Error: {e}"
                st.error(full_res)
        
        st.session_state.messages.append({"role": "assistant", "content": full_res})
        st.session_state.all_chats[st.session_state.current_chat_id] = st.session_state.messages
        st.rerun()
