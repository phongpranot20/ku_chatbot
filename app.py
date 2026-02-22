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
# 2. ระบบดึง API Key และเลือกโมเดล (ปรับปรุงเพื่อรองรับ Google Search)
# -------------------------------------------------------------
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("❌ ไม่พบ GEMINI_API_KEY ในหน้า Settings > Secrets")
    st.stop()

genai.configure(api_key=api_key)

@st.cache_resource
def load_model():
    try:
        # ใช้โครงสร้าง Tool ที่ปลอดภัยที่สุดสำหรับรุ่นปัจจุบัน
        # เพื่อป้องกัน Error 400 และ Unknown field
        search_tool = {"google_search_retrieval": {}}
        
        # วนลูปหาโมเดลที่รองรับเหมือนโค้ดเดิมของคุณ
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                # เลือกโมเดลตัวแรกที่เจอและผูก Tool เข้าไป
                return genai.GenerativeModel(model_name=m.name, tools=[search_tool])
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการดึงรายชื่อโมเดล: {e}")
    return None

model = load_model()

if not model:
    st.error("❌ ไม่พบโมเดลที่ใช้งานได้ในบัญชีนี้ กรุณาตรวจสอบ API Key อีกครั้ง")
    st.stop()

# -------------------------------------------------------------
# 3. จัดการข้อมูลและแชท
# -------------------------------------------------------------
st.title("AI TEST")

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
        # ปรับปรุง Instruction ให้กระชับและสั่งให้สรุปสภาพจราจรได้จริง
        instruction = (
            "คุณคือ 'น้องนนทรี' AI รุ่นพี่ของ มก. ศรีราชา (KU SRC) "
            "ตอบคำถามตามข้อมูลที่ให้มาอย่างสุภาพ หากถามเรื่องตึก ต้องส่งลิ้งค์แผนที่เสมอ "
            "หากถูกถามเรื่องสภาพจราจรหรือข้อมูลเรียลไทม์ ให้ใช้ Google Search เพื่อหาข้อมูลล่าสุดและสรุปคำตอบให้ผู้ใช้"
        )
        full_prompt = f"{instruction}\n\nข้อมูล: {knowledge_base}\n\nคำถาม: {prompt}"
        
        try:
            # เรียกใช้โมเดลตามโครงสร้างเดิม
            response = model.generate_content(full_prompt)
            
            # ตรวจสอบการตอบกลับเพื่อป้องกัน Error กรณีไม่มี Text
            if response.text:
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            else:
                st.warning("พี่กำลังหาข้อมูลอยู่ครับ รบกวนถามอีกครั้งนะ")
        except Exception as e:
            st.error(f"❌ ระบบขัดข้อง: {e}")
