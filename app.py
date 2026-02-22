import streamlit as st
import google.generativeai as genai
import os

st.set_page_config(page_title="KU SRC AI - น้องนนทรี", page_icon="🦖", layout="wide")

# --- CUSTOM CSS: ULTIMATE DESIGN ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;600&display=swap');
    * { font-family: 'Kanit', sans-serif; }
    .stApp { background: radial-gradient(circle at top left, #f0fdf4 0%, #ffffff 100%); }
    [data-testid="stSidebar"] { background-color: #004d43 !important; border-right: 1px solid rgba(255,255,255,0.1); }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    .main-title {
        font-size: 42px; font-weight: 800;
        background: linear-gradient(90deg, #00594C, #2D6A4F);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .stChatMessage {
        background: rgba(255, 255, 255, 0.7) !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.4);
        border-radius: 25px !important;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.05) !important;
        margin-bottom: 15px !important;
        padding: 20px !important;
    }
    div[data-testid="stChatMessage"]:has(span:contains("🧑‍🎓")) {
        border-bottom-right-radius: 2px !important;
        background: rgba(230, 244, 234, 0.8) !important;
    }
    div[data-testid="stChatMessage"]:has(span:contains("🦖")) {
        border-bottom-left-radius: 2px !important;
    }
    div.stButton > button {
        border-radius: 50px !important;
        border: 2px solid #00594C !important;
        background-color: transparent !important;
        color: #00594C !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        padding: 10px 25px !important;
        width: 100%;
    }
    div.stButton > button:hover {
        background-color: #00594C !important;
        color: #ffffff !important;
        box-shadow: 0 4px 15px rgba(0, 89, 76, 0.3);
    }
    .loading-container { display: flex; gap: 5px; padding: 10px; }
    .dot { width: 10px; height: 10px; background: #00594C; border-radius: 50%; animation: wave 1.3s linear infinite; }
    .dot:nth-child(2) { animation-delay: -1.1s; }
    .dot:nth-child(3) { animation-delay: -0.9s; }
    @keyframes wave { 0%, 60%, 100% { transform: translateY(0); } 30% { transform: translateY(-10px); } }
</style>
""", unsafe_allow_html=True)

# --- AUTO-DETECT MODEL LOGIC ---
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("❌ กรุณาตั้งค่า GEMINI_API_KEY ใน Secrets")
    st.stop()

genai.configure(api_key=api_key)

@st.cache_resource
def load_available_model():
    try:
        # วนลูปหาชื่อโมเดลที่ใช้งานได้จริงใน Key นี้
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if "flash" in m.name.lower():
                    return genai.GenerativeModel(model_name=m.name)
        # ถ้าไม่มี flash ให้เอาตัวแรกที่เจอ
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                return genai.GenerativeModel(model_name=m.name)
    except Exception as e:
        st.error(f"❌ ระบบไม่สามารถดึงข้อมูลโมเดลได้: {e}")
    return None

model = load_available_model()

if not model:
    st.stop()

# Sidebar
with st.sidebar:
    st.markdown("<h1 style='text-align:center;'>🦖</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;'>KU SRC AI</h3>", unsafe_allow_html=True)
    st.markdown("---")
    if st.button("✨ เริ่มบทสนทนาใหม่"):
        st.session_state.messages = []
        st.rerun()

# Header
st.markdown("<h1 class='main-title'>น้องนนทรี AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #4A5568;'>รุ่นพี่ AI พร้อมช่วยเหลือดูแลน้องๆ มก. ศรีราชา แล้วครับผม!</p>", unsafe_allow_html=True)

# Quick Reply Buttons
st.markdown("<br>", unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
btn_prompt = None
with c1:
    if st.button("🏢 พิกัดตึกเรียน"): btn_prompt = "ขอพิกัดตึกเรียนสำคัญใน มก. ศรีราชา"
with c2:
    if st.button("🍜 ของกินรอบมอ"): btn_prompt = "รอบ มก. ศรีราชา มีอะไรอร่อยบ้าง แนะนำหน่อยครับ"
with c3:
    if st.button("📑 ติดต่อฝ่ายทะเบียน"): btn_prompt = "อยากติดต่อเรื่องเอกสารการเรียนต้องไปที่ไหน"
with c4:
    if st.button("🚐 ข้อมูลรถตะไล"): btn_prompt = "ขอเส้นทางและเวลาเดินรถตะไลครับ"

# Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    avatar = "🧑‍🎓" if message["role"] == "user" else "🦖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Input
chat_input = st.chat_input("พิมพ์ข้อความคุยกับพี่นนทรี...")
prompt = chat_input if chat_input else btn_prompt

if prompt:
    with st.chat_message("user", avatar="🧑‍🎓"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="🦖"):
        status_placeholder = st.empty()
        status_placeholder.markdown("""
            <div class="loading-container"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div>
        """, unsafe_allow_html=True)
        
        kb = ""
        if os.path.exists("ku_data.txt"):
            with open("ku_data.txt", "r", encoding="utf-8") as f: kb = f.read()

        instruction = (
            "คุณคือ 'น้องนนทรี' AI รุ่นพี่ของ มก. ศรีราชา (KU SRC) "
            "พูดจาสุภาพ เป็นกันเอง แทนตัวเองว่า 'พี่' และเรียกผู้ใช้ว่า 'น้อง' "
            "จงจำชื่อผู้ใช้หากเขาบอกชื่อมา และใช้ข้อมูลที่ให้มาตอบอย่างอบอุ่น"
        )
        
        history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-10:]])
        full_p = f"{instruction}\n\nข้อมูล: {kb}\n\nประวัติ: {history}\n\nคำถาม: {prompt}"
        
        try:
            response = model.generate_content(full_p)
            status_placeholder.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            status_placeholder.empty()
            st.error(f"ขอโทษครับน้อง พี่ขัดข้องนิดหน่อย: {e}")
