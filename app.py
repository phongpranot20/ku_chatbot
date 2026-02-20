import streamlit as st
import google.generativeai as genai
import os

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="KU Sriracha Bot", page_icon="🐢", layout="wide")

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

# ใช้ชื่อโมเดลตัวนี้ครับ ชัวร์ที่สุดสำหรับตอนนี้
try:
    model = genai.GenerativeModel('gemini-1.5-flash') 
except Exception as e:
    st.error(f"เชื่อมต่อโมเดลไม่ได้: {e}")
    st.stop()

# -------------------------------------------------------------
# 3. จัดการข้อมูลและแชท
# -------------------------------------------------------------
st.title("🐢 น้องนนทรี (AI Assistant)")

if os.path.exists("ku_data.txt"):
    with open("ku_data.txt", "r", encoding="utf-8") as f:
        knowledge_base = f.read()
else:
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
            "ตอบคำถามตามข้อมูลที่ให้มาเท่านั้น หากถามเรื่องตึก ต้องส่งลิ้งค์แผนที่เสมอ"
        )
        full_prompt = f"{instruction}\n\nข้อมูล: {knowledge_base}\n\nคำถาม: {prompt}"
        
        try:
            response = model.generate_content(full_prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            # ถ้าพังอีก ให้โชว์ Error แบบละเอียดเพื่อแก้จุดสุดท้าย
            st.error(f"❌ ระบบขัดข้อง: {e}")
