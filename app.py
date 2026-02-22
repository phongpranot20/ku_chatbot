import streamlit as st
import google.generativeai as genai
import os

st.set_page_config(page_title="KU Sriracha Bot", page_icon="🐢", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #FFFFFF !important; color: black !important; }
    [data-testid="stSidebar"] { background-color: #f2f9f6 !important; }
    h1, h2, h3, p, span, div { color: #00594C; }
    [data-testid="stChatMessage"] { background-color: #f0f2f6; border-radius: 10px; }
    .stMarkdown p { color: #333333 !important; }
</style>
""", unsafe_allow_html=True)

api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("❌ ไม่พบ GEMINI_API_KEY ในหน้า Settings > Secrets")
    st.stop()

genai.configure(api_key=api_key)

@st.cache_resource
def load_model():
    try:
        # ใช้โมเดล gemini-1.5-flash โดยตรงเพราะรองรับ Google Search ได้แน่นอนและเสถียรที่สุด
        return genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            tools=[{"google_search": {}}]
        )
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการโหลดโมเดล: {e}")
    return None

model = load_model()

if not model:
    st.stop()

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
        instruction = (
            "คุณคือ 'น้องนนทรี' AI รุ่นพี่ของ มก. ศรีราชา (KU SRC) "
            "1. ตอบคำถามตามข้อมูลที่ให้มาอย่างสุภาพ "
            "2. หากถามเรื่องตึกหรือแบบฟอร์ม ให้ใช้ข้อมูลจาก 'ความรู้ในไฟล์' และส่งลิงก์เสมอ "
            "3. หากถูกถามเรื่องสภาพจราจรหรือข้อมูลเรียลไทม์ ให้ใช้ Google Search เพื่อสรุปข้อมูลสภาพจราจรล่าสุดมาตอบ ห้ามส่งแค่ลิ้งค์อย่างเดียว"
        )
        full_prompt = f"{instruction}\n\nความรู้ในไฟล์: {knowledge_base}\n\nคำถาม: {prompt}"
        
        try:
            response = model.generate_content(full_prompt)
            if response.text:
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            else:
                st.write("พี่กำลังตรวจสอบข้อมูลให้นะครับ รอสักครู่")
        except Exception as e:
            st.error(f"❌ ระบบขัดข้อง: {e}")
