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
# 2. ระบบดึง API Key จาก Secrets
# -------------------------------------------------------------
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("❌ ไม่พบ GEMINI_API_KEY ในหน้า Settings > Secrets")
    st.stop()

genai.configure(api_key=api_key)

# ใช้ชื่อโมเดลที่ยืนยันแล้วจากหน้า Diagnostic ของคุณ
try:
    model = genai.GenerativeModel('gemini-2.0-flash-exp') # หรือ 'gemini-1.5-flash' ตามที่ระบบคุณรองรับ
except Exception as e:
    st.error(f"เชื่อมต่อโมเดลไม่ได้: {e}")
    st.stop()

# -------------------------------------------------------------
# 3. จัดการข้อมูลและแชท
# -------------------------------------------------------------
st.title("🐢 น้องนนทรี (AI Assistant)")

# โหลดข้อมูลความรู้ (ต้องมีไฟล์ ku_data.txt อยู่ในโฟลเดอร์เดียวกับ app.py)
if os.path.exists("ku_data.txt"):
    with open("ku_data.txt", "r", encoding="utf-8") as f:
        knowledge_base = f.read()
else:
    st.warning("⚠️ ไม่พบไฟล์ ku_data.txt ระบบจะตอบจากความรู้ทั่วไป")
    knowledge_base = ""

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🧑‍🎓" if message["role"] == "user" else "🦖"):
        st.markdown(message["content"])

if prompt := st.chat_input("พิมพ์คำถามที่นี่..."):
    st.chat_message("user", avatar="🧑‍🎓").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="🦖"):
        # คำสั่งคุมสติ AI
        instruction = (
            "คุณคือ 'น้องนนทรี' AI รุ่นพี่ของ มก. ศรีราชา (KU SRC) "
            "ตอบคำถามโดยอ้างอิงจากข้อมูลที่ให้มาเท่านั้น "
            "หากถามเรื่องสถานที่ ต้องส่งลิงก์แผนที่เสมอ และตอบอย่างเป็นกันเอง"
        )
        full_prompt = f"{instruction}\n\nข้อมูลอ้างอิง: {knowledge_base}\n\nคำถาม: {prompt}"
        
        try:
            response = model.generate_content(full_prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"❌ ระบบขัดข้อง: {e}")
