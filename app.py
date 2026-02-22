import streamlit as st
import google.generativeai as genai
import os
import random
from datetime import date

# 1. Page Configuration
st.set_page_config(page_title="KU SRC AI - พี่นนทรี", page_icon="🦖", layout="wide")

# 2. Premium CSS (Glassmorphism + KU Theme)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;600&display=swap');
    * { font-family: 'Kanit', sans-serif; }
    .stApp { background: radial-gradient(circle at top left, #f0fdf4 0%, #ffffff 100%); }
    
    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #004d43 !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }

    /* Glass Chat Bubbles */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.7) !important;
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.4);
        border-radius: 20px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05) !important;
    }

    /* Quick Action Buttons */
    div.stButton > button {
        border-radius: 20px !important;
        border: 1px solid #00594C !important;
        transition: all 0.3s ease;
        width: 100%;
    }
    div.stButton > button:hover {
        background-color: #00594C !important;
        color: white !important;
        transform: translateY(-2px);
    }

    /* Header Styling */
    .main-title {
        font-size: 38px; font-weight: 800;
        background: linear-gradient(90deg, #00594C, #2D6A4F);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
</style>
""", unsafe_allow_html=True)

# 3. Model Logic (Auto-Detect)
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("❌ ลืมตั้งค่า GEMINI_API_KEY ใน Secrets ครับฮอน")
    st.stop()

genai.configure(api_key=api_key)

@st.cache_resource
def load_ai_model():
    try:
        # ใช้รุ่นที่รองรับทั้งข้อความและรูปภาพ
        return genai.GenerativeModel('gemini-1.5-flash')
    except:
        return None

model = load_ai_model()

# 4. Sidebar Content (Function 3 & 4)
with st.sidebar:
    st.markdown("<h1 style='text-align:center;'>🦖</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;'>พี่นนทรี Digital Assistant</h3>", unsafe_allow_html=True)
    
    # Event Countdown (Function 3)
    exam_date = date(2026, 3, 2) # สมมติวันสอบ
    days_left = (exam_date - date.today()).days
    st.info(f"📅 อีก {days_left} วันจะถึงวันสอบไฟนอล!")
    
    if st.button("✨ ล้างการสนทนา"):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    # Multi-modal Input (Function 1)
    st.markdown("📷 **ส่งรูปให้พี่ช่วยดูได้นะ**")
    uploaded_file = st.file_uploader("เช่น ตารางเรียน หรือเมนูอาหาร", type=['png', 'jpg', 'jpeg'])

# 5. Main UI
st.markdown("<h1 class='main-title'>🦖 น้องนนทรี AI (KU SRC)</h1>", unsafe_allow_html=True)

# Quick Reply & Utility (Function 3 & 5)
col1, col2, col3, col4 = st.columns(4)
btn_prompt = None
with col1:
    if st.button("📍 พิกัดตึกเรียน"): btn_prompt = "ขอพิกัดตึกเรียนสำคัญใน มก. ศรีราชา พร้อมคำแนะนำการเดินทาง"
with col2:
    if st.button("🎲 สุ่มเมนูอาหาร"):
        menus = ["ข้าวมันไก่โรง 1", "ก๋วยเตี๋ยวข้างมอ", "สเต็กเด็กแนว", "ส้มตำป้าแดง"]
        choice = random.choice(menus)
        btn_prompt = f"พี่สุ่มได้ '{choice}' ครับ น้องว่าร้านนี้โอเคไหม?"
with col3:
    if st.button("📚 ที่อ่านหนังสือ"): btn_prompt = "แนะนำที่อ่านหนังสือเงียบๆ ในมอหน่อยพี่"
with col4:
    if st.button("🚌 รถตะไลสายไหน?"): btn_prompt = "จะไปหน้ามอ ต้องขึ้นรถตะไลสายไหนครับ"

# 6. Chat Logic
if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"], avatar="🧑‍🎓" if m["role"] == "user" else "🦖"):
        st.markdown(m["content"])

# Input Handling
chat_input = st.chat_input("คุยกับพี่นนทรีได้เลย...")
prompt = chat_input if chat_input else btn_prompt

if prompt:
    # แสดงข้อความฝั่ง User
    with st.chat_message("user", avatar="🧑‍🎓"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # ฝั่ง AI ตอบกลับ
    with st.chat_message("assistant", avatar="🦖"):
        status = st.empty()
        status.markdown("กำลังคิดแป๊บนึงนะน้อง...")

        # ระบบ Knowledge Base เชิงลึก (Function 5)
        instruction = (
            "คุณคือ 'พี่นนทรี' รุ่นพี่ใจดีแห่ง มก. ศรีราชา "
            "ตอบแบบสนิทสนม แทนตัวเองว่าพี่ เรียกผู้ใช้ว่าน้อง "
            "ต้องให้ข้อมูลที่เป็น 'Inside' เช่น ร้านไหนรอนาน ตึกไหนแอร์หนาว "
            "ถ้ามีการอัปโหลดรูป ให้วิเคราะห์รูปนั้นอย่างละเอียดในบริบทนิสิต"
        )
        
        # เตรียมเนื้อหาสำหรับส่งให้ Model
        content_to_send = [f"{instruction}\n\nคำถาม: {prompt}"]
        
        # ถ้ามีการอัปโหลดรูป (Function 1)
        if uploaded_file:
            import PIL.Image
            img = PIL.Image.open(uploaded_file)
            content_to_send.append(img)
            content_to_send.append("ช่วยวิเคราะห์รูปนี้ในฐานะรุ่นพี่ มก. หน่อยครับ")

        try:
            response = model.generate_content(content_to_send)
            status.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            status.empty()
            st.error(f"พี่ขัดข้องนิดหน่อย: {e}")
