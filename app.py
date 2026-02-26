import streamlit as st
import google.generativeai as genai
import os

# --- ตั้งค่าหน้าจอ ---
st.set_page_config(page_title="น้องนนทรี - KU Sriracha Bot", page_icon="🐯", layout="wide")

# --- CSS ปรับแต่งความสวยงาม ---
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; color: black; }
    [data-testid="stSidebar"] { background-color: #00594C !important; }
    .stSidebar [data-testid="stMarkdownContainer"] p, .stSidebar h3 { color: white !important; }
    h1 { color: #00594C !important; }
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# --- ส่วนจัดการ API ---
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("❌ ไม่พบ GEMINI_API_KEY ใน Streamlit Secrets")
    st.stop()

genai.configure(api_key=api_key)

@st.cache_resource
def load_model():
    instruction = (
        "คุณคือ 'น้องนนทรี' AI รุ่นพี่ มก. ศรีราชา (KU SRC) "
        "1. ตอบคำถามโดยใช้ข้อมูลจาก 'ข้อมูลอ้างอิง' ที่ให้มาเป็นหลัก "
        "2. ถ้าถามหาแบบฟอร์ม ให้ส่งชื่อแบบฟอร์มพร้อมลิงก์ PDF ตรงๆ ทันที "
        "3. ถ้าถามหาสถานที่ ให้บอกพิกัดจากลิงก์ Google Maps ที่เตรียมไว้ให้ "
        "4. ห้ามแสดงตัวเลขละติจูด/ลองจิจูด (GPS) ให้ผู้ใช้เห็น "
        "5. ใช้สรรพนาม พี่-น้อง และตอบอย่างเป็นกันเองแต่สุภาพ"
    )
    return genai.GenerativeModel(model_name="gemini-1.5-flash", system_instruction=instruction)

model = load_model()

# --- ส่วน Sidebar (แก้ไข Iframe แผนที่ให้ถูกต้อง) ---
with st.sidebar:
    st.image("https://www.src.ku.ac.th/th/images/logo/KU_Sriracha_Logo.png", width=150)
    st.markdown("### 📍 แผนที่วิทยาเขตศรีราชา")
    
    # ใช้พิกัดกลางของ มก.ศรช. เพื่อเลี่ยง Error pb parameter
    map_url = "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3882.443217424641!2d100.9201!3d13.1158!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3102b1156a5c531d%3A0x600b2158864700!2z4Lih4Lir4Liy4Lin4Li04LiX4Lii4Liy4Lis4Liy4LiU4Lio4Liy4Liq4LiV4Lij4LiU4LmA4LiB4Liy4Lij4LiK4Liy4Liq4Liy4LiX4Lij4Liy4LiE4Li1!5e0!3m2!1sth!2sth!4v1700000000000"
    st.components.v1.html(f'<iframe src="{map_url}" width="100%" height="300" style="border:0; border-radius:10px;" allowfullscreen="" loading="lazy"></iframe>', height=320)
    st.info("💡 น้องๆ ถามทางหรือขอแบบฟอร์มกับพี่นนทรีได้เลยนะครับ")

# --- การจัดการ Chat ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# โหลด Knowledge Base
if os.path.exists("ku_data.txt"):
    with open("ku_data.txt", "r", encoding="utf-8") as f:
        knowledge_base = f.read()
else:
    knowledge_base = "ข้อมูล มก. ศรีราชา"

# แสดงประวัติ
for m in st.session_state.messages:
    with st.chat_message(m["role"], avatar="🧑‍🎓" if m["role"] == "user" else "🐯"):
        st.markdown(m["content"])

# ส่วนรับ Input
if prompt := st.chat_input("พิมพ์คำถามที่นี่..."):
    st.chat_message("user", avatar="🧑‍🎓").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="🐯"):
        placeholder = st.empty()
        placeholder.markdown("*(กำลังประมวลผล...)*")
        
        full_prompt = f"ข้อมูลอ้างอิง:\n{knowledge_base}\n\nคำถาม: {prompt}"
        
        try:
            # ใช้ Stream เพื่อให้ดูเหมือน AI กำลังพิมพ์
            response = model.generate_content(full_prompt, stream=True)
            full_response = ""
            for chunk in response:
                full_response += chunk.text
                placeholder.markdown(full_response + "▌")
            
            placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            st.rerun()
        except Exception as e:
            st.error(f"Error: {str(e)}")
