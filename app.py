import streamlit as st
import google.generativeai as genai
import os

# 1. ตั้งค่าหน้าเว็บแบบ Minimal
st.set_page_config(page_title="AI TEST", layout="centered")

# ลบการตกแต่งสีและ CSS เดิมออกทั้งหมด ให้เหลือแค่พื้นหลังขาวมาตรฐาน
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# 2. ระบบดึง API Key และโมเดล (คงเดิม)
# -------------------------------------------------------------
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("❌ API Key not found")
    st.stop()

genai.configure(api_key=api_key)

@st.cache_resource
def load_model():
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                return genai.GenerativeModel(m.name)
    except Exception as e:
        st.error(f"Error: {e}")
    return None

model = load_model()

# -------------------------------------------------------------
# 3. ส่วนแสดงผล UI (ปรับให้คลีนที่สุด)
# -------------------------------------------------------------
st.title("AI TEST")

# โหลดข้อมูล Knowledge Base (คงเดิม)
if os.path.exists("ku_data.txt"):
    with open("ku_data.txt", "r", encoding="utf-8") as f:
        knowledge_base = f.read()
else:
    knowledge_base = ""

# จัดการ Session State สำหรับข้อความแชท
if "messages" not in st.session_state:
    st.session_state.messages = []

# แสดงข้อความแชท (เอา Avatar/Icon ออก)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ส่วนรับข้อมูล Input
if prompt := st.chat_input("พิมพ์ข้อความ..."):
    # แสดงข้อความฝั่ง User
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # ส่วนประมวลผลของ AI
    with st.chat_message("assistant"):
        instruction = "ตอบคำถามตามข้อมูลที่ให้มาอย่างสุภาพ"
        full_prompt = f"{instruction}\n\nข้อมูล: {knowledge_base}\n\nคำถาม: {prompt}"
        
        try:
            response = model.generate_content(full_prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Error: {e}")
