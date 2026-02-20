import streamlit as st
import google.generativeai as genai
import os

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(
    page_title="KU Sriracha Bot",
    page_icon="🐢",
    layout="wide"
)

# 🎨 ธีมสีเขียว KU
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF !important; color: black !important; }
    [data-testid="stSidebar"] { background-color: #f2f9f6 !important; }
    h1, h2, h3, p, span, div { color: #00594C; }
    [data-testid="stChatMessage"] { background-color: #f0f2f6; border-radius: 10px; }
    .stMarkdown p { color: #333333 !important; }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# 2. ระบบตรวจสอบ API Key (Debug Mode)
# -------------------------------------------------------------
api_key = None

# ตรวจสอบว่ามีคีย์ใน Secrets หรือไม่
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
elif os.environ.get("GEMINI_API_KEY"):
    api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("❌ ไม่พบ API Key ในระบบ Secrets")
    st.info("💡 วิธีแก้: ไปที่ Settings > Secrets แล้วใส่ GEMINI_API_KEY = 'รหัสของคุณ'")
    st.stop()

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    # ทดสอบเรียกโมเดลเบื้องต้น
    model.generate_content("test")
except Exception as e:
    st.error(f"❌ API Key มีปัญหาหรือหมดอายุ: {e}")
    st.stop()

# -------------------------------------------------------------
# 3. การจัดการข้อมูลและแชท
# -------------------------------------------------------------
st.title("🐢 น้องนนทรี (AI Assistant)")

# โหลดข้อมูลจาก ku_data.txt
if os.path.exists("ku_data.txt"):
    with open("ku_data.txt", "r", encoding="utf-8") as f:
        knowledge_base = f.read()
else:
    st.warning("⚠️ ไม่พบไฟล์ ku_data.txt กรุณาอัปโหลดไฟล์ข้อมูลด้วยครับ")
    knowledge_base = "ข้อมูลมหาวิทยาลัยเกษตรศาสตร์ วิทยาเขตศรีราชา"

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🧑‍🎓" if message["role"] == "user" else "🦖"):
        st.markdown(message["content"])

if prompt := st.chat_input("พิมพ์คำถามที่นี่..."):
    st.chat_message("user", avatar="🧑‍🎓").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="🦖"):
        instruction = (
            "คุณคือ 'น้องนนทรี' AI รุ่นพี่ของ มก. ศรีราชา (KU SRC) "
            "ใช้ข้อมูลอ้างอิงที่ให้มาเท่านั้นในการตอบ "
            "หากถามเรื่องตึก ต้องส่งลิ้งค์แผนที่เสมอ และตอบอย่างสุภาพ"
        )
        full_prompt = f"{instruction}\n\nข้อมูลอ้างอิง: {knowledge_base}\n\nคำถาม: {prompt}"
        
        try:
            response = model.generate_content(full_prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในการสร้างคำตอบ: {e}")
