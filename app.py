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
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                # เพิ่มเครื่องมือ google_search เข้าไปในโมเดลเดิมของคุณ
                return genai.GenerativeModel(
                    model_name=m.name,
                    tools=[{"google_search": {}}]
                )
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการดึงรายชื่อโมเดล: {e}")
    return None

model = load_model()

if not model:
    st.error("❌ ไม่พบโมเดลที่ใช้งานได้")
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
            "คุณคือ 'น้องนนทรี' AI รุ่นพี่ของ มก. [cite_start]ศรีราชา (KU SRC) [cite: 2] "
            "1. [cite_start]ตอบคำถามตามข้อมูลที่ให้มาอย่างสุภาพ หากถามเรื่องตึก ต้องส่งลิ้งค์แผนที่เสมอ [cite: 2] "
            "2. หากนิสิตถามเรื่องรถติด สภาพจราจร หรือข้อมูลปัจจุบัน ให้ใช้เครื่องมือ Google Search ค้นหาและสรุปคำตอบให้ชัดเจน"
        )
        full_prompt = f"{instruction}\n\nข้อมูลอ้างอิง: {knowledge_base}\n\nคำถาม: {prompt}"
        
        try:
            response = model.generate_content(full_prompt)
            if response.text:
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            else:
                st.warning("โมเดลไม่ได้ส่งข้อความกลับมา ลองถามใหม่อีกครั้งครับ")
        except Exception as e:
            st.error(f"❌ ระบบขัดข้อง: {e}")
