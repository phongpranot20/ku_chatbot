import streamlit as st
import google.generativeai as genai
import os

st.set_page_config(page_title="KU Sriracha AI Bot", page_icon="🦖", layout="wide")

# --- UI Customization (KU Green Premium Theme) ---
st.markdown("""
<style>
    /* พื้นหลังแบบไล่เฉดสีนวลตา */
    .stApp {
        background: linear-gradient(135deg, #f5fcf8 0%, #ffffff 100%);
    }

    /*Sidebar - สไตล์เข้มแบบพรีเมียม */
    [data-testid="stSidebar"] {
        background-color: #004d43 !important;
        box-shadow: 2px 0px 10px rgba(0,0,0,0.1);
    }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    
    /* ปุ่มใน Sidebar */
    .stSidebar [button] {
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.2);
        background-color: rgba(255,255,255,0.1);
    }

    /* หัวข้อหลัก */
    h1 {
        color: #00594C !important;
        font-family: 'Kanit', sans-serif;
        font-weight: 700;
        letter-spacing: -1px;
    }

    /* การตกแต่งกล่องข้อความแชท (Glassmorphism) */
    .stChatMessage {
        border-radius: 20px !important;
        margin-bottom: 1rem !important;
        padding: 1.5rem !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03) !important;
    }
    
    /* ผู้ใช้ (User) - ชิดขวา เขียวอ่อน */
    div[data-testid="stChatMessage"]:has(span:contains("🧑‍🎓")) {
        background-color: #e8f5e9 !important;
        border: 1px solid #c8e6c9 !important;
        margin-left: 15% !important;
    }

    /* บอท (Assistant) - ชิดซ้าย ขาวสะอาด */
    div[data-testid="stChatMessage"]:has(span:contains("🦖")) {
        background-color: #ffffff !important;
        border: 1px solid #f0f0f0 !important;
        margin-right: 15% !important;
    }

    /* ปุ่มทางลัด (Quick Reply) - ทรงมนสวยงาม */
    div.stButton > button {
        border-radius: 30px !important;
        border: 1px solid #00594C !important;
        color: #00594C !important;
        background-color: #ffffff !important;
        font-weight: 500 !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.3s ease !important;
    }
    div.stButton > button:hover {
        background-color: #00594C !important;
        color: #ffffff !important;
        transform: scale(1.05);
    }

    /* จุด Loading ใหญ่และมีสีสัน */
    .loading-dots {
        font-size: 30px;
        color: #00594C;
        letter-spacing: 5px;
    }
    .loading-dots:after {
        content: '.';
        animation: dots 1.5s infinite;
    }
    @keyframes dots {
        0%, 20% { content: '.'; }
        40% { content: '..'; }
        60% { content: '...'; }
        80%, 100% { content: ''; }
    }
</style>
""", unsafe_allow_html=True)

# --- Logic & API Setup ---
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("❌ ไม่พบ API Key")
    st.stop()

genai.configure(api_key=api_key)

@st.cache_resource
def load_model():
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if "flash" in m.name.lower():
                    return genai.GenerativeModel(model_name=m.name)
        return genai.GenerativeModel(model_name='gemini-1.5-flash')
    except: return None

model = load_model()

# --- Sidebar ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>KU SRC AI</h2>", unsafe_allow_html=True)
    st.markdown("---")
    if st.button("🔄 เริ่มการสนทนาใหม่"):
        st.session_state.messages = []
        st.rerun()
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.caption("เวอร์ชัน 1.5 - จำชื่อผู้ใช้และตอบไวพิเศษ")

# --- Main Page ---
st.title("🦖 น้องนนทรี AI")
st.markdown("<p style='color: #666;'>รุ่นพี่พร้อมตอบคำถามน้องๆ มก. ศรีราชา แล้วครับ!</p>", unsafe_allow_html=True)

# Quick Reply Buttons
st.markdown("---")
btn_prompt = None
c1, c2, c3, c4 = st.columns(4)
with c1:
    if st.button("🏢 พิกัดตึกเรียน"): btn_prompt = "ขอพิกัดตึกเรียนสำคัญใน มก. ศรีราชา"
with c2:
    if st.button("🍜 แนะนำของกิน"): btn_prompt = "แถวมอมีอะไรอร่อยบ้าง แนะนำหน่อยครับ"
with c3:
    if st.button("📑 ติดต่อทะเบียน"): btn_prompt = "อยากติดต่อเรื่องเอกสารการเรียนต้องไปที่ไหน"
with c4:
    if st.button("🚐 ตารางรถตะไล"): btn_prompt = "ขอเส้นทางและเวลาเดินรถตะไลครับ"

# Message History
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    avatar = "🧑‍🎓" if message["role"] == "user" else "🦖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Chat Input Logic
chat_input = st.chat_input("คุยกับพี่นนทรี...")
prompt = chat_input if chat_input else btn_prompt

if prompt:
    with st.chat_message("user", avatar="🧑‍🎓"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="🦖"):
        status_placeholder = st.empty()
        status_placeholder.markdown('<div class="loading-dots"></div>', unsafe_allow_html=True)
        
        # Load Knowledge Base
        kb = ""
        if os.path.exists("ku_data.txt"):
            with open("ku_data.txt", "r", encoding="utf-8") as f:
                kb = f.read()

        instruction = (
            "คุณคือ 'น้องนนทรี' AI รุ่นพี่สุดเท่แห่ง มก. ศรีราชา (KU SRC) "
            "พูดจาสุภาพ เป็นกันเอง แทนตัวเองว่า 'พี่' และเรียกผู้ใช้ว่า 'น้อง' "
            "จงจำชื่อผู้ใช้หากเขาบอกชื่อมา และใช้ชื่อเขาในการคุยเสมอ "
            "ใช้ข้อมูลมหาวิทยาลัยที่ให้มาตอบอย่างรวดเร็วและเป็นมิตร"
        )
        
        history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-10:]])
        full_p = f"{instruction}\n\nข้อมูล: {kb}\n\nประวัติการคุย:\n{history}\n\nคำถาม: {prompt}"
        
        try:
            response = model.generate_content(full_p)
            status_placeholder.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            status_placeholder.empty()
            st.error(f"ขอโทษทีครับน้อง พี่เกิดข้อผิดพลาดนิดหน่อย: {e}")
